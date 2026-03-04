"""
수익률 데이터 수집 스크립트 v2 - batch download approach
"""
import json, os, sys, time, requests, signal as sig
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, TimeoutError

BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env.local"
PRICES_FILE = BASE_DIR / "data" / "signal_prices.json"

env = {}
for line in ENV_FILE.read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip()

SUPABASE_URL = env['NEXT_PUBLIC_SUPABASE_URL']
SUPABASE_KEY = env.get('SUPABASE_SERVICE_ROLE_KEY', env['NEXT_PUBLIC_SUPABASE_ANON_KEY'])
headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
}

# Step 1
print("=== Step 1: Fetching signals and videos ===", flush=True)
signals = requests.get(f"{SUPABASE_URL}/rest/v1/influencer_signals?select=id,ticker,created_at,video_id,stock&limit=2000", headers=headers).json()
videos = requests.get(f"{SUPABASE_URL}/rest/v1/influencer_videos?select=id,published_at&limit=2000", headers=headers).json()
video_map = {v['id']: v['published_at'] for v in videos}
print(f"Signals: {len(signals)}, Videos: {len(videos)}", flush=True)

signal_dates = {}
for s in signals:
    sid = s['id']
    pub = video_map.get(s.get('video_id')) if s.get('video_id') else None
    date_str = pub or s.get('created_at')
    if date_str and s.get('ticker'):
        signal_dates[sid] = {'ticker': s['ticker'], 'date': date_str[:10]}

print(f"Signals with dates: {len(signal_dates)}", flush=True)

# Step 2
unique_pairs = set()
for info in signal_dates.values():
    unique_pairs.add((info['ticker'], info['date']))
print(f"\n=== Step 2: Unique pairs: {len(unique_pairs)} ===", flush=True)

# Classify tickers
SKIP_TICKERS = {'BTC', 'ETH', 'SOL', 'DOGE', 'KLAY', 'KS11', 'SOXX', 'XLU', 'GLD'}

def get_yf_ticker(ticker):
    if ticker in SKIP_TICKERS:
        return None
    if '.' in ticker:
        return ticker
    if ticker.isdigit():
        return f"{ticker}.KS"
    return ticker

# Group by yf_ticker to find min/max date range
import yfinance as yf

ticker_date_ranges = {}  # yf_ticker -> (min_date, max_date, [(orig_ticker, date), ...])
for orig_ticker, date_str in unique_pairs:
    yft = get_yf_ticker(orig_ticker)
    if not yft:
        continue
    if yft not in ticker_date_ranges:
        ticker_date_ranges[yft] = {'min': date_str, 'max': date_str, 'pairs': [], 'orig': orig_ticker}
    if date_str < ticker_date_ranges[yft]['min']:
        ticker_date_ranges[yft]['min'] = date_str
    if date_str > ticker_date_ranges[yft]['max']:
        ticker_date_ranges[yft]['max'] = date_str
    ticker_date_ranges[yft]['pairs'].append((orig_ticker, date_str))

print(f"Unique yfinance tickers: {len(ticker_date_ranges)}", flush=True)

# Step 3: Fetch one ticker at a time with timeout
print("\n=== Step 3: Fetching prices ===", flush=True)
price_cache = {}  # (orig_ticker, date) -> close
failed = []
total = len(ticker_date_ranges)
done = 0
batch = 0

for yft, info in sorted(ticker_date_ranges.items()):
    done += 1
    batch += 1
    
    try:
        min_dt = datetime.strptime(info['min'], '%Y-%m-%d') - timedelta(days=7)
        max_dt = datetime.strptime(info['max'], '%Y-%m-%d') + timedelta(days=2)
        
        t = yf.Ticker(yft)
        hist = t.history(start=min_dt.strftime('%Y-%m-%d'), end=max_dt.strftime('%Y-%m-%d'), timeout=10)
        
        if hist.empty and yft.endswith('.KS'):
            yft_kq = info['orig'] + '.KQ'
            t = yf.Ticker(yft_kq)
            hist = t.history(start=min_dt.strftime('%Y-%m-%d'), end=max_dt.strftime('%Y-%m-%d'), timeout=10)
        
        if not hist.empty:
            hist.index = hist.index.tz_localize(None) if hist.index.tz else hist.index
            for orig_ticker, date_str in info['pairs']:
                target = datetime.strptime(date_str, '%Y-%m-%d')
                valid = hist[hist.index <= target]
                if valid.empty:
                    valid = hist.head(1)
                close = float(valid['Close'].iloc[-1])
                price_cache[(orig_ticker, date_str)] = close
        else:
            failed.append(yft)
    except Exception as e:
        failed.append(f"{yft}: {str(e)[:40]}")
    
    if done % 10 == 0:
        print(f"  {done}/{total} tickers done, {len(price_cache)} prices cached", flush=True)
    
    time.sleep(1.5)
    if batch >= 20:
        print(f"  Batch pause at {done}/{total}...", flush=True)
        time.sleep(8)
        batch = 0

print(f"\nPrices cached: {len(price_cache)}, Failed: {len(failed)}", flush=True)

# Step 4: Build signal_prices
print("\n=== Step 4: Updating signal_prices.json ===", flush=True)
existing = json.loads(PRICES_FILE.read_text(encoding='utf-8'))

success = 0
skip = 0
for sid, info in signal_dates.items():
    ticker = info['ticker']
    date_str = info['date']
    
    price_at = price_cache.get((ticker, date_str))
    current_price = existing.get(ticker, {}).get('current_price')
    
    if price_at and current_price:
        ret = round((current_price - price_at) / price_at * 100, 2)
        existing[sid] = {
            'price_at_signal': round(price_at, 2),
            'price_current': current_price,
            'return_pct': ret,
            'signal_date': date_str,
            'ticker': ticker
        }
        success += 1
    else:
        skip += 1

PRICES_FILE.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding='utf-8')

print(f"\n=== DONE ===", flush=True)
print(f"Signals total: {len(signal_dates)}", flush=True)
print(f"Unique pairs: {len(unique_pairs)}", flush=True)
print(f"Unique yf tickers: {len(ticker_date_ranges)}", flush=True)
print(f"Prices fetched: {len(price_cache)}", flush=True)
print(f"Signals with returns: {success}", flush=True)
print(f"Skipped: {skip}", flush=True)
print(f"Failed tickers ({len(failed)}): {failed[:30]}", flush=True)
