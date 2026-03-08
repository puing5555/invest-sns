# -*- coding: utf-8 -*-
"""
QA Gate 2 - 시그널 분석 검증
==============================
사용법:
  # JSON 파일 입력
  python scripts/qa/gate2_signals.py --input data/tmp/godofit_signals.json --channel godofit

  # stdin 입력
  cat data/tmp/godofit_signals.json | python scripts/qa/gate2_signals.py --channel godofit

입력 JSON 형식:
  [
    {
      "stock": "삼성전자",
      "signal": "매수",
      "key_quote": "...",
      "timestamp": "5:23",
      "video_id": "abc123"
    },
    ...
  ]

출력:
  - 콘솔: 검증 결과 리포트 (한글)
  - 성공(exit 0): stdout에 원본 시그널 목록 JSON
  - 실패(exit 1): data/qa/error_patterns.json에 에러 패턴 추가
"""

import sys
import os
import json
import re
import argparse
from datetime import datetime
from collections import defaultdict

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

SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')

QA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'qa')
ERROR_PATTERNS_FILE = os.path.join(QA_DIR, 'error_patterns.json')

# 타임스탬프 0:00 패턴
ZERO_TIMESTAMP_PATTERNS = re.compile(r'^(0:00|00:00|0:00:00|00:00:00)$')

# 유효 시그널 값
VALID_SIGNALS = {'매수', '긍정', '중립', '부정', '매도'}

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

def check_unknown_stocks(signals):
    """체크 1: DB에서 3회 미만 등장한 종목이 3건+ → 비종목 오추출 의심"""
    stocks = [s.get('stock', '') for s in signals if s.get('stock')]
    unique_stocks = list(set(stocks))

    if not unique_stocks or not SUPABASE_URL:
        return [], "DB 연결 없어 스킵"

    # DB에서 종목별 등장 횟수 조회
    unknown = []
    for stock in unique_stocks:
        encoded = urllib.request.quote(stock)
        data, err = supabase_get('influencer_signals', {
            'select': 'stock',
            'stock': f'eq.{encoded}'
        })
        if err:
            continue
        if data is not None and len(data) < 3:
            count_in_input = stocks.count(stock)
            unknown.append({'stock': stock, 'db_count': len(data), 'input_count': count_in_input})

    return unknown, None

def check_signal_distribution(signals):
    """체크 2: 매수 80%+ 또는 부정 0건 → 편향 경고"""
    if not signals:
        return {}
    dist = defaultdict(int)
    for s in signals:
        sig = s.get('signal', '')
        dist[sig] += 1

    total = len(signals)
    buy_ratio = dist.get('매수', 0) / total
    negative_count = dist.get('부정', 0) + dist.get('매도', 0)

    return {
        'distribution': dict(dist),
        'buy_ratio': buy_ratio,
        'negative_count': negative_count,
        'total': total
    }

def check_zero_timestamps(signals):
    """체크 3: 타임스탬프 0:00 비율 20%+ → 치명적"""
    if not signals:
        return 0.0, []
    zero_list = []
    for s in signals:
        ts = str(s.get('timestamp', '') or '')
        if ZERO_TIMESTAMP_PATTERNS.match(ts.strip()):
            zero_list.append({'video_id': s.get('video_id'), 'stock': s.get('stock'), 'timestamp': ts})
    ratio = len(zero_list) / len(signals)
    return ratio, zero_list

def check_duplicate_stock_per_video(signals):
    """체크 4: 같은 영상에 동일 종목 중복"""
    seen = defaultdict(set)
    dupes = []
    for s in signals:
        vid = s.get('video_id', '')
        stock = s.get('stock', '')
        key = (vid, stock)
        if stock and vid:
            if stock in seen[vid]:
                dupes.append({'video_id': vid, 'stock': stock})
            else:
                seen[vid].add(stock)
    return dupes

def ts_to_secs(ts):
    """타임스탬프 문자열을 초로 변환"""
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
    except:
        return None


def check_timestamp_overflow(signals, video_durations):
    """
    Gate 2 추가 체크: timestamp > duration 경고
    video_durations: {video_id(yt): duration_secs} 딕셔너리
    """
    if not video_durations:
        return True  # 데이터 없으면 스킵
    overflow_count = 0
    for s in signals:
        ts = s.get('timestamp')
        video_id = s.get('video_id')  # YouTube video ID
        ts_secs = ts_to_secs(ts)
        dur = video_durations.get(video_id)
        if ts_secs and dur and ts_secs > dur:
            overflow_count += 1
            print(f"  ⚠️  OVERFLOW: {s.get('stock')} ts={ts}({ts_secs}s) > dur={dur}s")
    if overflow_count > 0:
        pct = overflow_count / len(signals) * 100
        print(f"  타임스탬프 초과: {overflow_count}/{len(signals)}건 ({pct:.1f}%)")
        if pct > 20:
            print(f"  ❌ 초과율 20% 초과 → Gate 2 FAIL")
            return False
        else:
            print(f"  ⚠️  경고 (20% 미만이므로 계속 진행)")
    return True


def check_null_key_quotes(signals):
    """체크 5: key_quote null 비율 10%+ → 경고"""
    if not signals:
        return 0.0
    null_count = sum(1 for s in signals if not s.get('key_quote'))
    return null_count / len(signals)

def check_signal_count_per_video(signals):
    """체크 6/7: 영상당 시그널 수"""
    if not signals:
        return 0.0, {}
    per_video = defaultdict(int)
    for s in signals:
        per_video[s.get('video_id', 'unknown')] += 1
    avg = len(signals) / max(len(per_video), 1)
    return avg, dict(per_video)

# ────────────────────────────────────────
# 메인
# ────────────────────────────────────────

def run_gate2(signals, channel, video_durations=None):
    """Gate 2 실행. 반환: (passed: bool)"""
    print(f"\n{'='*60}")
    print(f"🔍 QA Gate 2 - 시그널 분석 검증")
    print(f"   채널: {channel} | 시그널 수: {len(signals)}개")
    print(f"{'='*60}")

    has_fatal = False

    # ── 체크 1: 비종목 오추출 ──
    print(f"\n🔎 [체크 1] DB 미등록 종목 검사 중...")
    unknown, err = check_unknown_stocks(signals)
    unknown_new = [u for u in unknown if u['input_count'] >= 1]
    if len(unknown_new) >= 3:
        print(f"⚠️  [체크 1] 비종목 오추출 의심 — DB 3회 미만 종목 {len(unknown_new)}건")
        for u in unknown_new[:10]:
            print(f"   - '{u['stock']}' (DB: {u['db_count']}회, 이번: {u['input_count']}건)")
        save_error_pattern(channel, 'gate2', 'unknown_stocks',
                           f"DB 3회 미만 종목 {len(unknown_new)}개: {[u['stock'] for u in unknown_new[:5]]}")
    elif err:
        print(f"ℹ️  [체크 1] DB 조회 실패, 스킵: {err}")
    else:
        print(f"✅ [체크 1] 종목 검증 통과 (미등록 종목 {len(unknown_new)}건)")

    # ── 체크 2: 신호 분포 ──
    dist_info = check_signal_distribution(signals)
    buy_ratio = dist_info.get('buy_ratio', 0)
    neg_count = dist_info.get('negative_count', 0)
    dist = dist_info.get('distribution', {})

    dist_str = ' | '.join(f"{k}:{v}" for k, v in sorted(dist.items()))
    print(f"\n📊 [체크 2] 신호 분포: {dist_str}")

    if buy_ratio >= 0.8:
        print(f"⚠️  [체크 2] 매수 편향 — 매수 비율 {buy_ratio*100:.1f}% (80% 이상)")
        save_error_pattern(channel, 'gate2', 'signal_bias_buy',
                           f"매수 {buy_ratio*100:.1f}%")
    elif neg_count == 0 and len(signals) > 5:
        print(f"⚠️  [체크 2] 부정/매도 신호 0건 — 편향 의심")
        save_error_pattern(channel, 'gate2', 'signal_bias_no_negative',
                           "부정+매도 신호 0건")
    else:
        print(f"✅ [체크 2] 신호 분포 정상")

    # ── 체크 3: 타임스탬프 0:00 ──
    zero_ratio, zero_list = check_zero_timestamps(signals)
    if zero_ratio >= 0.2:
        print(f"\n⛔ [체크 3] 타임스탬프 0:00 비율 {zero_ratio*100:.1f}% — 20% 초과 (중단)")
        for z in zero_list[:5]:
            print(f"   - {z['video_id']}: {z['stock']}")
        save_error_pattern(channel, 'gate2', 'zero_timestamp',
                           f"0:00 타임스탬프 {zero_ratio*100:.1f}% ({len(zero_list)}/{len(signals)})")
        has_fatal = True
    else:
        print(f"\n✅ [체크 3] 타임스탬프 0:00 비율 {zero_ratio*100:.1f}% (정상)")

    # ── 체크 4: 같은 영상 동일 종목 중복 ──
    dupes = check_duplicate_stock_per_video(signals)
    if dupes:
        unique_dupes = list({(d['video_id'], d['stock']) for d in dupes})
        print(f"\n⚠️  [체크 4] 동일 영상 종목 중복 {len(unique_dupes)}건")
        for d in unique_dupes[:10]:
            print(f"   - {d[0]}: {d[1]}")
        save_error_pattern(channel, 'gate2', 'duplicate_stock_per_video',
                           f"{len(unique_dupes)}건 중복")
    else:
        print(f"\n✅ [체크 4] 동일 영상 종목 중복 없음")

    # ── 체크 5: key_quote null 비율 ──
    null_ratio = check_null_key_quotes(signals)
    if null_ratio >= 0.1:
        print(f"\n⚠️  [체크 5] key_quote null 비율 {null_ratio*100:.1f}% — 10% 이상")
        save_error_pattern(channel, 'gate2', 'null_key_quote',
                           f"key_quote null {null_ratio*100:.1f}%")
    else:
        print(f"\n✅ [체크 5] key_quote null 비율 {null_ratio*100:.1f}% (정상)")

    # ── 체크 6/7: 시그널 수 ──
    avg, per_video = check_signal_count_per_video(signals)
    video_count = len(per_video)
    print(f"\n📈 [체크 6/7] 영상 {video_count}개 | 시그널 평균 {avg:.2f}개/영상")

    if avg < 0.5 and video_count > 0:
        print(f"⚠️  [체크 6] 시그널 수 너무 적음 — 평균 {avg:.2f}/영상 (0.5 미만)")
        save_error_pattern(channel, 'gate2', 'too_few_signals',
                           f"평균 {avg:.2f}/영상")
    elif avg >= 10:
        print(f"⚠️  [체크 7] 시그널 수 너무 많음 — 평균 {avg:.2f}/영상 (10 이상)")
        save_error_pattern(channel, 'gate2', 'too_many_signals',
                           f"평균 {avg:.2f}/영상")
    else:
        print(f"✅ [체크 6/7] 시그널 수 정상 범위")

    # ── 체크 8: timestamp > duration (옵션) ──
    if video_durations is not None:
        print(f"\n🕐 [체크 8] 타임스탬프 초과 검사 중...")
        overflow_ok = check_timestamp_overflow(signals, video_durations)
        if not overflow_ok:
            save_error_pattern(channel, 'gate2', 'timestamp_overflow',
                               f"타임스탬프 초과율 20% 초과")
            has_fatal = True
        else:
            print(f"✅ [체크 8] 타임스탬프 초과 체크 통과")
    else:
        print(f"\nℹ️  [체크 8] video_durations 없음 — 타임스탬프 초과 체크 스킵")

    # ── 결과 ──
    print(f"\n{'='*60}")
    if has_fatal:
        print(f"❌ Gate 2 실패 — 치명적 오류 발생. 파이프라인 중단.")
        print(f"{'='*60}\n")
        return False
    else:
        print(f"✅ Gate 2 통과 — 시그널 검증 완료")
        print(f"{'='*60}\n")
        return True


def main():
    parser = argparse.ArgumentParser(description='QA Gate 2 - 시그널 분석 검증')
    parser.add_argument('--input', '-i', help='입력 JSON 파일 경로')
    parser.add_argument('--channel', '-c', required=True, help='채널 슬러그 (예: godofit)')
    args = parser.parse_args()

    # 입력 읽기
    if args.input:
        with open(args.input, encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    # 배열 또는 {'signals': [...]} 허용
    if isinstance(data, list):
        signals = data
    elif isinstance(data, dict) and 'signals' in data:
        signals = data['signals']
    else:
        print("❌ 입력 형식 오류: 배열 또는 {'signals': [...]} 형식이어야 합니다.", file=sys.stderr)
        sys.exit(1)

    passed = run_gate2(signals, args.channel)

    if passed:
        sys.stdout.write(json.dumps(signals, ensure_ascii=False, indent=2))
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
