import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests, json

key = open('.env.local').readlines()[2].split('=',1)[1].strip()
h = {'apikey': key, 'Authorization': 'Bearer ' + key}
r = requests.get('https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals?select=id,stock,ticker,signal', headers=h)
signals = r.json()

# All unique tickers from DB
db_tickers = {}
null_tickers = []
for s in signals:
    if s['ticker'] and s['ticker'].strip():
        if s['ticker'] not in db_tickers:
            db_tickers[s['ticker']] = s['stock']
    else:
        null_tickers.append(s)

# Load stockPrices.json
sp = json.load(open('data/stockPrices.json', 'r', encoding='utf-8'))
# Load signal_prices.json
sigp = json.load(open('data/signal_prices.json', 'r', encoding='utf-8'))

print(f"=== DB 시그널 현황 ===")
print(f"Total signals: {len(signals)}")
print(f"Unique tickers: {len(db_tickers)}")
print(f"Null ticker signals: {len(null_tickers)}")

print(f"\n=== stockPrices.json ===")
print(f"Total entries: {len(sp)}")
has_prices = [k for k,v in sp.items() if v.get('prices') and len(v['prices']) > 0]
no_prices = [k for k,v in sp.items() if not v.get('prices') or len(v['prices']) == 0]
print(f"With price history: {len(has_prices)}")
print(f"Without price history: {len(no_prices)}")
if no_prices:
    print(f"  Missing prices: {no_prices}")

print(f"\n=== ticker 있는데 stockPrices.json에 없는 종목 ===")
missing_sp = []
for ticker, stock in sorted(db_tickers.items()):
    if ticker not in sp:
        in_sigp = '✅' if stock in sigp or ticker in sigp else '❌'
        missing_sp.append((ticker, stock, in_sigp))
        print(f"  {ticker} ({stock}) | signal_prices: {in_sigp}")
print(f"Total missing from stockPrices: {len(missing_sp)}")

print(f"\n=== signal_prices.json에서 price null인 종목 ===")
for name, v in sorted(sigp.items()):
    if v.get('current_price') is None:
        print(f"  {name} | ticker={v.get('ticker','?')}")

print(f"\n=== ticker가 null인 시그널 ===")
for s in null_tickers:
    print(f"  [{s['id'][:8]}] {s['stock']} | signal={s['signal']}")

# Classify missing tickers
print(f"\n=== 분류 ===")
coins = ['BTC', 'ETH', 'DOGE', 'SOL', 'KLAY']
kr_pattern = lambda t: t.isdigit() and len(t) == 6
for ticker, stock, _ in missing_sp:
    if ticker in coins:
        cat = 'COIN'
    elif kr_pattern(ticker):
        cat = 'KR'
    else:
        cat = 'US'
    print(f"  {cat}: {ticker} ({stock})")
