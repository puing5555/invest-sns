#!/usr/bin/env python3
"""Fetch latest prices for all tickers in Supabase influencer_signals table."""
import json, os, requests, yfinance as yf
from datetime import datetime

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

print("Fetching tickers from Supabase...")
all_signals = []
offset = 0
while True:
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/influencer_signals?select=ticker,stock,market&offset={offset}&limit=1000",
        headers=headers
    )
    data = r.json()
    if not data:
        break
    all_signals.extend(data)
    if len(data) < 1000:
        break
    offset += 1000

# Deduplicate by ticker
ticker_map = {}
for s in all_signals:
    t = s.get('ticker', '')
    if t and t not in ticker_map:
        ticker_map[t] = {'name': s.get('stock', ''), 'market': s.get('market', 'KR')}

print(f"Found {len(ticker_map)} unique tickers from {len(all_signals)} signals")

# Load existing prices
prices_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'signal_prices.json')
try:
    with open(prices_path, 'r', encoding='utf-8') as f:
        existing = json.load(f)
except:
    existing = {}

def get_yf_symbol(ticker, market):
    market = (market or '').upper()
    if market == 'CRYPTO' or '-USD' in ticker:
        return ticker if '-USD' in ticker else f"{ticker}-USD"
    if market in ('KR', '') and ticker.isdigit():
        return f"{ticker.zfill(6)}.KS"
    if market == 'HK':
        return f"{ticker.zfill(4)}.HK"
    if market == 'DE':
        return f"{ticker}.DE"
    return ticker

today = datetime.now().strftime('%Y-%m-%d')
result = {}
failed = []
tickers_list = list(ticker_map.items())
batch_size = 50

for i in range(0, len(tickers_list), batch_size):
    batch = tickers_list[i:i+batch_size]
    symbols = {}
    for ticker, info in batch:
        sym = get_yf_symbol(ticker, info['market'])
        symbols[sym] = (ticker, info)
    
    sym_str = ' '.join(symbols.keys())
    print(f"Batch {i//batch_size + 1}/{(len(tickers_list)-1)//batch_size + 1}: {len(symbols)} tickers...")
    
    try:
        data = yf.download(sym_str, period='5d', progress=False, threads=True)
        
        for sym, (ticker, info) in symbols.items():
            price = 0
            market = (info['market'] or 'KR').upper()
            currency = 'KRW' if market == 'KR' and ticker.isdigit() else 'USD'
            if market == 'HK': currency = 'HKD'
            if market == 'DE': currency = 'EUR'
            if market == 'CRYPTO' or '-USD' in ticker: currency = 'USD'
            
            try:
                if len(symbols) == 1:
                    close = data['Close']
                else:
                    close = data['Close'][sym] if sym in data['Close'].columns else None
                if close is not None and len(close.dropna()) > 0:
                    price = float(close.dropna().iloc[-1])
                    if price != price: price = 0
            except:
                pass
            
            if price == 0 and ticker in existing and existing[ticker].get('current_price', 0) > 0:
                price = existing[ticker]['current_price']
                currency = existing[ticker].get('currency', currency)
            
            if price == 0:
                failed.append(ticker)
            
            result[ticker] = {
                'name': info['name'] or existing.get(ticker, {}).get('name', ticker),
                'ticker': ticker,
                'market': info['market'] or 'KR',
                'current_price': round(price, 2) if currency != 'KRW' else int(price),
                'currency': currency,
                'last_updated': today
            }
    except Exception as e:
        print(f"Batch error: {e}")
        for sym, (ticker, info) in symbols.items():
            if ticker in existing:
                result[ticker] = existing[ticker]
                result[ticker]['last_updated'] = today
            else:
                result[ticker] = {
                    'name': info['name'] or ticker, 'ticker': ticker,
                    'market': info['market'] or 'KR', 'current_price': 0,
                    'currency': 'KRW', 'last_updated': today
                }
            failed.append(ticker)

result = dict(sorted(result.items()))
with open(prices_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\nDone! {len(result)} tickers saved")
print(f"Failed: {len(failed)} tickers")
if failed:
    print(f"Failed: {failed[:30]}{'...' if len(failed)>30 else ''}")
