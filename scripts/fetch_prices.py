import yfinance as yf
import json

stocks = {
    '005930': '005930.KS',  # 삼성전자
    '000660': '000660.KS',  # SK하이닉스
}

result = {}
for code, ticker in stocks.items():
    t = yf.Ticker(ticker)
    h = t.history(period='5y')
    prices = []
    for date, row in h.iterrows():
        prices.append({
            'date': date.strftime('%Y-%m-%d'),
            'close': int(row['Close'])
        })
    current = prices[-1]['close'] if prices else 0
    result[code] = {
        'currentPrice': current,
        'prices': prices
    }
    print(f"{code}: {len(prices)} days, current={current}")

with open('data/stockPrices.json', 'w') as f:
    json.dump(result, f)
print("Done")
