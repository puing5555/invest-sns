#!/usr/bin/env python3
"""PENGU 수익률 계산 및 signal_prices.json 추가"""
import json
from pathlib import Path
from datetime import datetime

base = Path(__file__).parent.parent / 'data'

# stockPrices.json에서 PENGU 차트 데이터
sp = json.loads((base / 'stockPrices.json').read_text(encoding='utf-8'))
pengu = sp.get('PENGU', {})
prices = pengu.get('prices', [])
print(f"PENGU 가격 데이터: {len(prices)}개")

signal_date = '2025-09-08'
signal_price = None
for p in prices:
    if p['date'] == signal_date:
        signal_price = p['close']
        break

if signal_price is None:
    t = datetime.strptime(signal_date, '%Y-%m-%d').timestamp()
    closest = min(prices, key=lambda p: abs(datetime.strptime(p['date'], '%Y-%m-%d').timestamp() - t))
    signal_price = closest['close']
    print(f"가장 가까운 날짜 {closest['date']} 가격: {signal_price}")
else:
    print(f"2025-09-08 가격: {signal_price}")

current_price = pengu['currentPrice']
return_pct = round((current_price - signal_price) / signal_price * 100, 2)
print(f"현재가: {current_price} KRW")
print(f"수익률: {return_pct}%")

# signal_prices.json 업데이트
sp_path = base / 'signal_prices.json'
sp_data = json.loads(sp_path.read_text(encoding='utf-8'))

# UUID 키 (시그널 수익률)
signal_id = 'adce5070-6e7b-4926-b42d-37062071e709'
sp_data[signal_id] = {
    'price_at_signal': round(signal_price, 6),
    'price_current': round(current_price, 6),
    'return_pct': return_pct,
    'signal_date': signal_date,
    'ticker': 'PENGU',
    'market': 'CRYPTO',
    'currency': 'KRW'
}

# 티커 키 (현재가)
sp_data['PENGU'] = {
    'name': '퍼지펭귄',
    'ticker': 'PENGU',
    'market': 'CRYPTO',
    'current_price': round(current_price, 6),
    'currency': 'KRW',
    'last_updated': '2026-03-12',
    'source': 'coingecko'
}

sp_path.write_text(json.dumps(sp_data, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"signal_prices.json 업데이트 완료 (총 {len(sp_data)}개)")

# public/ 과 out/ 에도 동기
for dest_dir in ['public', 'out']:
    dest = Path(__file__).parent.parent / dest_dir / 'signal_prices.json'
    if dest.exists():
        dest.write_text(json.dumps(sp_data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"  {dest_dir}/signal_prices.json 동기화 완료")

print("\n=== PENGU 수익률 설정 완료 ===")
print(f"  진입가: {signal_price:.6f} KRW (2025-09-08)")
print(f"  현재가: {current_price:.6f} KRW")
print(f"  수익률: {return_pct}%")
