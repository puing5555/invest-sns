"""
update_btc_price.py -- 크립토 현재가 업데이트 + 수익률 재계산
================================================================
개선사항 (2026-03-12):
  - price_utils.py 사용 (yfinance -> CoinGecko -> Binance 폴백)
  - last_updated 신선도 검증 (6시간 이내 캐시는 재사용)
  - 스테일 데이터 사용 방지
"""
import json, re, shutil, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils.price_utils import get_crypto_price

BASE = Path(__file__).parent.parent
SIGNAL_PRICES = BASE / 'data' / 'signal_prices.json'
PUBLIC_DEST   = BASE / 'public' / 'signal_prices.json'
OUT_DEST      = BASE / 'out' / 'signal_prices.json'

CRYPTO_TARGETS = [
    {'ticker': 'BTC',  'yf_symbol': 'BTC-USD'},
    {'ticker': 'ETH',  'yf_symbol': 'ETH-USD'},
    {'ticker': 'SOL',  'yf_symbol': 'SOL-USD'},
    {'ticker': 'DOGE', 'yf_symbol': 'DOGE-USD'},
    {'ticker': 'XRP',  'yf_symbol': 'XRP-USD'},
    {'ticker': 'CNTN', 'yf_symbol': 'CNTN-USD'},
]

# DB ticker -> signal_prices.json ticker 매핑
TICKER_ALIAS = {
    'CNTN-USD': 'CNTN',
    'BTC-USD': 'BTC',
    'ETH-USD': 'ETH',
    'SOL-USD': 'SOL',
    'DOGE-USD': 'DOGE',
    'XRP-USD': 'XRP',
}

# 1. 로드
with open(SIGNAL_PRICES, encoding='utf-8') as f:
    data = json.load(f)

today = datetime.now().strftime('%Y-%m-%d')
updated_prices = {}
failed_tickers = []

# 2. 현재가 조회
print("=== 크립토 현재가 조회 ===")
for target in CRYPTO_TARGETS:
    ticker = target['ticker']
    yf_sym = target['yf_symbol']
    cached = data.get(ticker) or data.get(yf_sym)
    result = get_crypto_price(ticker, yf_symbol=yf_sym, max_age_hours=6, cached_entry=cached)

    if result['price']:
        updated_prices[ticker] = result['price']
        for key in [ticker, yf_sym]:
            if key in data and isinstance(data[key], dict):
                data[key]['current_price'] = result['price']
                data[key]['last_updated']  = today
                data[key]['price_source']  = result['source']
    else:
        failed_tickers.append(ticker)
        print("  [WARN] %s 가격 없음 -> 기존 값 유지" % ticker)

if failed_tickers:
    print("\n[WARN] 조회 실패 티커: %s" % failed_tickers)

# 3. UUID 수익률 재계산
print("\n=== UUID 수익률 재계산 ===")
uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
recalc_count = 0

for key, val in data.items():
    if not uuid_pattern.match(key):
        continue
    if not isinstance(val, dict):
        continue
    raw_ticker = val.get('ticker', '')
    # DB에 CNTN-USD 등으로 저장된 것도 처리
    ticker = TICKER_ALIAS.get(raw_ticker, raw_ticker)
    if ticker not in updated_prices:
        continue
    new_price = updated_prices[ticker]
    price_at  = val.get('price_at_signal')
    if price_at and price_at > 0:
        new_return = round((new_price - price_at) / price_at * 100, 2)
        old_return = val.get('return_pct')
        data[key]['price_current'] = round(new_price, 4)
        data[key]['return_pct']    = new_return
        print("  [%s] %s... %s%% -> %s%%" % (ticker, key[:8], old_return, new_return))
        recalc_count += 1

# 4. 저장
with open(SIGNAL_PRICES, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

shutil.copy2(SIGNAL_PRICES, PUBLIC_DEST)
if OUT_DEST.exists():
    shutil.copy2(SIGNAL_PRICES, OUT_DEST)

print("\n[OK] 완료: 가격 %d개, 수익률 %d개" % (len(updated_prices), recalc_count))
if failed_tickers:
    print("[WARN] 실패 티커: %s -- 수동 확인 필요" % failed_tickers)
