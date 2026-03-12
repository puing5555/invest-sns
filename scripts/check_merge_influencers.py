#!/usr/bin/env python3
"""Godofit + 이형수 인플루언서 DB 상태 확인"""
import requests, json

env = {}
with open('.env.local') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v

headers = {'apikey': env['SUPABASE_SERVICE_ROLE_KEY'], 'Authorization': 'Bearer ' + env['SUPABASE_SERVICE_ROLE_KEY']}
url = env['NEXT_PUBLIC_SUPABASE_URL']

# 1. influencers 테이블 전체 조회
resp = requests.get(url + '/rest/v1/influencers', headers=headers, params={'select': 'id,name,slug,profile_image_url'})
influencers = resp.json()
print('=== influencers 테이블 ===')
if isinstance(influencers, list):
    for inf in influencers:
        print(f"  id={inf.get('id')}, name={inf.get('name')}, slug={inf.get('slug')}")
else:
    print('ERROR:', influencers)

# 2. influencer_channels 조회 (godofit 관련)
resp2 = requests.get(url + '/rest/v1/influencer_channels', headers=headers, params={'select': 'id,channel_name,channel_handle,influencer_id'})
channels = resp2.json()
print('\n=== influencer_channels ===')
if isinstance(channels, list):
    for ch in channels:
        name = str(ch.get('channel_name','')) + str(ch.get('channel_handle',''))
        if any(k in name.lower() for k in ['godofit','이형수','it의신','god']):
            print(f"  MATCH: id={ch.get('id')}, name={ch.get('channel_name')}, handle={ch.get('channel_handle')}, influencer_id={ch.get('influencer_id')}")
else:
    print('ERROR:', channels)

# 3. influencer_signals에서 각각 카운트
for label, term in [('Godofit', 'godofit'), ('이형수', '이형수')]:
    # influencer_id로 조인해서 찾기
    resp3 = requests.get(url + '/rest/v1/influencer_signals', headers={**headers, 'Prefer': 'count=exact'}, 
                        params={'select': 'id', 'limit': '1'})
    # 실제로는 speaker로 찾아야 함
    resp4 = requests.get(url + '/rest/v1/influencer_signals', headers={**headers, 'Prefer': 'count=exact'},
                        params={'speaker': f'ilike.*{label}*', 'select': 'id', 'limit': '1'})
    print(f'\n=== {label} 시그널 (speaker 기준) ===')
    print(f"  Content-Range: {resp4.headers.get('Content-Range', 'N/A')}")

# speaker 전체 분포 확인
resp5 = requests.get(url + '/rest/v1/influencer_signals', headers=headers, 
                    params={'select': 'speaker', 'limit': '2000'})
signals = resp5.json()
if isinstance(signals, list):
    from collections import Counter
    speaker_counts = Counter(s.get('speaker','') for s in signals)
    print('\n=== speaker 분포 (상위 20) ===')
    for spk, cnt in speaker_counts.most_common(20):
        print(f"  {spk}: {cnt}개")
