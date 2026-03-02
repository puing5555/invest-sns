import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import yfinance as yf

sp = json.load(open('data/stockPrices.json', 'r', encoding='utf-8'))

if 'GLD' not in sp:
    sp['GLD'] = {'name': 'SPDR Gold Shares', 'ticker': 'GLD', 'market': 'US', 'currency': 'USD'}

t = yf.Ticker('GLD')
hist = t.history(period='5y')
prices = [{'date': d.strftime('%Y-%m-%d'), 'close': round(float(r['Close']), 2), 'volume': int(r['Volume'])} for d, r in hist.iterrows()]
sp['GLD']['prices'] = prices
sp['GLD']['currentPrice'] = prices[-1]['close']
sp['GLD']['change'] = round(prices[-1]['close'] - prices[-2]['close'], 2)
sp['GLD']['changePercent'] = round((prices[-1]['close'] - prices[-2]['close']) / prices[-2]['close'] * 100, 2)
json.dump(sp, open('data/stockPrices.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"GLD: {len(prices)} days, latest ${prices[-1]['close']}")
print(f"Total tickers: {len(sp)}")
