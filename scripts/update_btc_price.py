"""BTC/ETH/SOL/DOGE 현재가 CoinGecko에서 가져와 signal_prices.json 업데이트 + 수익률 재계산"""
import json, urllib.request, re, shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent
SIGNAL_PRICES = BASE / 'data' / 'signal_prices.json'
PUBLIC_DEST = BASE / 'public' / 'signal_prices.json'
OUT_DEST = BASE / 'out' / 'signal_prices.json'

# 1. CoinGecko 현재가
url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,dogecoin,ripple&vs_currencies=usd'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
with urllib.request.urlopen(req, timeout=15) as resp:
    cg = json.loads(resp.read())

CRYPTO_MAP = {
    'BTC':  cg['bitcoin']['usd'],
    'ETH':  cg['ethereum']['usd'],
    'SOL':  cg['solana']['usd'],
    'DOGE': cg['dogecoin']['usd'],
}
today = datetime.now().strftime('%Y-%m-%d')
print("현재가:")
for k, v in CRYPTO_MAP.items():
    print(f"  {k}: ${v:,.2f}")

# 2. signal_prices.json 로드
with open(SIGNAL_PRICES, encoding='utf-8') as f:
    data = json.load(f)

updated_count = 0

# 3. 티커 키 업데이트 (BTC, ETH, SOL, DOGE, BTC-USD 등)
TICKER_NAMES = {'BTC': '비트코인 (BTC)', 'ETH': '이더리움 (ETH)', 'SOL': '솔라나 (SOL)', 'DOGE': '도지코인 (DOGE)'}
for ticker, price in CRYPTO_MAP.items():
    if ticker in data and isinstance(data[ticker], dict) and 'current_price' in data[ticker]:
        old = data[ticker]['current_price']
        data[ticker]['current_price'] = round(price, 4)
        data[ticker]['last_updated'] = today
        print(f"  [{ticker}] 티커키 업데이트: ${old} -> ${price:,.2f}")
        updated_count += 1
    # yfinance 형식 키 (BTC-USD)
    yf_key = f'{ticker}-USD'
    if yf_key in data and isinstance(data[yf_key], dict):
        data[yf_key]['current_price'] = round(price, 4)
        data[yf_key]['last_updated'] = today

# 4. UUID 시그널 수익률 재계산
uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
recalc_count = 0
for key, val in data.items():
    if not uuid_pattern.match(key):
        continue
    if not isinstance(val, dict):
        continue
    ticker = val.get('ticker', '')
    if ticker not in CRYPTO_MAP:
        continue
    new_price = CRYPTO_MAP[ticker]
    old_return = val.get('return_pct')
    price_at = val.get('price_at_signal')
    if price_at and price_at > 0:
        new_return = round((new_price - price_at) / price_at * 100, 2)
        data[key]['price_current'] = round(new_price, 4)
        data[key]['return_pct'] = new_return
        print(f"  [{ticker}] UUID {key[:8]}... 수익률: {old_return}% -> {new_return}%  (진입가: ${price_at:,.2f}, 현재: ${new_price:,.2f})")
        recalc_count += 1

print(f"\n총 업데이트: 티커 {updated_count}개, 수익률 {recalc_count}개")

# 5. 저장
with open(SIGNAL_PRICES, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

shutil.copy2(SIGNAL_PRICES, PUBLIC_DEST)
if OUT_DEST.exists():
    shutil.copy2(SIGNAL_PRICES, OUT_DEST)

print("data/ + public/ + out/ 저장 완료")
