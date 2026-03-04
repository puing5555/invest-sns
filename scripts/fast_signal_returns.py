"""Fast signal returns collector - downloads all at once"""
import json, os, requests, yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path

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
headers = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'}

# Fetch signals + videos
print("Fetching signals...", flush=True)
signals = requests.get(f"{SUPABASE_URL}/rest/v1/influencer_signals?select=id,ticker,created_at,video_id,stock&limit=2000", headers=headers).json()
videos = requests.get(f"{SUPABASE_URL}/rest/v1/influencer_videos?select=id,published_at&limit=2000", headers=headers).json()
video_map = {v['id']: v['published_at'] for v in videos}
print(f"Signals: {len(signals)}, Videos: {len(videos)}", flush=True)

# Build signal -> (ticker, date) mapping
SKIP_TICKERS = {'BTC', 'ETH', 'SOL', 'DOGE', 'KLAY', 'KS11', 'SOXX', 'XLU', 'GLD'}
signal_info = {}
for s in signals:
    if not s.get('ticker') or s['ticker'] in SKIP_TICKERS:
        continue
    pub = video_map.get(s.get('video_id')) if s.get('video_id') else None
    date_str = (pub or s.get('created_at', ''))[:10]
    if date_str:
        signal_info[s['id']] = {'ticker': s['ticker'], 'date': date_str, 'stock': s.get('stock', '')}

# Get unique tickers and their yf symbols
def to_yf(t):
    if '.' in t: return t
    if t.isdigit(): return f"{t}.KS"
    return t

unique_tickers = set(v['ticker'] for v in signal_info.values())
yf_map = {t: to_yf(t) for t in unique_tickers}
all_yf = list(set(yf_map.values()))

# Find global date range
all_dates = [v['date'] for v in signal_info.values()]
min_date = min(all_dates)
max_date = max(all_dates)
start = (datetime.strptime(min_date, '%Y-%m-%d') - timedelta(days=10)).strftime('%Y-%m-%d')
end = (datetime.strptime(max_date, '%Y-%m-%d') + timedelta(days=2)).strftime('%Y-%m-%d')

print(f"Unique tickers: {len(unique_tickers)}, yf symbols: {len(all_yf)}", flush=True)
print(f"Date range: {start} to {end}", flush=True)

# Batch download - split into chunks of 50
from functools import reduce
all_hist = {}
chunk_size = 30
for i in range(0, len(all_yf), chunk_size):
    chunk = all_yf[i:i+chunk_size]
    print(f"Downloading chunk {i//chunk_size+1}/{(len(all_yf)+chunk_size-1)//chunk_size} ({len(chunk)} tickers)...", flush=True)
    try:
        data = yf.download(chunk, start=start, end=end, group_by='ticker', timeout=30, progress=False)
        if len(chunk) == 1:
            all_hist[chunk[0]] = data
        else:
            for sym in chunk:
                try:
                    df = data[sym] if sym in data.columns.get_level_values(0) else None
                    if df is not None and not df.empty:
                        all_hist[sym] = df
                except:
                    pass
    except Exception as e:
        print(f"  Chunk failed: {e}", flush=True)

# Also try KOSDAQ for missing KS tickers
missing_ks = [yf_map[t] for t in unique_tickers if yf_map[t].endswith('.KS') and yf_map[t] not in all_hist]
if missing_ks:
    kq_tickers = [t.replace('.KS', '.KQ') for t in missing_ks]
    print(f"Retrying {len(kq_tickers)} as KOSDAQ...", flush=True)
    for i in range(0, len(kq_tickers), chunk_size):
        chunk = kq_tickers[i:i+chunk_size]
        try:
            data = yf.download(chunk, start=start, end=end, group_by='ticker', timeout=30, progress=False)
            if len(chunk) == 1:
                ks = chunk[0].replace('.KQ', '.KS')
                if not data.empty:
                    all_hist[ks] = data
            else:
                for sym in chunk:
                    try:
                        df = data[sym]
                        if df is not None and not df.empty:
                            ks = sym.replace('.KQ', '.KS')
                            all_hist[ks] = df
                    except:
                        pass
        except:
            pass

print(f"Got history for {len(all_hist)} tickers", flush=True)

# Build price lookup: (orig_ticker, date) -> close price
def get_close(hist_df, date_str):
    try:
        target = datetime.strptime(date_str, '%Y-%m-%d')
        idx = hist_df.index.tz_localize(None) if hist_df.index.tz else hist_df.index
        hist_df = hist_df.copy()
        hist_df.index = idx
        valid = hist_df[hist_df.index <= target]
        if valid.empty:
            valid = hist_df.head(1)
        if valid.empty:
            return None
        col = 'Close' if 'Close' in valid.columns else valid.columns[3]  # fallback
        return float(valid[col].iloc[-1])
    except:
        return None

# Load existing prices (ticker -> current_price)
existing = json.loads(PRICES_FILE.read_text(encoding='utf-8'))

# Build signal_prices with signal IDs
result = dict(existing)  # keep ticker entries
success = skip = 0

for sid, info in signal_info.items():
    ticker = info['ticker']
    date_str = info['date']
    yft = yf_map[ticker]
    
    hist_df = all_hist.get(yft)
    current_price = existing.get(ticker, {}).get('current_price')
    
    if hist_df is not None and current_price:
        price_at = get_close(hist_df, date_str)
        if price_at and price_at > 0:
            ret = round((current_price - price_at) / price_at * 100, 2)
            result[sid] = {
                'price_at_signal': round(price_at, 2),
                'price_current': current_price,
                'return_pct': ret,
                'signal_date': date_str,
                'ticker': ticker
            }
            success += 1
            continue
    skip += 1

PRICES_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

# Also copy to public
import shutil
shutil.copy(PRICES_FILE, BASE_DIR / "public" / "signal_prices.json")

print(f"\n=== DONE ===", flush=True)
print(f"Total signals: {len(signal_info)}", flush=True)
print(f"With returns: {success}", flush=True)
print(f"Skipped: {skip}", flush=True)
print(f"Missing hist: {[t for t in unique_tickers if yf_map[t] not in all_hist]}", flush=True)
