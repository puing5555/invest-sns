# -*- coding: utf-8 -*-
"""
QA Gate 1 - 메타데이터 검증
==============================
사용법:
  # JSON 파일 입력
  python scripts/qa/gate1_metadata.py --input data/tmp/godofit_metadata.json --channel godofit

  # stdin 입력
  cat data/tmp/godofit_metadata.json | python scripts/qa/gate1_metadata.py --channel godofit

  # 총 영상 수 대비 필터 통과율 체크 포함
  python scripts/qa/gate1_metadata.py --input data/tmp/godofit_metadata.json --channel godofit --total 200

출력:
  - 콘솔: 검증 결과 리포트 (한글)
  - 성공(exit 0): stdout에 필터된 영상 목록 JSON
  - 실패(exit 1): data/qa/error_patterns.json에 에러 패턴 추가
"""

import sys
import os
import json
import re
import argparse
from datetime import datetime, date

# .env.local 로드
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env.local')
    if os.path.exists(env_path):
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env()

import urllib.request
import urllib.error

SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')

QA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'qa')
ERROR_PATTERNS_FILE = os.path.join(QA_DIR, 'error_patterns.json')

YOUTUBE_ID_PATTERN = re.compile(r'^[A-Za-z0-9_-]{11}$')
KOREAN_PATTERN = re.compile(r'[가-힣]')

# ────────────────────────────────────────
# 유틸
# ────────────────────────────────────────

def ensure_qa_dir():
    os.makedirs(QA_DIR, exist_ok=True)

def load_error_patterns():
    if os.path.exists(ERROR_PATTERNS_FILE):
        with open(ERROR_PATTERNS_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []

def save_error_pattern(channel, gate, check_name, detail):
    ensure_qa_dir()
    patterns = load_error_patterns()
    patterns.append({
        "channel": channel,
        "gate": gate,
        "check_name": check_name,
        "detail": detail,
        "timestamp": datetime.now().isoformat()
    })
    with open(ERROR_PATTERNS_FILE, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)

def supabase_get(path, params=None):
    """Supabase REST API GET 요청"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None, "Supabase 설정 없음"
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    if params:
        qs = '&'.join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{qs}"
    req = urllib.request.Request(url, headers={
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8')), None
    except Exception as e:
        return None, str(e)

# ────────────────────────────────────────
# 체크 함수
# ────────────────────────────────────────

def check_title_has_video_id(videos):
    """체크 1: video_id가 title에 그대로 들어간 영상 탐지"""
    bad = []
    for v in videos:
        vid = v.get('video_id', '')
        title = v.get('title', '')
        if YOUTUBE_ID_PATTERN.match(vid) and vid in title:
            bad.append({'video_id': vid, 'title': title})
    return bad

def check_date_concentration(videos):
    """체크 2: 50%+ 영상이 같은 날짜 → 크롤링 날짜 사용 의심"""
    if not videos:
        return None, 0
    dates = {}
    for v in videos:
        d = str(v.get('published_at', ''))[:10]
        dates[d] = dates.get(d, 0) + 1
    top_date, top_count = max(dates.items(), key=lambda x: x[1])
    ratio = top_count / len(videos)
    return top_date, ratio

def check_future_dates(videos):
    """체크 3: published_at > today"""
    today = date.today()
    bad = []
    for v in videos:
        pa = v.get('published_at', '')
        if not pa:
            continue
        try:
            pub = date.fromisoformat(str(pa)[:10])
            if pub > today:
                bad.append({'video_id': v.get('video_id'), 'published_at': pa})
        except Exception:
            pass
    return bad

def check_channel_name(videos):
    """체크 4: channel_name이 영문/핸들만이면 경고"""
    if not videos:
        return False
    channel_name = videos[0].get('channel_name', '')
    has_korean = bool(KOREAN_PATTERN.search(channel_name))
    return not has_korean, channel_name

def check_duplicates_in_db(videos):
    """체크 5: video_id가 DB에 이미 있는지 확인"""
    video_ids = [v.get('video_id') for v in videos if v.get('video_id')]
    if not video_ids:
        return []
    
    # Supabase in() 쿼리
    ids_csv = ','.join(f'"{vid}"' for vid in video_ids)
    data, err = supabase_get('influencer_videos', {
        'select': 'video_id',
        f'video_id': f'in.({",".join(video_ids)})'
    })
    
    if err:
        print(f"  ⚠️  DB 중복 체크 실패: {err}")
        return []
    
    if data:
        existing = {row['video_id'] for row in data}
        return [vid for vid in video_ids if vid in existing]
    return []

def check_filter_pass_rate(original_count, filtered_count):
    """체크 6: 필터 통과율 5% 미만"""
    if original_count == 0:
        return 0.0
    return filtered_count / original_count

# ────────────────────────────────────────
# 메인
# ────────────────────────────────────────

def run_gate1(videos, channel, total_original=None):
    """Gate 1 실행. 반환: (passed: bool, filtered_videos: list)"""
    print(f"\n{'='*60}")
    print(f"🔍 QA Gate 1 - 메타데이터 검증")
    print(f"   채널: {channel} | 영상 수: {len(videos)}개")
    print(f"{'='*60}")

    has_fatal = False

    # ── 체크 1: 제목에 video_id 포함 ──
    bad_titles = check_title_has_video_id(videos)
    if bad_titles:
        print(f"\n⛔ [체크 1] 제목 검증 실패 — video_id가 title에 포함된 영상 {len(bad_titles)}건")
        for b in bad_titles[:5]:
            print(f"   - {b['video_id']}: {b['title'][:60]}")
        if len(bad_titles) > 5:
            print(f"   ... 외 {len(bad_titles)-5}건")
        save_error_pattern(channel, 'gate1', 'title_has_video_id',
                           f"{len(bad_titles)}개 영상 제목에 video_id 포함")
        has_fatal = True
    else:
        print(f"\n✅ [체크 1] 제목 검증 통과")

    # ── 체크 2: 날짜 집중 ──
    top_date, ratio = check_date_concentration(videos)
    if ratio >= 0.5:
        print(f"\n⛔ [체크 2] 날짜 집중 감지 — {top_date}에 {ratio*100:.1f}% 집중 (크롤링 날짜 의심)")
        save_error_pattern(channel, 'gate1', 'date_concentration',
                           f"{top_date}에 {ratio*100:.1f}% 집중")
        has_fatal = True
    else:
        print(f"\n✅ [체크 2] 날짜 분포 정상 (최다: {top_date}, {ratio*100:.1f}%)")

    # ── 체크 3: 미래 날짜 ──
    future = check_future_dates(videos)
    if future:
        print(f"\n⛔ [체크 3] 미래 날짜 감지 — {len(future)}건")
        for f in future[:5]:
            print(f"   - {f['video_id']}: {f['published_at']}")
        save_error_pattern(channel, 'gate1', 'future_date',
                           f"{len(future)}개 영상의 published_at이 미래")
        has_fatal = True
    else:
        print(f"\n✅ [체크 3] 미래 날짜 없음")

    # ── 체크 4: 채널명 경고 ──
    no_korean, ch_name = check_channel_name(videos)
    if no_korean:
        print(f"\n⚠️  [체크 4] 채널명 경고 — '{ch_name}' 한글 없음 (JAY 확인 필요)")
        save_error_pattern(channel, 'gate1', 'channel_name_no_korean',
                           f"channel_name='{ch_name}'에 한글 없음")
    else:
        print(f"\n✅ [체크 4] 채널명 한글 확인 OK: '{ch_name}'")

    # ── 체크 5: DB 중복 ──
    print(f"\n🔎 [체크 5] DB 중복 체크 중...")
    dupes = check_duplicates_in_db(videos)
    if dupes:
        print(f"⚠️  [체크 5] DB 중복 {len(dupes)}건 (스킵 예정)")
        for d in dupes[:10]:
            print(f"   - {d}")
        if len(dupes) > 10:
            print(f"   ... 외 {len(dupes)-10}건")
    else:
        print(f"✅ [체크 5] 중복 없음")

    # 중복 제거
    dup_set = set(dupes)
    filtered = [v for v in videos if v.get('video_id') not in dup_set]

    # ── 체크 6: 필터 통과율 ──
    original_count = total_original if total_original else len(videos)
    pass_rate = check_filter_pass_rate(original_count, len(filtered))
    if pass_rate < 0.05 and original_count > 10:
        print(f"\n⚠️  [체크 6] 필터 통과율 {pass_rate*100:.1f}% — 5% 미만 경고!")
        save_error_pattern(channel, 'gate1', 'low_pass_rate',
                           f"통과율 {pass_rate*100:.1f}% ({len(filtered)}/{original_count})")
    else:
        print(f"\n✅ [체크 6] 필터 통과율 {pass_rate*100:.1f}% ({len(filtered)}/{original_count})")

    # ── 결과 ──
    print(f"\n{'='*60}")
    if has_fatal:
        print(f"❌ Gate 1 실패 — 치명적 오류 발생. 파이프라인 중단.")
        print(f"{'='*60}\n")
        return False, []
    else:
        print(f"✅ Gate 1 통과 — 검증 완료. 유효 영상 {len(filtered)}개")
        print(f"{'='*60}\n")
        return True, filtered


def main():
    parser = argparse.ArgumentParser(description='QA Gate 1 - 메타데이터 검증')
    parser.add_argument('--input', '-i', help='입력 JSON 파일 경로')
    parser.add_argument('--channel', '-c', required=True, help='채널 슬러그 (예: godofit)')
    parser.add_argument('--total', '-t', type=int, help='원본 영상 총 수 (통과율 계산용)')
    args = parser.parse_args()

    # 입력 읽기
    if args.input:
        with open(args.input, encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    # 배열 또는 객체{'videos': [...]} 모두 허용
    if isinstance(data, list):
        videos = data
    elif isinstance(data, dict) and 'videos' in data:
        videos = data['videos']
    else:
        print("❌ 입력 형식 오류: 배열 또는 {'videos': [...]} 형식이어야 합니다.", file=sys.stderr)
        sys.exit(1)

    passed, filtered = run_gate1(videos, args.channel, args.total)

    if passed:
        # stdout에 필터된 영상 목록 출력
        sys.stdout.write(json.dumps(filtered, ensure_ascii=False, indent=2))
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
