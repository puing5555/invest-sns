import urllib.request, json, ssl, re

ctx = ssl.create_default_context()
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

uuid_pat = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

# Get all tickers from DB (paginate)
all_rows = []
for offset in range(0, 10000, 1000):
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals?select=stock,ticker,market&offset={offset}&limit=1000"
    req = urllib.request.Request(url)
    req.add_header('apikey', KEY)
    req.add_header('Authorization', f'Bearer {KEY}')
    resp = urllib.request.urlopen(req, context=ctx)
    data = json.loads(resp.read())
    if not data:
        break
    all_rows.extend(data)
    print(f"Fetched {len(data)} rows (total: {len(all_rows)})")

# Unique tickers
tickers = {}
for r in all_rows:
    t = r.get('ticker', '')
    n = r.get('stock', '')
    m = r.get('market', '')
    if t and not uuid_pat.match(t):
        tickers[t] = {'name': n, 'market': m}

print(f"\nUnique valid tickers in DB: {len(tickers)}")

# Load current prices
with open(r'C:\Users\Mario\work\invest-sns\data\signal_prices.json', 'r', encoding='utf-8') as f:
    prices = json.load(f)

missing = {t: v for t, v in tickers.items() if t not in prices}
print(f"In prices: {len(prices)}")
print(f"Missing from prices: {len(missing)}")
for t, v in sorted(missing.items()):
    print(f"  {t}: {v['name']} ({v['market']})")

# Save missing list for next step
with open(r'C:\Users\Mario\work\invest-sns\scripts\missing_tickers.json', 'w', encoding='utf-8') as f:
    json.dump(missing, f, ensure_ascii=False, indent=2)
