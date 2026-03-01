import yfinance as yf
import json

stocks = {
    '005930': '005930.KS',
    '000660': '000660.KS',
    '086520': '086520.KS',
    '009540': '009540.KS',
    '399720': '399720.KS',
}

result = {}
for code, ticker in stocks.items():
    try:
        t = yf.Ticker(ticker)
        h = t.history(period='5y')
        if len(h) < 2:
            print(f"{code}: not enough data ({len(h)} rows)")
            continue
        prices = []
        for date, row in h.iterrows():
            prices.append({
                'date': date.strftime('%Y-%m-%d'),
                'close': int(row['Close'])
            })
        current = prices[-1]['close']
        prev = prices[-2]['close']
        change = current - prev
        change_pct = round((change / prev) * 100, 2) if prev else 0
        result[code] = {
            'currentPrice': current,
            'change': change,
            'changePercent': change_pct,
            'prices': prices
        }
        print(f"{code}: {len(prices)} days, current={current}, change={change} ({change_pct}%)")
    except Exception as e:
        print(f"{code}: error - {e}")

with open('data/stockPrices.json', 'w') as f:
    json.dump(result, f)
print("Done")
