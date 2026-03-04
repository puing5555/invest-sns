import json, re, time, os
import urllib.request

PRICES_PATH = r'C:\Users\Mario\work\invest-sns\data\signal_prices.json'
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

with open(PRICES_PATH, 'r', encoding='utf-8') as f:
    prices = json.load(f)

print(f"Current entries: {len(prices)}")

# Query Supabase REST API for distinct tickers
uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

url = f"{SUPABASE_URL}/rest/v1/influencer_signals?select=stock_name,ticker"
req = urllib.request.Request(url, headers={
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Range': '0-999'
})
resp = urllib.request.urlopen(req)
data = json.loads(resp.read())
print(f"Total rows from DB: {len(data)}")

# Get unique non-UUID tickers
db_tickers = {}
for row in data:
    t = row.get('ticker', '')
    n = row.get('stock_name', '')
    if t and not uuid_pattern.match(t):
        db_tickers[t] = n

print(f"Unique valid tickers in DB: {len(db_tickers)}")

# Find missing
missing = {t: n for t, n in db_tickers.items() if t not in prices}
print(f"In DB but missing from prices: {len(missing)}")
for t, n in sorted(missing.items()):
    print(f"  {t}: {n}")

# Now fetch prices for missing tickers using yfinance
if missing:
    import yfinance as yf
    today = "2026-03-04"
    updated = 0
    failed = []
    
    all_missing = list(missing.items())
    for i in range(0, len(all_missing), 10):
        batch = all_missing[i:i+10]
        for ticker, name in batch:
            # Determine market and yf symbol
            if re.match(r'^\d{6}$', ticker):
                symbols = [f"{ticker}.KS", f"{ticker}.KQ"]
                market = 'KR'
                currency = 'KRW'
            elif ticker.endswith('.HK'):
                symbols = [ticker]
                market = 'HK'
                currency = 'HKD'
            elif ticker in ('BTC', 'ETH', 'SOL', 'DOGE', 'KLAY'):
                symbols = [f"{ticker}-USD"]
                market = 'CRYPTO'
                currency = 'USD'
            else:
                symbols = [ticker]
                market = 'US'
                currency = 'USD'
            
            price = None
            for sym in symbols:
                try:
                    d = yf.Ticker(sym)
                    h = d.history(period='5d')
                    if not h.empty:
                        price = round(float(h['Close'].iloc[-1]), 2)
                        break
                except:
                    continue
            
            if price and price > 0:
                prices[ticker] = {
                    'name': name,
                    'ticker': ticker,
                    'market': market,
                    'current_price': int(price) if market == 'KR' else price,
                    'currency': currency,
                    'last_updated': today
                }
                updated += 1
                print(f"  ✅ {ticker} ({name}): {price}")
            else:
                failed.append((ticker, name))
                print(f"  ❌ {ticker} ({name}): no data")
        
        if i + 10 < len(all_missing):
            time.sleep(2)
    
    print(f"\nUpdated: {updated}, Failed: {len(failed)}")

# Also refresh existing prices
print("\n=== Refreshing all existing prices ===")
import yfinance as yf
today = "2026-03-04"
refresh_count = 0

all_existing = list(prices.keys())
for i in range(0, len(all_existing), 10):
    batch = all_existing[i:i+10]
    # Build yf symbols
    yf_map = {}
    for t in batch:
        m = prices[t].get('market', '')
        if m == 'KR':
            yf_map[t] = [f"{t}.KS", f"{t}.KQ"]
        elif m == 'HK':
            yf_map[t] = [t if t.endswith('.HK') else f"{t}.HK"]
        elif m in ('CRYPTO', 'CRYPTO_DEFI'):
            yf_map[t] = [f"{t}-USD"]
        else:
            yf_map[t] = [t]
    
    for t in batch:
        for sym in yf_map[t]:
            try:
                d = yf.Ticker(sym)
                h = d.history(period='5d')
                if not h.empty:
                    p = round(float(h['Close'].iloc[-1]), 2)
                    if p > 0:
                        prices[t]['current_price'] = int(p) if prices[t].get('market') == 'KR' else p
                        prices[t]['last_updated'] = today
                        refresh_count += 1
                        break
            except:
                continue
    
    print(f"  Batch {i//10+1}/{(len(all_existing)+9)//10} done")
    if i + 10 < len(all_existing):
        time.sleep(2)

print(f"Refreshed: {refresh_count}/{len(all_existing)}")

# Save
with open(PRICES_PATH, 'w', encoding='utf-8') as f:
    json.dump(prices, f, ensure_ascii=False, indent=2)

print(f"\nFinal: {len(prices)} entries saved")

# Audit report
report = f"""# Price Audit Report - {today}

## Summary
- Valid entries: {len(prices)}
- KR: {len([k for k,v in prices.items() if v.get('market')=='KR'])}
- US: {len([k for k,v in prices.items() if v.get('market')=='US'])}
- Other: {len([k for k,v in prices.items() if v.get('market') not in ('KR','US')])}
- Newly added from DB: {len(missing)}
- Prices refreshed: {refresh_count}
"""
with open(r'C:\Users\Mario\work\invest-sns\data\price_audit_report.md', 'w', encoding='utf-8') as f:
    f.write(report)
print("Audit report saved")
