import sys
sys.stdout.reconfigure(encoding='utf-8')
import json, time
import yfinance as yf

sp = json.load(open('data/stockPrices.json', 'r', encoding='utf-8'))

print(f"Total tickers: {len(sp)}")

# Classify tickers
coins = ['BTC', 'ETH', 'DOGE', 'SOL', 'KLAY']
indices = ['KS11', 'SOXX']

success = 0
fail = 0

for ticker in sorted(sp.keys()):
    # Determine yfinance symbol
    if ticker in coins:
        # Coins use -USD suffix
        yf_symbol = ticker + '-USD'
    elif ticker in indices:
        if ticker == 'KS11':
            yf_symbol = '^KS11'
        else:
            yf_symbol = ticker
    elif ticker.isdigit() and len(ticker) == 6:
        yf_symbol = ticker + '.KS'
    else:
        yf_symbol = ticker
    
    try:
        t = yf.Ticker(yf_symbol)
        hist = t.history(period='5y')
        if hist.empty:
            # Try max period
            hist = t.history(period='max')
        
        if hist.empty:
            print(f"  SKIP {ticker} ({yf_symbol}) - no data")
            fail += 1
            continue
        
        prices = []
        for date, row in hist.iterrows():
            prices.append({
                'date': date.strftime('%Y-%m-%d'),
                'close': round(float(row['Close']), 2),
                'volume': int(row['Volume'])
            })
        
        old_count = len(sp[ticker].get('prices', []))
        sp[ticker]['prices'] = prices
        sp[ticker]['currentPrice'] = prices[-1]['close']
        if len(prices) > 1:
            sp[ticker]['change'] = round(prices[-1]['close'] - prices[-2]['close'], 2)
            sp[ticker]['changePercent'] = round((prices[-1]['close'] - prices[-2]['close']) / prices[-2]['close'] * 100, 2)
        
        print(f"  OK {ticker} ({yf_symbol}): {old_count} -> {len(prices)} days")
        success += 1
        time.sleep(0.3)
    except Exception as e:
        print(f"  ERROR {ticker}: {e}")
        fail += 1

json.dump(sp, open('data/stockPrices.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"\nDone! Success={success}, Fail={fail}")
