"""
Price data rebuild script:
1. Clean UUID garbage from signal_prices.json
2. Query Supabase for actual tickers
3. Fetch missing prices via yfinance
"""
import json, re, time, os, sys

# Load current prices
PRICES_PATH = r'C:\Users\Mario\work\invest-sns\data\signal_prices.json'
with open(PRICES_PATH, 'r', encoding='utf-8') as f:
    prices = json.load(f)

# Step 1: Remove UUID entries (keys that look like UUIDs)
uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
cleaned = {k: v for k, v in prices.items() if not uuid_pattern.match(k)}
removed_count = len(prices) - len(cleaned)
print(f"Removed {removed_count} UUID garbage entries")
print(f"Remaining: {len(cleaned)} entries")

# Classify remaining
kr_tickers = []
us_tickers = []
other_tickers = []
zero_price = []

for k, v in cleaned.items():
    market = v.get('market', '')
    p = v.get('current_price', 0)
    if not p or p == 0:
        zero_price.append((k, v.get('name', '?'), market))
    if market == 'KR':
        kr_tickers.append(k)
    elif market == 'US':
        us_tickers.append(k)
    else:
        other_tickers.append((k, market))

print(f"\nKR: {len(kr_tickers)}, US: {len(us_tickers)}, Other: {len(other_tickers)}")
print(f"Zero price (after cleanup): {len(zero_price)}")
for t, n, m in zero_price:
    print(f"  {t}: {n} ({m})")

# Save cleaned version first
with open(PRICES_PATH, 'w', encoding='utf-8') as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)
print(f"\nSaved cleaned signal_prices.json ({len(cleaned)} entries)")

# Step 2: Query Supabase for distinct tickers
print("\n=== Querying Supabase ===")
try:
    from supabase import create_client
except ImportError:
    os.system('pip install supabase')
    from supabase import create_client

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)
result = sb.table('influencer_signals').select('stock_name, ticker').execute()

# Get unique tickers from DB
db_tickers = {}
for row in result.data:
    ticker = row.get('ticker', '')
    name = row.get('stock_name', '')
    if ticker and not uuid_pattern.match(ticker):
        db_tickers[ticker] = name

print(f"Unique tickers in DB: {len(db_tickers)}")

# Find tickers in DB but missing from prices
missing_from_prices = []
for ticker, name in db_tickers.items():
    if ticker not in cleaned:
        missing_from_prices.append((ticker, name))

print(f"In DB but missing from prices: {len(missing_from_prices)}")
for t, n in sorted(missing_from_prices):
    print(f"  {t}: {n}")

# Step 3: Fetch prices with yfinance
print("\n=== Fetching prices with yfinance ===")
try:
    import yfinance as yf
except ImportError:
    os.system('pip install yfinance')
    import yfinance as yf

# Build list of all tickers needing price fetch
to_fetch = {}

# Zero-price existing entries
for t, n, m in zero_price:
    to_fetch[t] = {'name': n, 'market': m}

# Missing from prices entirely
for t, n in missing_from_prices:
    if t not in to_fetch:
        # Guess market
        if re.match(r'^\d{6}$', t):
            market = 'KR'
        elif re.match(r'^[A-Z]+$', t):
            market = 'US'
        else:
            market = 'OTHER'
        to_fetch[t] = {'name': n, 'market': market}

# Also add existing KR/US tickers to refresh all prices
for t in kr_tickers + us_tickers:
    if t not in to_fetch:
        to_fetch[t] = {'name': cleaned[t].get('name', '?'), 'market': cleaned[t].get('market', '?')}

print(f"Total tickers to fetch: {len(to_fetch)}")

# Map ticker to yfinance symbol
def get_yf_symbol(ticker, market):
    if market == 'KR':
        # Try both .KS (KOSPI) and .KQ (KOSDAQ)
        return [f"{ticker}.KS", f"{ticker}.KQ"]
    elif market in ('US', 'US_ADR'):
        return [ticker]
    elif market == 'HK':
        if not ticker.endswith('.HK'):
            return [f"{ticker}.HK"]
        return [ticker]
    elif market in ('CRYPTO', 'CRYPTO_DEFI'):
        return [f"{ticker}-USD"]
    elif market == 'ETF':
        return [ticker]
    elif market == 'OTHER':
        # Try as-is first
        return [ticker]
    else:
        return [ticker]

# Batch fetch
all_tickers_list = list(to_fetch.keys())
updated_count = 0
failed = []
today = "2026-03-04"

for i in range(0, len(all_tickers_list), 10):
    batch = all_tickers_list[i:i+10]
    print(f"\nBatch {i//10 + 1}: {batch}")
    
    for ticker in batch:
        info = to_fetch[ticker]
        symbols = get_yf_symbol(ticker, info['market'])
        
        price = None
        currency = 'KRW' if info['market'] == 'KR' else 'USD'
        
        for sym in symbols:
            try:
                data = yf.Ticker(sym)
                hist = data.history(period='5d')
                if not hist.empty:
                    price = round(float(hist['Close'].iloc[-1]), 2)
                    # Determine currency
                    try:
                        fi = data.fast_info
                        currency = getattr(fi, 'currency', currency)
                    except:
                        pass
                    break
            except Exception as e:
                continue
        
        if price and price > 0:
            # Determine market properly
            market = info['market']
            if market in (None, '', 'OTHER', '?'):
                if re.match(r'^\d{6}$', ticker):
                    market = 'KR'
                elif re.match(r'^[A-Z]+$', ticker):
                    market = 'US'
            
            cleaned[ticker] = {
                'name': info['name'] if info['name'] != '?' else cleaned.get(ticker, {}).get('name', ticker),
                'ticker': ticker,
                'market': market,
                'current_price': price if market != 'KR' else int(price),
                'currency': currency,
                'last_updated': today
            }
            updated_count += 1
            print(f"  ✅ {ticker}: {price} {currency}")
        else:
            failed.append((ticker, info['name']))
            print(f"  ❌ {ticker}: no data")
    
    # Rate limit
    if i + 10 < len(all_tickers_list):
        time.sleep(2)

# Save final
with open(PRICES_PATH, 'w', encoding='utf-8') as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

print(f"\n=== RESULTS ===")
print(f"UUID garbage removed: {removed_count}")
print(f"Prices updated: {updated_count}")
print(f"Failed to fetch: {len(failed)}")
for t, n in failed:
    print(f"  {t}: {n}")
print(f"Final entries in signal_prices.json: {len(cleaned)}")

# Save audit report
report = f"""# Price Audit Report - {today}

## Summary
- Total entries before cleanup: {len(prices)}
- UUID garbage removed: {removed_count}
- Valid entries after cleanup: {len(cleaned)}
- KR stocks: {len(kr_tickers)}
- US stocks: {len(us_tickers)}
- Other: {len(other_tickers)}
- Prices updated: {updated_count}
- Failed to fetch: {len(failed)}

## Failed Tickers
"""
for t, n in failed:
    report += f"- {t}: {n}\n"

with open(r'C:\Users\Mario\work\invest-sns\data\price_audit_report.md', 'w', encoding='utf-8') as f:
    f.write(report)

print("\nAudit report saved to data/price_audit_report.md")
