#!/usr/bin/env python3
import requests, json
from collections import Counter

env = {}
with open('.env.local') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v

headers = {'apikey': env['SUPABASE_SERVICE_ROLE_KEY'], 'Authorization': 'Bearer ' + env['SUPABASE_SERVICE_ROLE_KEY']}
url = env['NEXT_PUBLIC_SUPABASE_URL']

# influencer_signals 컬럼 확인
resp = requests.get(url + '/rest/v1/influencer_signals', headers=headers, params={'select': '*', 'limit': '1'})
data = resp.json()
if isinstance(data, list) and data:
    print('influencer_signals columns:', list(data[0].keys()))

# speaker 분포 (전체)
resp2 = requests.get(url + '/rest/v1/influencer_signals', headers=headers, params={'select': 'speaker,channel_id', 'limit': '2000'})
signals = resp2.json()
print(f'총 시그널: {len(signals)}')

spk_cnt = Counter(s.get('speaker','') for s in signals)
print('\n상위 30 speaker:')
for spk, cnt in spk_cnt.most_common(30):
    print(f'  [{cnt:3d}] {spk}')

# 채널 목록
resp3 = requests.get(url + '/rest/v1/influencer_channels', headers=headers, params={'select': '*'})
channels = resp3.json()
print('\n모든 채널:')
for ch in channels:
    cname = ch.get('channel_name', '')
    handle = ch.get('channel_handle', '')
    cid = ch.get('id', '')
    print(f'  {cname} / {handle} -> id={cid}')
    if any(k in (cname + handle).lower() for k in ['godofit', '이형수', 'it의신', 'god']):
        print(f'    *** GODOFIT/이형수 MATCH ***')

# Godofit/이형수 시그널 상세
print('\n이형수/Godofit 관련 시그널 샘플:')
for s in signals:
    spk = str(s.get('speaker', ''))
    if any(k in spk for k in ['이형수', 'Godofit', 'godofit', 'IT의신']):
        print(f"  speaker={spk}, channel_id={s.get('channel_id','')[:8]}")
        break
