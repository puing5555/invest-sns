# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
QA Gate 4 - Ticker 유효성 검증
===============================
Supabase influencer_signals 전체 ticker를
stock_tickers.json / stockPrices.json과 대조하여 누락 리포트.

사용법:
  python scripts/qa/gate4_ticker_check.py
  python scripts/qa/gate4_ticker_check.py --fix   # 누락 ticker 자동 추가 (tickers.json만)

출력:
  - 콘솔: 검증 결과 테이블
  - 누락 있으면 exit(1), 없으면 exit(0)
"""

import sys
import os
import json
import argparse
from collections import defaultdict

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

TICKERS_PATH = os.path.join(PROJECT_ROOT, 'data', 'stock_tickers.json')
PRICES_PATH = os.path.join(PROJECT_ROOT, 'data', 'stockPrices.json')
PRICES_PUBLIC_PATH = os.path.join(PROJECT_ROOT, 'public', 'stockPrices.json')


def load_env():
    env_path = os.path.join(PROJECT_ROOT, '.env.local')
    if os.path.exists(env_path):
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())


def fetch_all_signal_tickers():
    """Supabase에서 모든 시그널의 고유 ticker + stock 이름 조회"""
    try:
        import requests
    except ImportError:
        print("[ERROR] requests 패키지 필요: pip install requests")
        sys.exit(1)

    url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL', '')
    key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
    if not url or not key:
        print("[ERROR] Supabase 환경변수 없음 (.env.local 확인)")
        sys.exit(1)

    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
    }

    # 고유 ticker + stock + market 조합 가져오기 (페이지네이션)
    ticker_map = {}  # ticker -> {stock, market, count}
    offset = 0
    page_size = 1000

    while True:
        resp = requests.get(
            f"{url}/rest/v1/influencer_signals?select=ticker,stock,market&offset={offset}&limit={page_size}",
            headers=headers,
        )
        if resp.status_code != 200:
            print(f"[ERROR] Supabase API 오류: {resp.status_code} {resp.text}")
            sys.exit(1)

        rows = resp.json()
        if not rows:
            break

        for r in rows:
            t = r.get('ticker')
            if not t:
                continue
            if t not in ticker_map:
                ticker_map[t] = {
                    'stock': r.get('stock', ''),
                    'market': r.get('market', ''),
                    'count': 0,
                }
            ticker_map[t]['count'] += 1

        if len(rows) < page_size:
            break
        offset += page_size

    return ticker_map


def load_tickers_json():
    with open(TICKERS_PATH, encoding='utf-8') as f:
        return set(json.load(f))


def load_prices_keys():
    with open(PRICES_PATH, encoding='utf-8') as f:
        data = json.load(f)
    return set(data.keys())


def run_gate4(fix=False):
    load_env()

    print("\n" + "=" * 60)
    print("  QA Gate 4 - Ticker 유효성 검증")
    print("=" * 60)

    # 1) Supabase에서 전체 ticker 수집
    print("\n[1/3] Supabase 시그널 ticker 수집 중...")
    ticker_map = fetch_all_signal_tickers()
    print(f"  → 고유 ticker {len(ticker_map)}개 발견")

    # 2) 로컬 파일 로드
    print("[2/3] 로컬 파일 대조 중...")
    tickers_set = load_tickers_json()
    prices_set = load_prices_keys()
    print(f"  → stock_tickers.json: {len(tickers_set)}개")
    print(f"  → stockPrices.json: {len(prices_set)}개")

    # 3) 대조
    missing_tickers = []   # tickers.json에 없음
    missing_prices = []    # stockPrices.json에 없음
    missing_both = []      # 둘 다 없음

    for ticker, info in sorted(ticker_map.items()):
        in_tickers = ticker in tickers_set
        in_prices = ticker in prices_set
        if not in_tickers and not in_prices:
            missing_both.append((ticker, info))
        elif not in_tickers:
            missing_tickers.append((ticker, info))
        elif not in_prices:
            missing_prices.append((ticker, info))

    # 결과 출력
    total_missing = len(missing_both) + len(missing_tickers) + len(missing_prices)

    print(f"\n[3/3] 검증 결과:")
    if total_missing == 0:
        print("  ✅ 모든 ticker가 tickers.json + stockPrices.json에 존재합니다.")
        print("=" * 60)
        return 0

    print(f"  ❌ 누락 ticker {total_missing}개 발견\n")
    print(f"  {'ticker':<12} {'종목명':<20} {'마켓':<8} {'시그널수':<8} {'tickers':<10} {'prices':<10}")
    print(f"  {'-'*12} {'-'*20} {'-'*8} {'-'*8} {'-'*10} {'-'*10}")

    for ticker, info in missing_both:
        print(f"  {ticker:<12} {info['stock']:<20} {info['market']:<8} {info['count']:<8} ❌         ❌")
    for ticker, info in missing_tickers:
        print(f"  {ticker:<12} {info['stock']:<20} {info['market']:<8} {info['count']:<8} ❌         ✅")
    for ticker, info in missing_prices:
        print(f"  {ticker:<12} {info['stock']:<20} {info['market']:<8} {info['count']:<8} ✅         ❌")

    # --fix: tickers.json에 누락 ticker 추가
    if fix:
        to_add = [t for t, _ in missing_both] + [t for t, _ in missing_tickers]
        if to_add:
            print(f"\n[FIX] stock_tickers.json에 {len(to_add)}개 ticker 추가 중...")
            with open(TICKERS_PATH, encoding='utf-8') as f:
                tickers_list = json.load(f)
            tickers_list.extend(to_add)
            tickers_list = sorted(set(tickers_list))
            with open(TICKERS_PATH, 'w', encoding='utf-8') as f:
                json.dump(tickers_list, f, ensure_ascii=False, indent=2)
            print(f"  → {len(to_add)}개 추가 완료: {', '.join(to_add)}")
            print(f"  ⚠️  stockPrices.json 가격 데이터는 별도 수집 필요:")
            print(f"     python scripts/fetch_prices.py {' '.join(to_add)}")

    print("\n" + "=" * 60)
    return 1


def main():
    parser = argparse.ArgumentParser(description='QA Gate 4 - Ticker 유효성 검증')
    parser.add_argument('--fix', action='store_true', help='누락 ticker를 stock_tickers.json에 자동 추가')
    args = parser.parse_args()

    code = run_gate4(fix=args.fix)
    sys.exit(code)


if __name__ == '__main__':
    main()
