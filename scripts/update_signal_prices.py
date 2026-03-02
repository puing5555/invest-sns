"""
해외 종목 시그널 가격 데이터 업데이트
"""
import json
import os
import urllib.request

SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
SIGNAL_PRICES_PATH = os.path.join(DATA_DIR, 'signal_prices.json')
STOCK_PRICES_PATH = os.path.join(DATA_DIR, 'stockPrices.json')

FOREIGN_CODES = [
    'BTC', 'ETH', 'SOL', 'DOGE', 'KLAY',
    'NVDA', 'TSLA', 'PLTR', 'AMD', 'TSM', 'ASML', 'GOOGL',
    'MSTR', 'RKLB', 'SQ', 'RIOT', 'GBTC', 'COIN', 'IREN',
    'GME', 'SOXX', 'MU', 'KS11',
]

def supabase_get(path):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    req = urllib.request.Request(url, headers={
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def find_price_at_date(prices, target_date):
    target = target_date[:10]
    best = None
    for p in prices:
        if p['date'] <= target:
            best = p['close']
        else:
            break
    return best

def main():
    with open(STOCK_PRICES_PATH, 'r', encoding='utf-8') as f:
        stock_prices = json.load(f)
    with open(SIGNAL_PRICES_PATH, 'r', encoding='utf-8') as f:
        signal_prices = json.load(f)
    
    # Fetch all signals
    print("Fetching signals...")
    signals = supabase_get('influencer_signals?limit=2000')
    print(f"Total signals: {len(signals)}")
    
    # Fetch all videos for published_at dates
    print("Fetching videos...")
    videos = supabase_get('influencer_videos?select=id,published_at&limit=2000')
    video_map = {v['id']: v['published_at'] for v in videos}
    print(f"Total videos: {len(videos)}")
    
    foreign_signals = [s for s in signals if s.get('ticker') in FOREIGN_CODES]
    print(f"Foreign stock signals: {len(foreign_signals)}")
    
    updated = 0
    for signal in foreign_signals:
        sid = signal['id']
        code = signal['ticker']
        
        if sid in signal_prices and signal_prices[sid].get('price_at_signal'):
            continue
        
        if code not in stock_prices:
            continue
        
        published_at = video_map.get(signal.get('video_id'))
        if not published_at:
            continue
        
        price_history = stock_prices[code].get('prices', [])
        current_price = stock_prices[code].get('currentPrice', 0)
        
        price_at_signal = find_price_at_date(price_history, published_at)
        if not price_at_signal:
            continue
        
        return_pct = round((current_price - price_at_signal) / price_at_signal * 100, 2) if price_at_signal else 0
        
        signal_prices[sid] = {
            'price_at_signal': price_at_signal,
            'price_current': current_price,
            'return_pct': return_pct,
        }
        updated += 1
    
    with open(SIGNAL_PRICES_PATH, 'w', encoding='utf-8') as f:
        json.dump(signal_prices, f, ensure_ascii=False, indent=2)
    
    print(f"Updated {updated} signal prices. Total: {len(signal_prices)}")

if __name__ == '__main__':
    main()
