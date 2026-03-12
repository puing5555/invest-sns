"""
CNTN-USD 시그널 수익률 계산 후 signal_prices.json에 추가
"""
import urllib.request, json, time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent

# env
env = {}
for line in (BASE / '.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip()

URL = env['NEXT_PUBLIC_SUPABASE_URL']
KEY = env['NEXT_PUBLIC_SUPABASE_ANON_KEY']

# 1. DB에서 CNTN-USD 시그널 전체 조회
print('CNTN-USD 시그널 DB 조회...')
api_url = URL + '/rest/v1/influencer_signals?select=id,ticker,signal,created_at&ticker=ilike.*CNTN*&limit=100'
req = urllib.request.Request(api_url, headers={'apikey': KEY, 'Authorization': 'Bearer ' + KEY})
with urllib.request.urlopen(req, timeout=15) as r:
    signals = json.loads(r.read())
print('총 %d개 시그널' % len(signals))

# 2. CoinGecko에서 CNTN 전체 가격 히스토리 가져오기 (max 365일)
print('\nCoinGecko에서 Canton 가격 히스토리 조회...')
time.sleep(1)
cg_url = 'https://api.coingecko.com/api/v3/coins/canton-network/market_chart?vs_currency=usd&days=365&interval=daily'
req = urllib.request.Request(cg_url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
with urllib.request.urlopen(req, timeout=20) as r:
    chart = json.loads(r.read())

# 날짜별 가격 맵 {YYYY-MM-DD: price}
price_map = {}
for ts_ms, price in chart['prices']:
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    date_str = dt.strftime('%Y-%m-%d')
    price_map[date_str] = round(price, 6)
print('가격 히스토리 %d일치' % len(price_map))

# 3. 현재 CNTN 가격
time.sleep(2)
curr_url = 'https://api.coingecko.com/api/v3/simple/price?ids=canton-network&vs_currencies=usd'
req = urllib.request.Request(curr_url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
with urllib.request.urlopen(req, timeout=15) as r:
    curr_data = json.loads(r.read())
current_price = curr_data['canton-network']['usd']
today = datetime.now().strftime('%Y-%m-%d')
print('현재 가격: $%.6f (%s)' % (current_price, today))

# 4. signal_prices.json 로드 & UUID 추가
sp_path = BASE / 'data' / 'signal_prices.json'
sp_data = json.load(open(sp_path, encoding='utf-8'))

added = 0
skipped = 0
for sig in signals:
    uuid = sig['id']
    created_at = sig['created_at'][:10]  # YYYY-MM-DD
    signal_type = sig['signal']

    # 이미 있으면 current_price만 업데이트
    if uuid in sp_data:
        sp_data[uuid]['price_current'] = round(current_price, 6)
        if sp_data[uuid].get('price_at_signal'):
            pct = (current_price - sp_data[uuid]['price_at_signal']) / sp_data[uuid]['price_at_signal'] * 100
            sp_data[uuid]['return_pct'] = round(pct, 2)
        skipped += 1
        continue

    # 시그널 날짜 가격 찾기 (당일 없으면 ±1일)
    price_at = None
    for delta in [0, 1, -1, 2, -2, 3]:
        from datetime import timedelta
        dt = datetime.strptime(created_at, '%Y-%m-%d') + timedelta(days=delta)
        key = dt.strftime('%Y-%m-%d')
        if key in price_map:
            price_at = price_map[key]
            break

    if not price_at:
        print('  [SKIP] %s - %s 날짜 가격 없음' % (uuid[:8], created_at))
        skipped += 1
        continue

    return_pct = round((current_price - price_at) / price_at * 100, 2) if price_at else None

    sp_data[uuid] = {
        'ticker': 'CNTN',
        'signal': signal_type,
        'price_at_signal': price_at,
        'price_current': round(current_price, 6),
        'return_pct': return_pct,
        'last_updated': today
    }
    print('  [ADD] %s | %s | 진입 $%.4f | 현재 $%.4f | 수익률 %s%%' % (
        uuid[:8], created_at, price_at, current_price,
        return_pct if return_pct is not None else 'N/A'
    ))
    added += 1

# 5. 저장
json.dump(sp_data, open(sp_path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('\n완료: %d개 추가, %d개 스킵' % (added, skipped))

# public/ 복사
import shutil
shutil.copy2(sp_path, BASE / 'public' / 'signal_prices.json')
print('public/ 복사 완료')
