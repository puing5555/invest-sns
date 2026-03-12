#!/usr/bin/env python3
"""DB 스키마 정확히 파악"""
import requests, json

env = {}
with open('.env.local') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v

h = {'apikey': env['SUPABASE_SERVICE_ROLE_KEY'], 'Authorization': 'Bearer ' + env['SUPABASE_SERVICE_ROLE_KEY']}
url = env['NEXT_PUBLIC_SUPABASE_URL']

# 1. speakers 테이블 있는지 확인
for table in ['speakers', 'influencer_speakers', 'speaker_profiles']:
    r = requests.get(url + f'/rest/v1/{table}', headers=h, params={'select': '*', 'limit': '3'})
    print(f'{table}: status={r.status_code}, body={r.text[:200]}')

# 2. influencer_signals 전체 카운트 (Prefer: count=exact)
r2 = requests.get(url + '/rest/v1/influencer_signals', headers={**h, 'Prefer': 'count=exact'},
                  params={'select': 'id', 'limit': '1'})
print(f'\ninfl_signals count: {r2.headers.get("Content-Range")}')

# 3. influencer_signals 샘플 (올바른 컬럼)
r3 = requests.get(url + '/rest/v1/influencer_signals', headers=h, 
                  params={'select': 'id,video_id,speaker_id,signal,stock', 'limit': '5'})
data = r3.json()
print('\ninfl_signals 샘플:')
if isinstance(data, list):
    for d in data:
        print(f"  {json.dumps(d, ensure_ascii=False)}")
else:
    print(data)

# 4. influencer_channels에서 godofit 찾기
r4 = requests.get(url + '/rest/v1/influencer_channels', headers=h, params={'select': '*'})
channels = r4.json()
print('\n모든 채널:')
for ch in channels:
    print(f"  {ch.get('channel_name')} | {ch.get('channel_handle')} | id={ch.get('id','')}")

# 5. influencer_videos 샘플
r5 = requests.get(url + '/rest/v1/influencer_videos', headers=h, params={'select': '*', 'limit': '1'})
vd = r5.json()
if isinstance(vd, list) and vd:
    print('\ninfl_videos columns:', list(vd[0].keys()))
