"""
해외주식/코인 가격 데이터 수집 스크립트
CoinGecko API + Yahoo Finance (yfinance)
"""
import json
import os
import time
import urllib.request
from datetime import datetime

COIN_MAP = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum', 
    'SOL': 'solana',
    'DOGE': 'dogecoin',
    'KLAY': 'klay-token',
}

STOCK_TICKERS = [
    'NVDA', 'TSLA', 'PLTR', 'AMD', 'TSM', 'ASML', 'GOOGL',
    'MSTR', 'RKLB', 'SQ', 'RIOT', 'GBTC', 'COIN', 'IREN',
    'GME', 'SOXX', 'MU',
]

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
STOCK_PRICES_PATH = os.path.join(DATA_DIR, 'stockPrices.json')
USD_KRW = 1380

def fetch_json(url, retries=5, delay=30):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except Exception as e:
            print(f"  Attempt {i+1}/{retries} failed: {e}")
            if i < retries - 1:
                wait = delay * (i + 1)
                print(f"  Waiting {wait}s...")
                time.sleep(wait)
    return None

def get_usd_krw():
    global USD_KRW
    data = fetch_json('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=krw,usd')
    if data:
        USD_KRW = round(data['bitcoin']['krw'] / data['bitcoin']['usd'])
        print(f"USD/KRW: {USD_KRW}")

def fetch_coin_prices():
    results = {}
    for code, cg_id in COIN_MAP.items():
        print(f"Fetching {code} ({cg_id})...")
        
        # Current price
        time.sleep(15)
        current = fetch_json(f'https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=krw&include_24hr_change=true')
        if not current:
            print(f"  Skipping {code}")
            continue
        
        price_krw = current[cg_id]['krw']
        change_pct = current[cg_id].get('krw_24h_change', 0) or 0
        change = round(price_krw * change_pct / 100)
        
        # History
        time.sleep(15)
        hist = fetch_json(f'https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart?vs_currency=krw&days=365', delay=20)
        if not hist:
            # Still save current price with empty history
            results[code] = {'currentPrice': round(price_krw), 'change': round(change), 'changePercent': round(change_pct, 2), 'prices': []}
            continue
        
        seen = {}
        for ts, p in hist['prices']:
            dt = datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d')
            seen[dt] = {'date': dt, 'close': round(p)}
        prices = sorted(seen.values(), key=lambda x: x['date'])
        
        results[code] = {
            'currentPrice': round(price_krw),
            'change': round(change),
            'changePercent': round(change_pct, 2),
            'prices': prices,
        }
        print(f"  {code}: {price_krw:,.0f} KRW, {len(prices)} pts")
    
    return results

def fetch_stock_prices():
    import yfinance as yf
    results = {}
    
    all_tickers = STOCK_TICKERS + ['^KS11']
    
    for ticker in all_tickers:
        code = 'KS11' if ticker == '^KS11' else ticker
        print(f"Fetching {code}...")
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period='1y')
            if hist.empty:
                print(f"  No data")
                continue
            
            last = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2] if len(hist) > 1 else last
            is_krw = ticker == '^KS11'
            
            price_krw = round(last) if is_krw else round(last * USD_KRW)
            change_krw = round(last - prev) if is_krw else round((last - prev) * USD_KRW)
            change_pct = round((last - prev) / prev * 100, 2) if prev else 0
            
            prices = []
            for date, row in hist.iterrows():
                dt = date.strftime('%Y-%m-%d')
                close = round(row['Close']) if is_krw else round(row['Close'] * USD_KRW)
                prices.append({'date': dt, 'close': close})
            
            results[code] = {'currentPrice': price_krw, 'change': change_krw, 'changePercent': change_pct, 'prices': prices}
            print(f"  {code}: {price_krw:,.0f} KRW, {len(prices)} pts")
        except Exception as e:
            print(f"  Error: {e}")
    
    return results

def main():
    print("=== USD/KRW ===")
    get_usd_krw()
    
    print("\n=== Coins (CoinGecko) ===")
    coin_data = fetch_coin_prices()
    
    print("\n=== Stocks (Yahoo Finance) ===")
    stock_data = fetch_stock_prices()
    
    with open(STOCK_PRICES_PATH, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    existing.update(coin_data)
    existing.update(stock_data)
    
    with open(STOCK_PRICES_PATH, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False)
    
    print(f"\nDone! {len(coin_data)} coins + {len(stock_data)} stocks updated. Total: {len(existing)}")

if __name__ == '__main__':
    main()
