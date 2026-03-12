#!/usr/bin/env python3
"""유니스왑(UNI) 크립토 차트 + 수익률 추가"""
import json, urllib.request
from pathlib import Path
from datetime import datetime, timezone

base = Path(__file__).parent.parent / 'data'

# CoinGecko UNI 365일 KRW 데이터
print("=== CoinGecko UNI 데이터 수집 ===")
url = 'https://api.coingecko.com/api/v3/coins/uniswap/market_chart?vs_currency=krw&days=365&interval=daily'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read())

prices = data.get('prices', [])
print(f"데이터 포인트: {len(prices)}개")

price_records = []
for ts, price in prices:
    dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    price_records.append({'date': dt.strftime('%Y-%m-%d'), 'close': round(price, 4)})

current_price = price_records[-1]['close']
prev_price = price_records[-2]['close'] if len(price_records) >= 2 else current_price
change = round(current_price - prev_price, 4)
change_pct = round((change / prev_price * 100) if prev_price else 0, 2)
print(f"현재가(KRW): {current_price}")
print(f"전일대비: {change} ({change_pct}%)")

# stockPrices.json 업데이트
sp_path = base / 'stockPrices.json'
sp = json.loads(sp_path.read_text(encoding='utf-8'))
sp['UNI'] = {
    'currentPrice': current_price,
    'change': change,
    'changePercent': change_pct,
    'currency': 'KRW',
    'market': 'CRYPTO',
    'name': '유니스왑',
    'prices': price_records
}
sp_path.write_text(json.dumps(sp, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"stockPrices.json 업데이트 완료 (총 {len(sp)}개)")

# 수익률 계산 (영상 날짜: 2025-08-16)
signal_date = '2025-08-16'
signal_price = None
for p in price_records:
    if p['date'] == signal_date:
        signal_price = p['close']
        break
if signal_price is None:
    t = datetime.strptime(signal_date, '%Y-%m-%d').timestamp()
    closest = min(price_records, key=lambda p: abs(datetime.strptime(p['date'], '%Y-%m-%d').timestamp() - t))
    signal_price = closest['close']
    print(f"가장 가까운 날짜 {closest['date']} 가격: {signal_price}")
else:
    print(f"2025-08-16 가격: {signal_price}")

return_pct = round((current_price - signal_price) / signal_price * 100, 2)
print(f"수익률: {return_pct}% ({signal_price} → {current_price})")

# signal_prices.json 업데이트
spp_path = base / 'signal_prices.json'
spp = json.loads(spp_path.read_text(encoding='utf-8'))
signal_id = 'ccc172c2-e8fd-4f18-9d0b-84c1d54fedc7'
spp[signal_id] = {
    'price_at_signal': round(signal_price, 4),
    'price_current': round(current_price, 4),
    'return_pct': return_pct,
    'signal_date': signal_date,
    'ticker': 'UNI',
    'market': 'CRYPTO',
    'currency': 'KRW'
}
spp['UNI'] = {
    'name': '유니스왑',
    'ticker': 'UNI',
    'market': 'CRYPTO',
    'current_price': round(current_price, 4),
    'currency': 'KRW',
    'last_updated': '2026-03-12',
    'source': 'coingecko'
}
spp_path.write_text(json.dumps(spp, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"signal_prices.json 업데이트 완료")

# public/out 동기화
for dest_dir in ['public', 'out']:
    for fname in ['stockPrices.json', 'signal_prices.json']:
        src = base / fname
        dst = Path(__file__).parent.parent / dest_dir / fname
        if dst.exists():
            dst.write_bytes(src.read_bytes())
            print(f"  {dest_dir}/{fname} 동기화")

print(f"\n=== UNI 완료 ===")
print(f"  진입가: {signal_price} KRW (2025-08-16)")
print(f"  현재가: {current_price} KRW")
print(f"  수익률: {return_pct}%")
