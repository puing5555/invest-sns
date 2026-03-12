# -*- coding: utf-8 -*-
import sys, requests, json, os
sys.stdout.reconfigure(encoding='utf-8')

env = {}
with open('.env.local') as f:
    for line in f:
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v

key = env.get('SUPABASE_SERVICE_ROLE_KEY', '')
h = {'apikey': key, 'Authorization': 'Bearer ' + key}
SUPA = 'https://arypzhotxflimroprmdk.supabase.co'

# 전체 시그널 가져오기
all_sigs = []
offset = 0
while True:
    r = requests.get(f'{SUPA}/rest/v1/influencer_signals?select=id,stock,ticker,signal&limit=1000&offset={offset}', headers=h)
    batch = r.json()
    if not batch:
        break
    all_sigs.extend(batch)
    offset += 1000
    if len(batch) < 1000:
        break

sp = json.load(open('public/signal_prices.json', encoding='utf-8'))
existing_ids = set(k for k in sp.keys() if '-' in k)

all_ids = set(s['id'] for s in all_sigs)
missing = all_ids - existing_ids
print(f'총 시그널: {len(all_ids)}')
print(f'signal_prices에 있는 UUID: {len(existing_ids)}')
print(f'누락된 UUID: {len(missing)}')

missing_sigs = [s for s in all_sigs if s['id'] in missing]
missing_with_ticker = [s for s in missing_sigs if s.get('ticker')]
print(f'누락+ticker있음: {len(missing_with_ticker)}')

# 샘플 10개
for s in missing_with_ticker[:10]:
    sid = s['id'][:8]
    print(f'  {sid}... stock={s["stock"]} ticker={s["ticker"]} signal={s["signal"]}')

# 코린이아빠 관련 확인 - speaker join
r2 = requests.get(f'{SUPA}/rest/v1/influencer_signals?select=id,stock,ticker,signal,influencer_videos(influencer_channels(channel_name,slug))&limit=1000', headers=h)
sigs2 = r2.json()
korini_sigs = [s for s in sigs2 if s.get('influencer_videos') and s['influencer_videos'].get('influencer_channels') and 'korini' in str(s['influencer_videos']['influencer_channels'].get('slug', '')).lower()]
print(f'\n코린이아빠 시그널 수: {len(korini_sigs)}')
if korini_sigs:
    for s in korini_sigs[:3]:
        sid = s['id'][:8]
        in_sp = '✅' if s['id'] in existing_ids else '❌'
        print(f'  {sid}... stock={s["stock"]} ticker={s["ticker"]} | in_sp={in_sp}')
