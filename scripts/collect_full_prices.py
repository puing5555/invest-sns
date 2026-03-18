"""
stockPrices.json 전체 기간 수집 (용량 최적화)

- 3년 이내: 일별 데이터
- 3~5년: 주간 데이터
- 5년+: 월간 데이터

사용법:
  PYTHONIOENCODING=utf-8 python scripts/collect_full_prices.py
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    print("pip install yfinance")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
SP_PATH = PROJECT_ROOT / "data" / "stockPrices.json"

def get_yahoo_ticker(code: str) -> str:
    """종목코드 → Yahoo Finance ticker"""
    if code.endswith('.KS') or code.endswith('.KQ'):
        return code
    # 6자리 숫자 = 한국 종목
    if code.isdigit() and len(code) == 6:
        return f"{code}.KS"
    # 그 외 = 그대로 (US, CRYPTO 등)
    return code

def downsample(prices: list, cutoff_3y: str, cutoff_5y: str) -> list:
    """
    3년 이내: 일별 유지
    3~5년: 주간 (월요일만)
    5년+: 월간 (매월 1일에 가장 가까운 거래일)
    """
    result = []
    last_week = None
    last_month = None

    for p in prices:
        d = p['date']
        if d >= cutoff_3y:
            # 3년 이내: 일별
            result.append(p)
        elif d >= cutoff_5y:
            # 3~5년: 주간
            dt = datetime.strptime(d, '%Y-%m-%d')
            week_key = dt.isocalendar()[:2]  # (year, week)
            if week_key != last_week:
                result.append(p)
                last_week = week_key
        else:
            # 5년+: 월간
            month_key = d[:7]  # YYYY-MM
            if month_key != last_month:
                result.append(p)
                last_month = month_key

    return result

def fetch_ticker(ticker: str, yahoo_ticker: str) -> dict | None:
    """Yahoo Finance에서 max 기간 다운로드"""
    try:
        data = yf.download(yahoo_ticker, period="max", progress=False, timeout=15)
        if data.empty:
            # .KS 실패 시 .KQ 시도
            if yahoo_ticker.endswith('.KS'):
                alt = yahoo_ticker.replace('.KS', '.KQ')
                data = yf.download(alt, period="max", progress=False, timeout=15)
            if data.empty:
                return None

        prices = []
        for idx, row in data.iterrows():
            close = row['Close']
            if hasattr(close, 'iloc'):
                close = close.iloc[0]
            close = float(close)
            if close > 0:
                vol = row.get('Volume', 0)
                if hasattr(vol, 'iloc'):
                    vol = vol.iloc[0]
                prices.append({
                    'date': idx.strftime('%Y-%m-%d'),
                    'close': round(close, 2),
                })

        if not prices:
            return None

        current = prices[-1]['close']
        prev = prices[-2]['close'] if len(prices) >= 2 else current
        change = round(((current - prev) / prev) * 100, 2) if prev else 0

        return {
            'prices': prices,
            'currentPrice': current,
            'change': change,
            'totalEntries': len(prices),
        }

    except Exception as e:
        return None

def main():
    sp = json.load(open(SP_PATH, encoding='utf-8'))
    tickers = list(sp.keys())
    total = len(tickers)

    now = datetime.now()
    cutoff_3y = (now - timedelta(days=3*365)).strftime('%Y-%m-%d')
    cutoff_5y = (now - timedelta(days=5*365)).strftime('%Y-%m-%d')

    print(f"총 {total}개 종목 수집 (period=max)")
    print(f"3년 컷오프: {cutoff_3y}, 5년 컷오프: {cutoff_5y}")
    print()

    updated = 0
    failed = 0
    skipped = 0

    for i, ticker in enumerate(tickers):
        yahoo = get_yahoo_ticker(ticker)
        print(f"[{i+1:3d}/{total}] {ticker:12s} ({yahoo})", end=" ", flush=True)

        result = fetch_ticker(ticker, yahoo)
        if not result:
            print("FAIL")
            failed += 1
            time.sleep(0.3)
            continue

        raw_count = result['totalEntries']
        # Downsample
        ds_prices = downsample(result['prices'], cutoff_3y, cutoff_5y)

        # Preserve existing metadata (name, ticker field)
        existing = sp[ticker]
        if isinstance(existing, dict):
            existing['prices'] = ds_prices
            existing['currentPrice'] = result['currentPrice']
            existing['change'] = result['change']
        else:
            sp[ticker] = ds_prices

        print(f"OK  {raw_count} → {len(ds_prices)} entries  ({result['prices'][0]['date']}~)")
        updated += 1

        # Rate limit
        if (i + 1) % 50 == 0:
            print(f"\n--- {i+1}/{total} 완료, 10초 대기 ---\n")
            time.sleep(10)
        else:
            time.sleep(0.3)

    # Save
    json.dump(sp, open(SP_PATH, 'w', encoding='utf-8'), ensure_ascii=False)
    size_mb = os.path.getsize(SP_PATH) / 1024 / 1024

    print(f"\n{'='*60}")
    print(f"완료: {updated} 업데이트, {failed} 실패, {skipped} 스킵")
    print(f"파일: {SP_PATH} ({size_mb:.1f} MB)")
    print(f"다운샘플: 3년이내=일별, 3~5년=주간, 5년+=월간")

if __name__ == "__main__":
    main()
