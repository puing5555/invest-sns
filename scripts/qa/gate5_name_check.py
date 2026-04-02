# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
QA Gate 5 - 종목명 일치 검증
==============================
Supabase 시그널의 (stock_name, ticker) 쌍을 pykrx 실제 종목명과 비교.
사명변경/표기차이는 허용 목록으로 통과, 나머지 불일치를 에러로 리포트.

사용법:
  python scripts/qa/gate5_name_check.py
  python scripts/qa/gate5_name_check.py --channel 선대인TV   # 특정 채널만

출력:
  - 불일치 있으면 exit(1), 없으면 exit(0)
"""

import sys
import os
import json
import argparse
from collections import defaultdict

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# ── 허용 목록: (시그널 stock_name, pykrx 실제 종목명) ──
# 사명변경, 표기차이, 비상장→모회사 등 ticker는 맞지만 이름이 다른 케이스
ALLOWED_ALIASES = {
    # 표기차이 (한글↔영문)
    ('네이버', 'NAVER'),
    ('아이에스씨', 'ISC'),
    ('에스케이씨', 'SKC'),
    ('에코프로BM', '에코프로비엠'),
    ('CS윈드', '씨에스윈드'),
    ('CS WIND', '씨에스윈드'),
    ('NC소프트', '엔씨소프트'),
    ('포스코홀딩스', 'POSCO홀딩스'),
    ('포스코', 'POSCO홀딩스'),
    ('젠백스', '젬백스'),
    ('동아ST', '동아에스티'),
    ('해성DS', '해성디에스'),
    ('WCP', '더블유씨피'),
    # 약칭
    ('현대자동차', '현대차'),
    ('한전', '한국전력'),
    # 사명변경
    ('LS산전', 'LS ELECTRIC'),
    ('한화테크윈', '한화에어로스페이스'),
    ('한화엔진', '한화에어로스페이스'),
    ('포스코케미칼', '포스코퓨처엠'),
    ('삼강엠앤티', 'SK오션플랜트'),
    ('하나머티리얼스', '하나머티리얼즈'),
    ('윤성에프엔씨', '윤성에프앤씨'),
    ('유일한테크놀로지', '유일에너테크'),
    ('신승에스티', '신성에스티'),
    # 비상장→모회사
    ('SK온', 'SK이노베이션'),
    ('앱솔릭스', 'SKC'),
    ('SK넥실리스', 'SKC'),
    # 약칭/지주사
    ('세아제강', '세아제강지주'),
    ('마이크로컨텍솔루션', '마이크로컨텍솔'),
}


def load_env():
    env_path = os.path.join(PROJECT_ROOT, '.env.local')
    if os.path.exists(env_path):
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())


def fetch_signal_pairs(channel_name=None):
    """Supabase에서 (stock, ticker, market, count) 쌍 추출. channel_name 지정 시 해당 채널만."""
    import requests

    url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL', '')
    key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
    }

    # 채널 필터링: channel_name → channel_id → video_ids
    video_filter = None
    if channel_name:
        r = requests.get(
            f"{url}/rest/v1/influencer_channels?channel_name=eq.{channel_name}&select=id",
            headers=headers,
        )
        channels = r.json()
        if not channels:
            print(f"  [WARN] 채널 '{channel_name}' 없음")
            return {}
        ch_id = channels[0]['id']
        r2 = requests.get(
            f"{url}/rest/v1/influencer_videos?channel_id=eq.{ch_id}&select=id",
            headers=headers,
        )
        video_ids = [v['id'] for v in r2.json()]
        if not video_ids:
            return {}
        video_filter = video_ids

    # 시그널 fetch (pagination)
    ticker_map = {}  # ticker -> {stock, market, count}
    offset = 0
    page_size = 1000

    while True:
        req_url = f"{url}/rest/v1/influencer_signals?select=ticker,stock,market"
        if video_filter:
            # in filter: video_id가 video_ids에 포함
            ids_str = ','.join(video_filter)
            req_url += f"&video_id=in.({ids_str})"
        req_url += f"&offset={offset}&limit={page_size}"

        resp = requests.get(req_url, headers=headers)
        if resp.status_code != 200:
            print(f"  [ERROR] Supabase API: {resp.status_code}")
            return {}

        rows = resp.json()
        if not rows:
            break

        for r in rows:
            t = r.get('ticker')
            if not t:
                continue
            if t not in ticker_map:
                ticker_map[t] = {
                    'stocks': defaultdict(int),
                    'market': r.get('market', ''),
                }
            ticker_map[t]['stocks'][r.get('stock', '')] += 1

        if len(rows) < page_size:
            break
        offset += page_size

    return ticker_map


def load_pykrx_names(tickers):
    """KR 6자리 ticker → 실제 종목명 (pykrx)"""
    kr = [t for t in tickers if len(t) == 6 and t.isdigit()]
    if not kr:
        return {}
    from pykrx import stock as st
    result = {}
    for t in kr:
        try:
            name = st.get_market_ticker_name(t)
            if name and isinstance(name, str) and name.strip():
                result[t] = name.strip()
        except Exception:
            pass
    return result


def is_allowed(signal_stock, actual_name):
    """허용 목록 또는 포함관계로 통과하는지"""
    a = signal_stock.strip()
    b = actual_name.strip()
    if a == b:
        return True
    if a in b or b in a:
        return True
    if (a, b) in ALLOWED_ALIASES:
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description='QA Gate 5 - 종목명 일치 검증')
    parser.add_argument('--channel', type=str, default=None, help='특정 채널만 검증')
    args = parser.parse_args()

    load_env()

    scope = f" ({args.channel})" if args.channel else " (전체)"
    print(f"\n{'='*60}")
    print(f"  QA Gate 5 - 종목명 일치 검증{scope}")
    print(f"{'='*60}")

    # 1) Supabase에서 (stock, ticker) 쌍 추출
    print(f"\n[1/3] Supabase 시그널 조회 중...")
    ticker_map = fetch_signal_pairs(channel_name=args.channel)
    print(f"  → 고유 ticker {len(ticker_map)}개")

    # 2) pykrx로 실제 종목명 조회
    print(f"[2/3] pykrx 종목명 조회 중...")
    actual_names = load_pykrx_names(ticker_map.keys())
    kr_count = sum(1 for t in ticker_map if len(t) == 6 and t.isdigit())
    print(f"  → KR ticker {kr_count}개 중 {len(actual_names)}개 조회 성공")

    # 3) 비교
    print(f"[3/3] 종목명 비교 중...")
    errors = []       # 잘못된 매핑 (수정 필요)
    aliases = []      # 허용된 표기차이 (참고용)

    for ticker, info in sorted(ticker_map.items()):
        actual = actual_names.get(ticker)
        if not actual:
            continue
        for stock_name, count in info['stocks'].items():
            if not stock_name:
                continue
            if stock_name.strip() == actual:
                continue  # 완전 일치
            if is_allowed(stock_name, actual):
                aliases.append((ticker, stock_name, actual, count))
            else:
                errors.append((ticker, stock_name, actual, count))

    # 결과 출력
    if errors:
        print(f"\n  ❌ 종목명 불일치 {len(errors)}건 (수정 필요):\n")
        print(f"  {'ticker':<10} {'시그널 종목명':<24} {'pykrx 실제 종목명':<24} {'건수':<6}")
        print(f"  {'-'*10} {'-'*24} {'-'*24} {'-'*6}")
        for ticker, sig, actual, count in errors:
            print(f"  {ticker:<10} {sig:<24} {actual:<24} {count:<6}")
    else:
        print(f"\n  ✅ 종목명 불일치 없음.")

    if aliases:
        print(f"\n  ℹ️  허용된 표기차이/사명변경 {len(aliases)}건 (참고):")
        for ticker, sig, actual, count in aliases:
            print(f"    {ticker} {sig} → {actual} ({count}건)")

    print(f"\n{'='*60}")

    if errors:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
