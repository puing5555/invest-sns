import json, urllib.request

SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co'
ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAyMjIxNjcsImV4cCI6MjA1NTc5ODE2N30.N8vJRyFMOImA0uQzCMiMac0GdFn2MqSFSdXDcmknJHA'

headers = {'apikey': ANON_KEY, 'Authorization': f'Bearer {ANON_KEY}'}
url = f'{SUPABASE_URL}/rest/v1/influencer_signals?select=id,stock,ticker,signal_date'
req = urllib.request.Request(url, headers=headers)
data = json.loads(urllib.request.urlopen(req).read())
print(f'Total signals: {len(data)}')

prices = json.load(open('data/signal_prices.json', 'r', encoding='utf-8'))
covered = set(prices.keys())
print(f'Covered in prices: {len(covered)}')

missing = [d for d in data if d['id'] not in covered]
print(f'Missing: {len(missing)}')
for m in missing:
    print(f"  {m['id'][:8]}.. | {m['stock']} | {m['ticker']} | {m['signal_date']}")

# Also show unique tickers for all signals
all_tickers = {}
for d in data:
    t = d.get('ticker', '')
    if t:
        if t not in all_tickers:
            all_tickers[t] = []
        all_tickers[t].append(d['stock'])

print(f"\nUnique tickers ({len(all_tickers)}):")
for t in sorted(all_tickers.keys()):
    print(f"  {t} -> {all_tickers[t][0]}")
