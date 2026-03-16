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

# pipeline_config 접근 (모델 확인용)
def _get_pipeline_model():
    try:
        _scripts = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if _scripts not in sys.path:
            sys.path.insert(0, _scripts)
        from pipeline_config import PipelineConfig
        return PipelineConfig.ANTHROPIC_MODEL
    except Exception:
        return None

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
VALID_SIGNALS = {'매수', '긍정', '중립', '부정', '매도',
                 'BUY', 'POSITIVE', 'NEUTRAL', 'CONCERN', 'SELL',
                 'STRONG_BUY', 'STRONG_SELL'}

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


def check_duplicate_key_quotes(signals):
    """체크 NEW: 같은 영상에서 key_quote 80%+ 유사 시그널 중복 경고"""
    from collections import defaultdict

    def similarity(a, b):
        """두 문자열의 문자 집합 자카드 유사도 (빠른 근사치)"""
        if not a or not b:
            return 0.0
        a_chars = set(a.replace(' ', ''))
        b_chars = set(b.replace(' ', ''))
        if not a_chars or not b_chars:
            return 0.0
        inter = len(a_chars & b_chars)
        union = len(a_chars | b_chars)
        return inter / union if union else 0.0

    # 영상별로 key_quote 묶기
    vid_quotes = defaultdict(list)  # video_id → [(stock, key_quote), ...]
    for s in signals:
        vid = s.get('video_id', '')
        kq = s.get('key_quote', '') or ''
        stock = s.get('stock', '')
        if vid and kq:
            vid_quotes[vid].append((stock, kq))

    duplicates = []
    for vid, items in vid_quotes.items():
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                stock_a, quote_a = items[i]
                stock_b, quote_b = items[j]
                if stock_a == stock_b:
                    continue  # 같은 종목 중복은 체크 4에서 처리
                sim = similarity(quote_a, quote_b)
                if sim >= 0.8:
                    duplicates.append({
                        'video_id': vid,
                        'stock_a': stock_a,
                        'stock_b': stock_b,
                        'similarity': round(sim, 2),
                        'quote_a': quote_a[:60],
                        'quote_b': quote_b[:60],
                    })
    return duplicates


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


# ── 신규 체크 함수들 ────────────────────────────────────────────────────────

def check_pipeline_model():
    """
    체크 NEW-A: 파이프라인 모델이 Haiku인지 확인.
    Haiku 사용 중이면 치명적 오류 (시그널 품질 저하).
    반환: (is_ok: bool, model: str)
    """
    model = _get_pipeline_model()
    if model is None:
        return None, 'unknown'
    bad_models = ['haiku', 'claude-3-haiku', 'claude-3-haiku-20240307']
    is_bad = any(b in model.lower() for b in bad_models)
    return not is_bad, model


def check_signal_type_empty(signals):
    """
    체크 NEW-B: signal_type 빈값("") 또는 None 비율 → 1건이라도 있으면 치명적.
    반환: (empty_list: list)
    """
    empty = []
    for s in signals:
        sig = s.get('signal') or s.get('signal_type') or ''
        if not sig or not sig.strip():
            empty.append({
                'video_id': s.get('video_id', ''),
                'stock': s.get('stock', ''),
                'signal': repr(sig)
            })
    return empty


def check_invalid_signal_type(signals):
    """
    체크 NEW-B2: 유효하지 않은 signal_type (영문, 경계 등).
    반환: (invalid_list: list)
    """
    invalid = []
    for s in signals:
        sig = s.get('signal') or s.get('signal_type') or ''
        if sig and sig not in VALID_SIGNALS:
            invalid.append({
                'video_id': s.get('video_id', ''),
                'stock': s.get('stock', ''),
                'signal': sig
            })
    return invalid


def check_subtitle_has_timestamps(signals):
    """
    체크 NEW-C: 시그널에 포함된 key_quote에 타임코드 '[HH:MM:SS]' 형식이 있는지 확인.
    자막이 타임코드를 포함하면 key_quote에도 시간 정보가 섞여 있거나,
    timestamp 필드가 null이 아닌 구체적 값을 가져야 함.
    proxy 체크: timestamp null 비율 + 분포로 VTT 타임코드 포함 여부 추정.
    반환: (is_ok: bool, null_ts_ratio: float, detail: str)
    """
    if not signals:
        return True, 0.0, '시그널 없음'
    
    ts_null_count = 0
    ts_values = []
    for s in signals:
        ts = s.get('timestamp')
        if ts is None or str(ts).strip() in ('', 'null', 'None'):
            ts_null_count += 1
        else:
            ts_values.append(str(ts).strip())
    
    null_ratio = ts_null_count / len(signals)
    
    # null이 80%+ 이면 타임코드 없이 분석된 것으로 의심
    if null_ratio >= 0.8:
        return False, null_ratio, f"timestamp null {null_ratio*100:.1f}% — VTT 타임코드 미포함 의심"
    
    # 0:00 만 있고 다양한 값이 없으면 의심
    non_zero = [t for t in ts_values if not ZERO_TIMESTAMP_PATTERNS.match(t)]
    if ts_values and len(non_zero) / max(len(ts_values), 1) < 0.3:
        return False, null_ratio, f"유효 타임스탬프 {len(non_zero)}/{len(ts_values)} — VTT 타임코드 미포함 의심"
    
    return True, null_ratio, f"정상 (null {null_ratio*100:.1f}%, 유효값 {len(non_zero)}개)"

# ────────────────────────────────────────
# 메인
# ────────────────────────────────────────

def run_gate2(signals, channel, video_durations=None, videos=None, is_new_channel=False):
    """
    Gate 2 실행. 반환: (passed: bool)

    Args:
        signals: 시그널 리스트
        channel: 채널 슬러그 (channel_slug 별칭도 허용)
        video_durations: {video_id: duration_secs} (선택)
        videos: 영상 정보 리스트 [{video_id, published_at, title}, ...] (선택)
        is_new_channel: 새 채널 여부 (True면 체크1 신규종목을 경고로 완화)
    """
    print(f"\n{'='*60}")
    print(f"🔍 QA Gate 2 - 시그널 분석 검증")
    print(f"   채널: {channel} | 시그널 수: {len(signals)}개")
    print(f"{'='*60}")

    has_fatal = False

    # ── 체크 NEW-A: 파이프라인 모델 확인 (Haiku 금지) ──
    model_ok, current_model = check_pipeline_model()
    if model_ok is None:
        print(f"\nℹ️  [체크 A] 파이프라인 모델 확인 불가 (pipeline_config 로드 실패)")
    elif not model_ok:
        print(f"\n⛔ [체크 A] 파이프라인 모델 오류 — '{current_model}' 감지!")
        print(f"   Haiku 모델은 시그널 분석 품질이 Sonnet 대비 현저히 낮습니다.")
        print(f"   pipeline_config.py의 ANTHROPIC_MODEL을 claude-sonnet-4-6 으로 수정하세요.")
        save_error_pattern(channel, 'gate2', 'wrong_model',
                           f"모델 '{current_model}' 사용 — Haiku 금지")
        has_fatal = True
    else:
        print(f"\n✅ [체크 A] 파이프라인 모델 OK: '{current_model}'")

    # ── 체크 NEW-B: signal_type 빈값 ──
    empty_sigs = check_signal_type_empty(signals)
    if empty_sigs:
        print(f"\n⛔ [체크 B] signal_type 빈값/null {len(empty_sigs)}건 — DB INSERT 금지")
        for e in empty_sigs[:5]:
            print(f"   - {e['video_id']}: stock='{e['stock']}', signal={e['signal']}")
        save_error_pattern(channel, 'gate2', 'empty_signal_type',
                           f"빈값 {len(empty_sigs)}건: {[e['stock'] for e in empty_sigs[:5]]}")
        has_fatal = True
    else:
        print(f"\n✅ [체크 B] signal_type 빈값 없음")

    # ── 체크 NEW-B2: 유효하지 않은 signal_type ──
    invalid_sigs = check_invalid_signal_type(signals)
    if invalid_sigs:
        print(f"\n⛔ [체크 B2] 유효하지 않은 signal_type {len(invalid_sigs)}건")
        for inv in invalid_sigs[:5]:
            print(f"   - {inv['stock']}: '{inv['signal']}' (허용: {sorted(VALID_SIGNALS)})")
        save_error_pattern(channel, 'gate2', 'invalid_signal_type',
                           f"유효하지 않은 signal_type {len(invalid_sigs)}건: "
                           f"{list({i['signal'] for i in invalid_sigs})}")
        has_fatal = True
    else:
        print(f"\n✅ [체크 B2] signal_type 전부 유효 ({sorted(VALID_SIGNALS)})")

    # ── 체크 NEW-C: VTT 타임코드 포함 여부 ──
    ts_ok, null_ratio, ts_detail = check_subtitle_has_timestamps(signals)
    if not ts_ok:
        print(f"\n⛔ [체크 C] VTT 타임코드 미포함 의심 — {ts_detail}")
        print(f"   subtitle_extractor.py의 parse_vtt_content(include_timestamps=True) 확인 필요")
        save_error_pattern(channel, 'gate2', 'no_vtt_timestamps', ts_detail)
        has_fatal = True
    else:
        print(f"\n✅ [체크 C] VTT 타임코드 확인 OK — {ts_detail}")

    # ── 체크 1: 비종목 오추출 ──
    print(f"\n🔎 [체크 1] DB 미등록 종목 검사 중...")
    unknown, err = check_unknown_stocks(signals)
    unknown_new = [u for u in unknown if u['input_count'] >= 1]
    if len(unknown_new) >= 5 and not is_new_channel:
        # 5건 이상이면 치명적 (오추출 가능성 높음) — 단, 새 채널은 경고만
        print(f"\n⛔ [체크 1] 비종목 오추출 — DB 3회 미만 신규 종목 {len(unknown_new)}건 (5건 이상 → 중단)")
        for u in unknown_new[:10]:
            print(f"   - '{u['stock']}' (DB: {u['db_count']}회, 이번: {u['input_count']}건)")
        save_error_pattern(channel, 'gate2', 'unknown_stocks',
                           f"DB 3회 미만 종목 {len(unknown_new)}개: {[u['stock'] for u in unknown_new[:5]]}")
        has_fatal = True
    elif len(unknown_new) >= 5 and is_new_channel:
        print(f"\n⚠️  [체크 1] 새 채널 — 신규 종목 {len(unknown_new)}건 (새 채널이므로 경고만)")
        for u in unknown_new[:10]:
            print(f"   - '{u['stock']}' (DB: {u['db_count']}회, 이번: {u['input_count']}건)")
        save_error_pattern(channel, 'gate2', 'unknown_stocks_new_channel',
                           f"새 채널 신규 종목 {len(unknown_new)}개: {[u['stock'] for u in unknown_new[:5]]}")
    elif len(unknown_new) >= 1:
        print(f"⚠️  [체크 1] 신규 종목 {len(unknown_new)}건 (5건 미만 → 경고만)")
        for u in unknown_new[:5]:
            print(f"   - '{u['stock']}' (DB: {u['db_count']}회, 이번: {u['input_count']}건)")
        save_error_pattern(channel, 'gate2', 'unknown_stocks_warn',
                           f"신규 종목 {len(unknown_new)}개: {[u['stock'] for u in unknown_new[:5]]}")
    elif err:
        print(f"ℹ️  [체크 1] DB 조회 실패, 스킵: {err}")
    else:
        print(f"✅ [체크 1] 종목 검증 통과 (미등록 종목 없음)")

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

    # ── 체크 4b: key_quote 중복 (80%+ 유사도) ──
    dup_quotes = check_duplicate_key_quotes(signals)
    if dup_quotes:
        print(f"\n⚠️  [체크 4b] key_quote 중복 의심 — {len(dup_quotes)}쌍 (유사도 80%+)")
        for d in dup_quotes[:5]:
            print(f"   - '{d['stock_a']}' vs '{d['stock_b']}' (유사도 {d['similarity']:.0%})")
            print(f"     \"{d['quote_a']}\"")
        save_error_pattern(channel, 'gate2', 'duplicate_key_quote',
                           f"{len(dup_quotes)}쌍 중복 key_quote (유사도 80%+)")
    else:
        print(f"\n✅ [체크 4b] key_quote 중복 없음")

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

    # ── 체크 9/10: published_at 검증 (videos 파라미터 있을 때) ──
    if videos is not None:
        TODAY = datetime.utcnow().strftime('%Y-%m-%d')
        vid_count = len(videos)

        # 체크 9: published_at NULL
        null_pub = [v for v in videos if not v.get('published_at')]
        if null_pub:
            null_pct = len(null_pub) / max(vid_count, 1) * 100
            if len(null_pub) > vid_count * 0.5:
                print(f"\n⛔ [체크 9] published_at NULL 영상 {len(null_pub)}/{vid_count}건 ({null_pct:.1f}%) — 50% 초과 FAIL")
                save_error_pattern(channel, 'gate2', 'PUBLISHED_AT_NULL',
                                   f"published_at NULL {len(null_pub)}건 ({null_pct:.1f}%): "
                                   f"{[v.get('video_id','') for v in null_pub[:3]]}")
                has_fatal = True
            else:
                print(f"\n⚠️  [체크 9] published_at NULL {len(null_pub)}/{vid_count}건 ({null_pct:.1f}%) — 크롤링 날짜 사용 금지 (경고)")
                save_error_pattern(channel, 'gate2', 'PUBLISHED_AT_NULL_WARN',
                                   f"published_at NULL {len(null_pub)}건 ({null_pct:.1f}%): "
                                   f"{[v.get('video_id','') for v in null_pub[:3]]}")
        else:
            print(f"\n✅ [체크 9] published_at NULL 없음 ({vid_count}건 모두 날짜 있음)")

        # 체크 10: published_at = 오늘 날짜 (크롤링 날짜 오염 의심)
        today_pub = [v for v in videos if (v.get('published_at') or '')[:10] == TODAY]
        if today_pub:
            print(f"\n⛔ [체크 10] published_at이 오늘 날짜({TODAY}) {len(today_pub)}건 — 크롤링 날짜 오염 의심 FAIL")
            for v in today_pub[:3]:
                print(f"   - {v.get('video_id', '')}: {v.get('title', '')[:40]}")
            save_error_pattern(channel, 'gate2', 'PUBLISHED_AT_TODAY',
                               f"published_at 오늘날짜 {len(today_pub)}건: "
                               f"{[v.get('video_id','') for v in today_pub[:3]]}")
            has_fatal = True
        else:
            print(f"\n✅ [체크 10] published_at 오늘 날짜 오염 없음")
    else:
        print(f"\nℹ️  [체크 9/10] videos 파라미터 없음 — published_at 검증 스킵")

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
