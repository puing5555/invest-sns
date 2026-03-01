"""
시그널 시점 주가 + 현재 주가 JSON 생성
Output: data/signal_prices.json
"""
import requests, json, time
import yfinance as yf
from datetime import datetime, timedelta

BASE = 'https://arypzhotxflimroprmdk.supabase.co/rest/v1/'
KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}'}

# 종목명 → Yahoo ticker
TICKER_MAP = {
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
    try:
        dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
        start = dt - timedelta(days=7)
        end = dt + timedelta(days=3)
        hist = yf.Ticker(yahoo_ticker).history(start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
        if hist.empty: return None
        hist.index = hist.index.tz_localize(None)
        before = hist[hist.index <= dt]
        if not before.empty:
            return int(before.iloc[-1]['Close'])
        return int(hist.iloc[0]['Close'])
    except Exception as e:
        print(f"  Error {yahoo_ticker} @ {date_str}: {e}")
        return None

def get_current_price(yahoo_ticker):
    try:
        hist = yf.Ticker(yahoo_ticker).history(period='5d')
        if hist.empty: return None
        return int(hist.iloc[-1]['Close'])
    except Exception as e:
        print(f"  Error current {yahoo_ticker}: {e}")
        return None

def main():
    # Get all KR signals
    r = requests.get(BASE + 'influencer_signals?select=id,stock,ticker,market,signal,influencer_videos(published_at)&market=eq.KR', headers=H)
    signals = r.json()
    print(f"KR signals: {len(signals)}")

    # Cache
    current_cache = {}
    date_cache = {}
    result = {}

    for sig in signals:
        stock = sig['stock']
        yt = TICKER_MAP.get(stock)
        if not yt:
            print(f"  Skip (no mapping): {stock}")
            continue

        pub = sig.get('influencer_videos', {}).get('published_at')
        if not pub: continue

        # Current price
        if yt not in current_cache:
            current_cache[yt] = get_current_price(yt)
            time.sleep(0.3)
            print(f"  Current {stock}: {current_cache[yt]}")

        # Price at signal
        dk = (yt, pub)
        if dk not in date_cache:
            date_cache[dk] = get_price_at_date(yt, pub)
            time.sleep(0.3)
            print(f"  {stock} @ {pub}: {date_cache[dk]}")

        price_at = date_cache[dk]
        price_cur = current_cache[yt]
        
        if price_at and price_cur:
            ret = round((price_cur - price_at) / price_at * 100, 2)
        else:
            ret = None

        result[sig['id']] = {
            'price_at_signal': price_at,
            'price_current': price_cur,
            'return_pct': ret,
        }

    with open('data/signal_prices.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nDone: {len(result)} prices written to data/signal_prices.json")
    # Also write current prices map for frontend
    stock_prices = {}
    for stock, yt in TICKER_MAP.items():
        if yt in current_cache and current_cache[yt]:
            stock_prices[stock] = current_cache[yt]
    
    with open('data/current_prices.json', 'w', encoding='utf-8') as f:
        json.dump({'updated_at': datetime.now().isoformat(), 'prices': stock_prices}, f, ensure_ascii=False, indent=2)
    print(f"Current prices: {len(stock_prices)} stocks")

if __name__ == '__main__':
    main()
