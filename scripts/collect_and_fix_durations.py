# -*- coding: utf-8 -*-
"""
Step 1+2: YouTube duration 수집 + timestamp 초과 시그널 NULL 처리
"""
import os
import sys
import json
import re
import time
import urllib.request
import urllib.error
from collections import defaultdict

# 로그 파일 (UTF-8 직접 쓰기)
_LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'tmp')
os.makedirs(_LOG_DIR, exist_ok=True)
_LOG_FILE = open(os.path.join(_LOG_DIR, 'duration_collection.log'), 'w', encoding='utf-8')


def log(msg):
    _LOG_FILE.write(str(msg) + '\n')
    _LOG_FILE.flush()


# .env.local 로드
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env.local')
    if os.path.exists(env_path):
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())


load_env()

SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')

HEADERS_YT = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
}

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal',
}


# ──────────────────────────────────────────
# Supabase helpers
# ──────────────────────────────────────────

def sb_get(path, params=''):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    if params:
        url += f"?{params}"
    req = urllib.request.Request(url, headers=HEADERS_SB)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def sb_patch(path, params, body):
    url = f"{SUPABASE_URL}/rest/v1/{path}?{params}"
    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='PATCH', headers=HEADERS_SB)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return True, r.status
    except urllib.error.HTTPError as e:
        return False, e.code


# ──────────────────────────────────────────
# YouTube duration
# ──────────────────────────────────────────

def get_yt_duration(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        req = urllib.request.Request(url, headers=HEADERS_YT)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
        m = re.search(r'"approxDurationMs":"(\d+)"', html)
        if m:
            return int(m.group(1)) // 1000
        m = re.search(r'"lengthSeconds":"(\d+)"', html)
        if m:
            return int(m.group(1))
        return None
    except Exception:
        return None


# ──────────────────────────────────────────
# Timestamp helper
# ──────────────────────────────────────────

def ts_to_secs(ts):
    if not ts or str(ts).strip() in ('', 'N/A', 'null', 'None'):
        return None
    try:
        parts = list(map(int, str(ts).strip().split(':')))
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        else:
            return parts[0]
    except Exception:
        return None


# ──────────────────────────────────────────
# Step 1: duration 수집
# ──────────────────────────────────────────

def step1_collect_durations():
    log("=" * 60)
    log("Step 1: YouTube duration 수집")
    log("=" * 60)

    log("[INFO] influencer_videos 조회 중...")
    videos = sb_get('influencer_videos',
                    'select=id,video_id,channel_id,duration_seconds&limit=3000')
    log(f"  총 {len(videos)}개 영상 로드")

    # duration_seconds가 NULL 또는 0인 것만
    targets = [v for v in videos if not v.get('duration_seconds')]
    already_done = len(videos) - len(targets)
    log(f"  수집 대상: {len(targets)}개 (이미 있음: {already_done}개)")

    results = {}
    success = 0
    fail = 0
    skip = 0

    for i, video in enumerate(targets):
        try:
            vid_id = video.get('video_id')
            uuid = video.get('id')

            if not vid_id:
                skip += 1
                continue

            dur = get_yt_duration(vid_id)
            time.sleep(1.5)  # 레이트리밋

            if dur is None:
                fail += 1
                if fail <= 10 or fail % 50 == 0:
                    log(f"  [SKIP] [{i+1}/{len(targets)}] {vid_id} -- duration 없음")
            else:
                # DB UPDATE
                ok, status = sb_patch('influencer_videos', f'id=eq.{uuid}',
                                      {'duration_seconds': dur})
                if ok:
                    results[vid_id] = dur
                    success += 1
                else:
                    log(f"  [WARN] PATCH 실패 {vid_id}: status={status}")
                    fail += 1

            if (i + 1) % 100 == 0:
                log(f"  -- 진행: {i+1}/{len(targets)} | 성공:{success} 실패:{fail} 스킵:{skip}")
        except Exception as e:
            log(f"  [ERR] [{i+1}] 예외: {e}")
            fail += 1
            continue

    log(f"\n[DONE] Step 1 완료: 성공={success}, 실패={fail}, 스킵={skip}")

    # 기존 duration 데이터도 병합 (NULL 아닌 것)
    for v in videos:
        if v.get('duration_seconds') and v.get('video_id'):
            results[v['video_id']] = v['duration_seconds']

    # 결과 저장
    out_path = os.path.join(_LOG_DIR, 'duration_collection_result.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    log(f"  [SAVE] 결과 저장: {out_path} ({len(results)}개)")

    return results, {'success': success, 'fail': fail, 'skip': skip}


# ──────────────────────────────────────────
# Step 2: timestamp > duration 시그널 NULL 처리
# ──────────────────────────────────────────

def step2_fix_overflow_signals(video_durations):
    log("\n" + "=" * 60)
    log("Step 2: timestamp 초과 시그널 NULL 처리")
    log("=" * 60)

    if not video_durations:
        log("  [WARN] duration 데이터 없음 -- Step 2 스킵")
        return {'overflow_count': 0, 'by_channel': {}}

    # influencer_signals 로드 (pagination)
    log("[INFO] influencer_signals 조회 중...")
    all_signals = []
    limit = 1000
    offset = 0
    while True:
        chunk = sb_get('influencer_signals',
                       f'select=id,video_id,timestamp,channel_id,stock&limit={limit}&offset={offset}')
        if not chunk:
            break
        all_signals.extend(chunk)
        if len(chunk) < limit:
            break
        offset += limit
        log(f"  로드: {len(all_signals)}개...")

    log(f"  총 {len(all_signals)}개 시그널 로드")

    # 초과 시그널 찾기
    overflow = []
    for s in all_signals:
        ts = s.get('timestamp')
        vid_id = s.get('video_id')
        ts_secs = ts_to_secs(ts)
        dur = video_durations.get(vid_id)
        if ts_secs and dur and ts_secs > dur:
            overflow.append(s)

    log(f"\n  초과 시그널: {len(overflow)}건")

    if not overflow:
        log("  [OK] 초과 시그널 없음 -- 완료")
        return {'overflow_count': 0, 'by_channel': {}}

    # 채널별 분포
    by_channel = defaultdict(list)
    for s in overflow:
        ch = s.get('channel_id', 'unknown')
        by_channel[ch].append(s)

    log("\n  채널별 분포:")
    for ch, sigs in sorted(by_channel.items(), key=lambda x: -len(x[1])):
        log(f"    {ch}: {len(sigs)}건")

    # 샘플 (수정 전)
    log("\n  수정 전 샘플 (최대 5건):")
    for s in overflow[:5]:
        vid = s.get('video_id', '')
        dur = video_durations.get(vid, '?')
        log(f"    {s.get('stock')} | ts={s.get('timestamp')} | dur={dur}s | ch={s.get('channel_id')}")

    # NULL 처리
    log(f"\n  [FIX] {len(overflow)}건 timestamp NULL 처리 중...")
    null_ok = 0
    null_fail = 0
    for s in overflow:
        ok, status = sb_patch('influencer_signals', f'id=eq.{s["id"]}',
                              {'timestamp': None})
        if ok:
            null_ok += 1
        else:
            null_fail += 1
            if null_fail <= 5:
                log(f"    [WARN] PATCH 실패: {s['id']} status={status}")

    log(f"\n  [DONE] NULL 처리 완료: 성공={null_ok}, 실패={null_fail}")

    return {
        'overflow_count': len(overflow),
        'null_ok': null_ok,
        'null_fail': null_fail,
        'by_channel': {ch: len(v) for ch, v in by_channel.items()}
    }


# ──────────────────────────────────────────
# Main
# ──────────────────────────────────────────

if __name__ == '__main__':
    try:
        # Step 1
        video_durations, dur_stats = step1_collect_durations()

        # Step 2
        overflow_stats = step2_fix_overflow_signals(video_durations)

        log("\n" + "=" * 60)
        log("[SUMMARY] 최종 요약")
        log("=" * 60)
        log(f"  duration 수집: 성공={dur_stats['success']}, 실패={dur_stats['fail']}, 스킵={dur_stats['skip']}")
        log(f"  timestamp NULL 처리: {overflow_stats.get('overflow_count', 0)}건")
        if overflow_stats.get('by_channel'):
            for ch, cnt in overflow_stats['by_channel'].items():
                log(f"    {ch}: {cnt}건")
        log("=" * 60)
    except Exception as e:
        import traceback
        log(f"[FATAL] {e}")
        log(traceback.format_exc())
        sys.exit(1)
    finally:
        _LOG_FILE.close()
