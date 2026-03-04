import json, time, requests, sys
from datetime import date

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
PRICES_FILE = r"C:\Users\Mario\work\invest-sns\data\signal_prices.json"
TODAY = date.today().isoformat()

# Step 1: Get all tickers from DB
headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
all_tickers = set()
offset = 0
while True:
    r = requests.get(f"{SUPABASE_URL}/rest/v1/influencer_signals?select=ticker&offset={offset}&limit=1000", headers=headers)
    data = r.json()
    if not data:
        break
    for row in data:
        if row.get("ticker"):
            all_tickers.add(row["ticker"])
    offset += 1000

print(f"DB tickers: {len(all_tickers)}")

# Load existing prices
with open(PRICES_FILE, "r", encoding="utf-8") as f:
    prices = json.load(f)

existing = set(prices.keys())
missing = sorted(all_tickers - existing)
print(f"Existing: {len(existing)}, Missing: {len(missing)}")
print(f"Missing tickers: {missing}")

if not missing:
    print("No missing tickers!")
    sys.exit(0)

# Step 2: Fetch prices from Yahoo Finance
def is_korean(ticker):
    return ticker.isdigit() and len(ticker) == 6

def fetch_yahoo_price(symbol, retries=3):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    for attempt in range(retries):
        try:
            r = requests.get(url, headers={"User-Agent": ua}, timeout=10)
            if r.status_code == 429:
                print(f"  429 rate limit, waiting 60s...")
                time.sleep(60)
                continue
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}"
            data = r.json()
            result = data.get("chart", {}).get("result")
            if not result:
                return None, "no result"
            meta = result[0].get("meta", {})
            price = meta.get("regularMarketPrice")
            if price:
                return price, None
            return None, "no price in meta"
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(5)
            return None, str(e)
    return None, "max retries"

success = 0
failed = []
total = len(missing)

for i, ticker in enumerate(missing):
    if is_korean(ticker):
        # Try .KS first, then .KQ
        symbols = [f"{ticker}.KS", f"{ticker}.KQ"]
    else:
        symbols = [ticker]
    
    price = None
    err = None
    for sym in symbols:
        price, err = fetch_yahoo_price(sym)
        if price is not None:
            break
        time.sleep(1)
    
    if price is not None:
        currency = "KRW" if is_korean(ticker) else "USD"
        prices[ticker] = {
            "name": ticker,
            "ticker": ticker,
            "market": "KR" if is_korean(ticker) else "US",
            "current_price": price,
            "currency": currency,
            "last_updated": TODAY
        }
        success += 1
        print(f"  [{i+1}/{total}] {ticker} = {price}")
    else:
        prices[ticker] = {
            "name": ticker,
            "ticker": ticker,
            "market": "KR" if is_korean(ticker) else "US",
            "current_price": 0,
            "currency": "KRW" if is_korean(ticker) else "USD",
            "last_updated": TODAY
        }
        failed.append(ticker)
        print(f"  [{i+1}/{total}] {ticker} FAILED: {err}")
    
    # Progress report every 20
    if (i + 1) % 20 == 0:
        pct = round((i+1)/total*100)
        print(f"PROGRESS: {i+1}/{total} ({pct}%)")
    
    # Rate limiting
    time.sleep(2)
    if (i + 1) % 20 == 0:
        print("  Batch pause 10s...")
        time.sleep(10)

# Step 3: Save
with open(PRICES_FILE, "w", encoding="utf-8") as f:
    json.dump(prices, f, ensure_ascii=False, indent=2)

print(f"\n=== DONE ===")
print(f"Success: {success}")
print(f"Failed: {len(failed)}")
if failed:
    print(f"Failed tickers: {failed}")
print(f"Total in file: {len(prices)}")
