import sys
sys.stdout.reconfigure(encoding='utf-8')
import json, requests

key = open('.env.local').readlines()[2].split('=',1)[1].strip()
h = {'apikey': key, 'Authorization': 'Bearer ' + key}

# Get current DB stocks
r = requests.get('https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals?select=stock,ticker', headers=h)
signals = r.json()
db_stocks = set(s['stock'] for s in signals if s.get('stock'))
db_tickers = set(s['ticker'] for s in signals if s.get('ticker'))

sp = json.load(open('data/signal_prices.json', 'r', encoding='utf-8'))

# Keep only keys that match a DB stock name or ticker
clean = {}
removed_keys = []
for k, v in sp.items():
    if k in db_stocks or k in db_tickers:
        clean[k] = v
    else:
        removed_keys.append(k)

print(f"Before: {len(sp)} keys")
print(f"Removed: {len(removed_keys)}")
for rk in sorted(removed_keys):
    print(f"  - {rk}")
print(f"After: {len(clean)} keys")

json.dump(clean, open('data/signal_prices.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print("Saved!")
