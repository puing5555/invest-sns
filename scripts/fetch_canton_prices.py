"""Canton (CC) 가격 히스토리를 CoinGecko에서 가져와 stockPrices.json에 추가"""
import json, urllib.request, time
from datetime import datetime
from pathlib import Path

STOCK_PRICES_PATH = Path(__file__).parent.parent / 'data' / 'stockPrices.json'

def fetch_canton_history():
    url = 'https://api.coingecko.com/api/v3/coins/canton-network/market_chart?vs_currency=usd&days=180&interval=daily'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.loads(r.read())
    return d['prices']  # [[timestamp_ms, price], ...]

def fetch_canton_current():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=canton-network&vs_currencies=usd&include_24hr_change=true'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        d = json.loads(r.read())
    return d.get('canton-network', {})

print('Canton (CC) 가격 데이터 수집 중...')
prices_raw = fetch_canton_history()
time.sleep(2)
current = fetch_canton_current()

# 날짜 형식 변환
prices_formatted = []
seen_dates = set()
for ts_ms, price in prices_raw:
    date_str = datetime.utcfromtimestamp(ts_ms / 1000).strftime('%Y-%m-%d')
    if date_str not in seen_dates:
        prices_formatted.append({'date': date_str, 'close': round(price, 6)})
        seen_dates.add(date_str)

current_price = current.get('usd', 0)
change_pct = current.get('usd_24h_change', 0)

print('가격 데이터 수: %d개' % len(prices_formatted))
print('최신 가격: $%.4f' % current_price)
print('24h 변화율: %.2f%%' % change_pct)

# stockPrices.json에 추가
with open(STOCK_PRICES_PATH, encoding='utf-8') as f:
    stock_data = json.load(f)

stock_data['CNTN'] = {
    'name': '캔톤 (CC)',
    'ticker': 'CNTN',
    'currentPrice': round(current_price, 6),
    'change': round(current_price * change_pct / 100, 6),
    'changePercent': round(change_pct, 2),
    'prices': prices_formatted
}

with open(STOCK_PRICES_PATH, 'w', encoding='utf-8') as f:
    json.dump(stock_data, f, ensure_ascii=False, separators=(',', ':'))

print('stockPrices.json CNTN 추가 완료')
