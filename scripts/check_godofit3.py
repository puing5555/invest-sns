#!/usr/bin/env python3
"""Godofit 채널 시그널의 실제 speaker_id 역추적"""
import requests, json
from collections import Counter

env = {}
with open('.env.local') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v

h = {'apikey': env['SUPABASE_SERVICE_ROLE_KEY'], 'Authorization': 'Bearer ' + env['SUPABASE_SERVICE_ROLE_KEY']}
url = env['NEXT_PUBLIC_SUPABASE_URL']

GODOFIT_CH_ID = '227ad970-4f05-4fea-9a94-90f9649ca714'
HYOSEOK_SPK_ID = '88892b60-9e6b-4390-ba3b-c6d1453b3cef'

# 1. Godofit 채널 영상 목록
r = requests.get(url + '/rest/v1/influencer_videos', headers={**h, 'Prefer': 'count=exact'},
                 params={'channel_id': f'eq.{GODOFIT_CH_ID}', 'select': 'id', 'limit': '1'})
print(f'Godofit 채널 영상 수: {r.headers.get("Content-Range")}')

# 영상 ID 전체 수집
r2 = requests.get(url + '/rest/v1/influencer_videos', headers=h,
                  params={'channel_id': f'eq.{GODOFIT_CH_ID}', 'select': 'id', 'limit': '1000'})
videos = r2.json()
vid_ids = [v['id'] for v in videos] if isinstance(videos, list) else []
print(f'video IDs 수집: {len(vid_ids)}개')

# 2. 해당 영상들의 시그널 → speaker_id 분포
if vid_ids:
    # Supabase in() 필터: 최대 100개씩
    batch_size = 100
    all_signals = []
    for i in range(0, len(vid_ids), batch_size):
        batch = vid_ids[i:i+batch_size]
        ids_str = ','.join(batch)
        r3 = requests.get(url + '/rest/v1/influencer_signals', headers=h,
                         params={'video_id': f'in.({ids_str})', 'select': 'id,speaker_id', 'limit': '2000'})
        data = r3.json()
        if isinstance(data, list):
            all_signals.extend(data)

    print(f'Godofit 채널 시그널 수: {len(all_signals)}개')
    spk_cnt = Counter(s.get('speaker_id','') for s in all_signals)
    print('speaker_id 분포:')
    for spk_id, cnt in spk_cnt.most_common():
        # speaker 이름 조회
        sr = requests.get(url + '/rest/v1/speakers', headers=h, params={'id': f'eq.{spk_id}', 'select': 'name,aliases'})
        spk_data = sr.json()
        spk_name = spk_data[0].get('name') if spk_data else 'UNKNOWN'
        mark = ' *** GODOFIT/이형수 후보' if cnt > 50 else ''
        print(f'  [{cnt:3d}] {spk_id[:8]} = {spk_name}{mark}')

# 3. 이형수 speaker 시그널 카운트
r4 = requests.get(url + '/rest/v1/influencer_signals', headers={**h, 'Prefer': 'count=exact'},
                  params={'speaker_id': f'eq.{HYOSEOK_SPK_ID}', 'select': 'id', 'limit': '1'})
print(f'\n이형수 시그널 총 카운트: {r4.headers.get("Content-Range")}')
