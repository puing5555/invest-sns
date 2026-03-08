# -*- coding: utf-8 -*-
import sys, io, os, json, re, time, urllib.request, urllib.error, traceback
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

LOG_PATH = r'C:\Users\Mario\work\invest-sns\data\tmp\duration_collection.log'
LOG_FILE = open(LOG_PATH, 'w', encoding='utf-8')

def log(msg):
    LOG_FILE.write(str(msg) + '\n')
    LOG_FILE.flush()
    print(str(msg), flush=True)

# --- env ---
def load_env():
    with open(r'C:\Users\Mario\work\invest-sns\.env.local', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env()
SUPA_URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
SUPA_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

SB_HDR = {
    'apikey': SUPA_KEY,
    'Authorization': f'Bearer {SUPA_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal',
}
YT_HDR = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
}


def sb_get(path, params=''):
    url = f"{SUPA_URL}/rest/v1/{path}"
    if params:
        url += f"?{params}"
    req = urllib.request.Request(url, headers=SB_HDR)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def sb_patch(path, params, body):
    url = f"{SUPA_URL}/rest/v1/{path}?{params}"
    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='PATCH', headers=SB_HDR)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return True, r.status
    except urllib.error.HTTPError as e:
        return False, e.code


def get_yt_duration(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        req = urllib.request.Request(url, headers=YT_HDR)
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


# ========== STEP 1: DURATION COLLECTION ==========

log("=" * 60)
log("Step 1: YouTube duration 수집")
log("=" * 60)

log("[INFO] influencer_videos 조회 중...")
videos = sb_get('influencer_videos', 'select=id,video_id,channel_id,duration_seconds&limit=3000')
log(f"  총 {len(videos)}개 영상 로드")

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
        time.sleep(1.5)

        if dur is None:
            fail += 1
            if fail <= 10 or fail % 50 == 0:
                log(f"  [SKIP] [{i+1}/{len(targets)}] {vid_id}")
        else:
            ok, status = sb_patch('influencer_videos', f'id=eq.{uuid}', {'duration_seconds': dur})
            if ok:
                results[vid_id] = dur
                success += 1
            else:
                log(f"  [WARN] PATCH 실패 {vid_id}: status={status}")
                fail += 1

        if (i + 1) % 50 == 0:
            log(f"  -- 진행: {i+1}/{len(targets)} | 성공:{success} 실패:{fail}")
    except Exception as e:
        log(f"  [ERR] [{i+1}] {e}")
        fail += 1
        continue

log(f"\n[DONE] Step 1: 성공={success}, 실패={fail}, 스킵={skip}")

# 기존 duration 데이터도 병합
for v in videos:
    if v.get('duration_seconds') and v.get('video_id'):
        results[v['video_id']] = v['duration_seconds']

# 결과 저장
result_path = r'C:\Users\Mario\work\invest-sns\data\tmp\duration_collection_result.json'
with open(result_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
log(f"  [SAVE] {result_path} ({len(results)}개)")


# ========== STEP 2: TIMESTAMP OVERFLOW NULL 처리 ==========

log("\n" + "=" * 60)
log("Step 2: timestamp 초과 시그널 NULL 처리")
log("=" * 60)

if not results:
    log("  [WARN] duration 데이터 없음 -- Step 2 스킵")
else:
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

    overflow = []
    for s in all_signals:
        ts = s.get('timestamp')
        vid_id = s.get('video_id')
        ts_secs = ts_to_secs(ts)
        dur = results.get(vid_id)
        if ts_secs and dur and ts_secs > dur:
            overflow.append(s)

    log(f"  초과 시그널: {len(overflow)}건")

    by_channel = defaultdict(int)
    for s in overflow:
        by_channel[s.get('channel_id', 'unknown')] += 1

    if overflow:
        log("  채널별 분포:")
        for ch, cnt in sorted(by_channel.items(), key=lambda x: -x[1]):
            log(f"    {ch}: {cnt}건")

        log("  수정 전 샘플 (최대 5건):")
        for s in overflow[:5]:
            vid = s.get('video_id', '')
            dur = results.get(vid, '?')
            log(f"    {s.get('stock')} | ts={s.get('timestamp')} | dur={dur}s | ch={s.get('channel_id')}")

        log(f"  [FIX] {len(overflow)}건 timestamp NULL 처리 중...")
        null_ok = 0
        null_fail = 0
        for s in overflow:
            ok, status = sb_patch('influencer_signals', f'id=eq.{s["id"]}', {'timestamp': None})
            if ok:
                null_ok += 1
            else:
                null_fail += 1
                if null_fail <= 5:
                    log(f"    [WARN] PATCH 실패: {s['id']} status={status}")

        log(f"  [DONE] NULL 처리: 성공={null_ok}, 실패={null_fail}")
    else:
        log("  [OK] 초과 시그널 없음")

log("\n" + "=" * 60)
log("[SUMMARY] 최종 요약")
log("=" * 60)
log(f"  duration 수집: 성공={success}, 실패={fail}, 스킵={skip}")
log(f"  timestamp NULL 처리: {len(overflow) if results else 0}건")
if results and by_channel:
    for ch, cnt in by_channel.items():
        log(f"    {ch}: {cnt}건")
log("=" * 60)

LOG_FILE.close()
