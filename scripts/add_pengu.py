#!/usr/bin/env python3
"""
퍼지 펭귄(PENGU) 크립토 설정:
1. stockPrices.json에 PENGU 가격 데이터 추가
2. DB market KR → CRYPTO 수정
3. DB influencer_signals return_pct 계산
"""
import json, urllib.request, os, time
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv('.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
ANON_KEY = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')

KEY = SERVICE_ROLE_KEY or ANON_KEY

HEADERS = {
    'apikey': KEY,
    'Authorization': f'Bearer {KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def coingecko_chart(cg_id, days=365):
    url = f'https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart?vs_currency=krw&days={days}&interval=daily'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

# ── 1. CoinGecko에서 PENGU 데이터 수집 ──────────────────────────────────────
print("=== STEP 1: CoinGecko PENGU 365일 데이터 수집 ===")
data = coingecko_chart('pudgy-penguins', 365)
prices = data.get('prices', [])
print(f"총 {len(prices)}개 데이터 포인트")

# 포맷 변환: [{date, close}, ...]
price_records = []
for ts, price in prices:
    dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    price_records.append({
        'date': dt.strftime('%Y-%m-%d'),
        'close': round(price, 6)
    })

current_price = price_records[-1]['close'] if price_records else 0
prev_price = price_records[-2]['close'] if len(price_records) >= 2 else current_price
change = round(current_price - prev_price, 6)
change_pct = round((change / prev_price * 100) if prev_price else 0, 2)

print(f"현재가(KRW): {current_price}")
print(f"전일대비: {change} ({change_pct}%)")

# ── 2. stockPrices.json에 PENGU 추가 ──────────────────────────────────────
print("\n=== STEP 2: stockPrices.json 업데이트 ===")
prices_file = Path(__file__).parent.parent / 'data' / 'stockPrices.json'
stock_data = json.loads(prices_file.read_text(encoding='utf-8'))

stock_data['PENGU'] = {
    'currentPrice': current_price,
    'change': change,
    'changePercent': change_pct,
    'currency': 'KRW',
    'market': 'CRYPTO',
    'name': '퍼지펭귄',
    'prices': price_records
}

prices_file.write_text(json.dumps(stock_data, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"PENGU 추가 완료. stockPrices.json 총 {len(stock_data)}개 종목")

# ── 3. DB market 수정 (KR → CRYPTO) ──────────────────────────────────────
print("\n=== STEP 3: DB market KR → CRYPTO 수정 ===")

import urllib.parse

# 먼저 PENGU 시그널 확인
url = f"{SUPABASE_URL}/rest/v1/influencer_signals?ticker=eq.PENGU&select=id,stock,ticker,market,signal,created_at"
req = urllib.request.Request(url, headers=HEADERS)
with urllib.request.urlopen(req) as resp:
    signals = json.loads(resp.read())
    print(f"PENGU 시그널 {len(signals)}개:")
    for s in signals:
        print(f"  id={s['id']}, market={s['market']}, signal={s['signal']}")

# market 업데이트
if signals:
    update_url = f"{SUPABASE_URL}/rest/v1/influencer_signals?ticker=eq.PENGU"
    update_data = json.dumps({'market': 'CRYPTO'}).encode('utf-8')
    req = urllib.request.Request(update_url, data=update_data, method='PATCH', headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print(f"market 업데이트 완료: {len(result)}개")

# ── 4. 수익률 계산 및 DB 저장 ──────────────────────────────────────────────
print("\n=== STEP 4: 수익률 계산 ===")

# 시그널 created_at에서 날짜 추출
for signal in signals:
    created_at = signal['created_at'][:10]  # YYYY-MM-DD
    
    # 시그널 날짜 가격 찾기
    signal_price = None
    for pr in price_records:
        if pr['date'] == created_at:
            signal_price = pr['close']
            break
    
    # 정확한 날짜 없으면 가장 가까운 날짜
    if signal_price is None:
        target_ts = datetime.strptime(created_at, '%Y-%m-%d').timestamp() * 1000
        closest_ts = min([(abs(datetime.strptime(pr['date'], '%Y-%m-%d').timestamp()*1000 - target_ts), pr) for pr in price_records], key=lambda x: x[0])
        signal_price = closest_ts[1]['close']
        print(f"  {created_at} → 가장 가까운 날짜 {closest_ts[1]['date']} 가격: {signal_price}")
    else:
        print(f"  {created_at} 가격: {signal_price}")
    
    if signal_price and signal_price > 0:
        return_pct = round((current_price - signal_price) / signal_price * 100, 2)
        print(f"  수익률: {return_pct}% (진입 {signal_price} → 현재 {current_price})")
        
        # DB signal_returns 테이블이 있으면 저장 (없을 수 있음)
        # 일단 콘솔에 출력만
        print(f"  → DB signal_returns UPDATE 필요: signal_id={signal['id']}, return_pct={return_pct}")

print("\n=== 완료 ===")
print(f"PENGU(퍼지펭귄) 크립토 연동 완료!")
print(f"현재가: {current_price} KRW")
print(f"chart 데이터: {len(price_records)}일")
