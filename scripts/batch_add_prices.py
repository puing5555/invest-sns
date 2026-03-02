import sys
sys.stdout.reconfigure(encoding='utf-8')
import json, time

# Korean stocks need .KS suffix for yfinance
kr_tickers = [
    '000720','004170','005380','005940','006400','016360','035420',
    '036570','036930','039490','042700','051910','071050','079160',
    '084370','090430','095610','240810','267260','284620','298040',
    '352820','357780','403870'
]
us_tickers = ['GOOG']

import yfinance as yf

sp = json.load(open('data/stockPrices.json', 'r', encoding='utf-8'))

def add_ticker(ticker, yf_ticker, market):
    try:
        t = yf.Ticker(yf_ticker)
        hist = t.history(period='3mo')
        if hist.empty:
            print(f"  SKIP {ticker} ({yf_ticker}) - no data")
            return False
        prices = []
        for date, row in hist.iterrows():
            prices.append({
                'date': date.strftime('%Y-%m-%d'),
                'close': round(float(row['Close']), 2),
                'volume': int(row['Volume'])
            })
        info = t.info
        name = info.get('shortName', ticker)
        currency = 'KRW' if market == 'KR' else 'USD'
        
        sp[ticker] = {
            'name': name,
            'ticker': ticker,
            'market': market,
            'currentPrice': prices[-1]['close'],
            'change': round(prices[-1]['close'] - prices[-2]['close'], 2) if len(prices) > 1 else 0,
            'changePercent': round((prices[-1]['close'] - prices[-2]['close']) / prices[-2]['close'] * 100, 2) if len(prices) > 1 else 0,
            'currency': currency,
            'prices': prices
        }
        print(f"  OK {ticker} ({name}) - {len(prices)} days, latest {prices[-1]['close']} {currency}")
        return True
    except Exception as e:
        print(f"  ERROR {ticker}: {e}")
        return False

print("=== Korean Stocks ===")
ok = 0
fail = 0
for t in kr_tickers:
    result = add_ticker(t, t + '.KS', 'KR')
    if result:
        ok += 1
    else:
        fail += 1
    time.sleep(0.5)

print("\n=== US Stocks ===")
for t in us_tickers:
    result = add_ticker(t, t, 'US')
    if result:
        ok += 1
    else:
        fail += 1
    time.sleep(0.5)

# Save
json.dump(sp, open('data/stockPrices.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"\nDone! OK={ok}, FAIL={fail}, Total entries={len(sp)}")
