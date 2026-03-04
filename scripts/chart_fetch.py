"""Fetch historical price data for all tickers missing from stockPrices.json"""
import json, time, re, sys
sys.stdout.reconfigure(encoding='utf-8')
import yfinance as yf

STOCK_PRICES_PATH = r'C:\Users\Mario\work\invest-sns\data\stockPrices.json'
SIGNAL_PRICES_PATH = r'C:\Users\Mario\work\invest-sns\data\signal_prices.json'

with open(STOCK_PRICES_PATH, 'r', encoding='utf-8') as f:
    stock_prices = json.load(f)
with open(SIGNAL_PRICES_PATH, 'r', encoding='utf-8') as f:
    signal_prices = json.load(f)

missing = [k for k in signal_prices if k not in stock_prices]
print(f"Missing from stockPrices: {len(missing)}")

def get_yf_symbol(ticker, market):
    if market == 'KR':
        return [f"{ticker}.KS", f"{ticker}.KQ"]
    elif ticker == 'IXIC':
        return ['^IXIC']
    elif ticker == 'KS11':
        return ['^KS11']
    elif ticker == 'BRK.A':
        return ['BRK-A']
    elif ticker.endswith('.HK'):
        return [ticker]
    elif market == 'HK':
        return [f"{ticker}.HK"]
    elif market in ('CRYPTO', 'CRYPTO_DEFI'):
        return [f"{ticker}-USD"]
    else:
        return [ticker]

added = 0
failed = []

for i, ticker in enumerate(missing):
    info = signal_prices[ticker]
    market = info.get('market', '')
    name = info.get('name', ticker)
    symbols = get_yf_symbol(ticker, market)
    
    fetched = False
    for sym in symbols:
        try:
            d = yf.Ticker(sym)
            h = d.history(period='3mo')  # 3 months of data
            if not h.empty and len(h) > 5:
                prices_list = []
                for date, row in h.iterrows():
                    prices_list.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'close': round(float(row['Close']), 2),
                        'volume': int(row['Volume']) if row['Volume'] > 0 else 0
                    })
                
                stock_prices[ticker] = {
                    'name': name,
                    'ticker': ticker,
                    'prices': prices_list
                }
                added += 1
                fetched = True
                print(f"[{i+1}/{len(missing)}] OK {ticker} ({name}): {len(prices_list)} days")
                break
        except Exception as e:
            continue
    
    if not fetched:
        failed.append((ticker, name))
        print(f"[{i+1}/{len(missing)}] FAIL {ticker} ({name})")
    
    if (i + 1) % 10 == 0:
        time.sleep(2)

# Save
with open(STOCK_PRICES_PATH, 'w', encoding='utf-8') as f:
    json.dump(stock_prices, f, ensure_ascii=False, indent=2)

print(f"\n=== DONE ===")
print(f"Added: {added}")
print(f"Failed: {len(failed)}")
for t, n in failed:
    print(f"  {t}: {n}")
print(f"Total in stockPrices.json: {len(stock_prices)}")
