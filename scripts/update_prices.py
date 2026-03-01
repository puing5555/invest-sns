"""
시그널 시점 주가 + 현재 주가 업데이트 스크립트
- price_at_signal: 영상 published_at 날짜의 종가 (yfinance)
- price_current: 현재가 (yfinance)
- return_pct: 수익률 계산
한국 주식만 (market=KR)
"""
import requests, json, time
import yfinance as yf
from datetime import datetime, timedelta

BASE = 'https://arypzhotxflimroprmdk.supabase.co/rest/v1/'
KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json', 'Prefer': 'return=representation'}

# 종목명 → Yahoo ticker 매핑
STOCK_TICKER_MAP = {
    '삼성전자': '005930.KS',
    'SK하이닉스': '000660.KS',
    '현대차': '005380.KS',
    '효성중공업': '298040.KS',
    '주성엔지니어링': '036930.KQ',
    '한미반도체': '042700.KQ',
    '테스': '095610.KQ',
    '네이버': '035420.KS',
    '현대건설': '000720.KS',
    '신세계': '004170.KS',
    '삼성SDI': '006400.KS',
    'HD현대일렉트릭': '267260.KS',
    'LG화학': '051910.KS',
    '아모레퍼시픽': '090430.KS',
    'NC소프트': '036570.KS',
    '삼성바이오로직스': '207940.KS',
    'CGV': '079160.KS',
    'HPSP': '403870.KQ',
    '원익IPS': '240810.KQ',
    '레인보우로보틱스': '277810.KQ',
    '코스모신소재': '005070.KS',
    '두산에너빌리티': '034020.KS',
    '현대모비스': '012330.KS',
    'LS일렉트릭': '010120.KS',
}

def get_price_at_date(yahoo_ticker, date_str):
    """특정 날짜의 종가 가져오기"""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        start = dt - timedelta(days=5)  # 주말/공휴일 대비
        end = dt + timedelta(days=3)
        ticker = yf.Ticker(yahoo_ticker)
        hist = ticker.history(start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
        if hist.empty:
            return None
        # 해당 날짜 이전 가장 가까운 종가
        hist.index = hist.index.tz_localize(None)
        before = hist[hist.index <= dt]
        if not before.empty:
            return int(before.iloc[-1]['Close'])
        return int(hist.iloc[0]['Close'])
    except Exception as e:
        print(f"  Error getting price for {yahoo_ticker} at {date_str}: {e}")
        return None

def get_current_price(yahoo_ticker):
    """현재가 가져오기"""
    try:
        ticker = yf.Ticker(yahoo_ticker)
        hist = ticker.history(period='5d')
        if hist.empty:
            return None
        return int(hist.iloc[-1]['Close'])
    except Exception as e:
        print(f"  Error getting current price for {yahoo_ticker}: {e}")
        return None

def main():
    # 1. Get all KR signals
    r = requests.get(
        BASE + 'influencer_signals?select=id,stock,ticker,market,signal,price_at_signal,price_current,influencer_videos(published_at)&market=eq.KR',
        headers=H
    )
    signals = r.json()
    print(f"Total KR signals: {len(signals)}")

    # 2. Cache current prices per stock
    current_prices = {}
    signal_prices = {}  # (yahoo_ticker, date) -> price

    updated = 0
    skipped = 0
    failed = 0

    for sig in signals:
        stock_name = sig['stock']
        yahoo_ticker = STOCK_TICKER_MAP.get(stock_name)
        
        if not yahoo_ticker:
            # Try SECTOR signals - skip
            if stock_name.endswith('섹터') or stock_name.endswith('셀'):
                skipped += 1
                continue
            print(f"  No ticker mapping for: {stock_name}")
            skipped += 1
            continue

        pub_date = sig.get('influencer_videos', {}).get('published_at')
        if not pub_date:
            print(f"  No published_at for signal {sig['id']}")
            skipped += 1
            continue

        # Get price_at_signal
        cache_key = (yahoo_ticker, pub_date)
        if cache_key not in signal_prices:
            signal_prices[cache_key] = get_price_at_date(yahoo_ticker, pub_date)
            time.sleep(0.5)
        
        price_at = signal_prices[cache_key]

        # Get current price
        if yahoo_ticker not in current_prices:
            current_prices[yahoo_ticker] = get_current_price(yahoo_ticker)
            time.sleep(0.5)
        
        price_cur = current_prices[yahoo_ticker]

        if price_at is None and price_cur is None:
            failed += 1
            continue

        # Calculate return
        return_pct = None
        if price_at and price_cur:
            return_pct = round((price_cur - price_at) / price_at * 100, 2)

        # Update DB
        patch = {}
        if price_at: patch['price_at_signal'] = price_at
        if price_cur: patch['price_current'] = price_cur
        if return_pct is not None: patch['return_pct'] = return_pct

        if patch:
            r2 = requests.patch(
                BASE + f'influencer_signals?id=eq.{sig["id"]}',
                headers=H,
                json=patch
            )
            if r2.status_code in (200, 204):
                print(f"  ✅ {stock_name} ({pub_date}): {price_at} → {price_cur} ({return_pct}%)")
                updated += 1
            else:
                print(f"  ❌ Update failed for {sig['id']}: {r2.status_code} {r2.text}")
                failed += 1

    print(f"\n=== Done: {updated} updated, {skipped} skipped, {failed} failed ===")

if __name__ == '__main__':
    main()
