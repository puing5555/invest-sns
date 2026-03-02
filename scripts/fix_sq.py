import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import yfinance as yf

sp = json.load(open('data/stockPrices.json', 'r', encoding='utf-8'))
t = yf.Ticker('XYZ')
hist = t.history(period='5y')
prices = [{'date': d.strftime('%Y-%m-%d'), 'close': round(float(r['Close']), 2), 'volume': int(r['Volume'])} for d, r in hist.iterrows()]
sp['SQ']['prices'] = prices
sp['SQ']['currentPrice'] = prices[-1]['close']
sp['SQ']['change'] = round(prices[-1]['close'] - prices[-2]['close'], 2)
sp['SQ']['changePercent'] = round((prices[-1]['close'] - prices[-2]['close']) / prices[-2]['close'] * 100, 2)
json.dump(sp, open('data/stockPrices.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
last = prices[-1]['close']
print(f"SQ(XYZ): {len(prices)} days, latest ${last}")
