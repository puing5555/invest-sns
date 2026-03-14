#!/usr/bin/env python3
"""influencer_videos 400 에러 원인 진단"""
import requests, json, uuid

env = {}
with open('.env.local') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v

h = {'apikey': env['SUPABASE_SERVICE_ROLE_KEY'],
     'Authorization': 'Bearer ' + env['SUPABASE_SERVICE_ROLE_KEY'],
     'Content-Type': 'application/json'}
url = env['NEXT_PUBLIC_SUPABASE_URL']

ANYU_CH = '6d6817ca-76ab-484e-ad7e-b537921c3d25'

# 1. 정상 GET 조회
r1 = requests.get(url + '/rest/v1/influencer_videos', headers=h,
                  params={'video_id': 'eq.XveVkr3JHs4', 'select': 'id'})
print(f'[1] 정상 GET: {r1.status_code} → {r1.text[:200]}')

# 2. 빈 video_id GET
r2 = requests.get(url + '/rest/v1/influencer_videos', headers=h,
                  params={'video_id': 'eq.', 'select': 'id'})
print(f'[2] 빈 video_id GET: {r2.status_code} → {r2.text[:200]}')

# 3. 정상 INSERT 테스트
vid = 'TEST_' + str(uuid.uuid4())[:8]
test_data = {
    'id': str(uuid.uuid4()),
    'video_id': vid,
    'channel_id': ANYU_CH,
    'title': 'TEST VIDEO',
    'published_at': '2026-03-12T00:00:00+00:00',
    'duration_seconds': 100,
    'created_at': '2026-03-12T00:00:00+00:00'
}
r3 = requests.post(url + '/rest/v1/influencer_videos', headers=h, json=test_data)
print(f'[3] 정상 INSERT: {r3.status_code} → {r3.text[:300]}')
requests.delete(url + '/rest/v1/influencer_videos', headers=h, params={'video_id': f'eq.{vid}'})

# 4. published_at=NULL INSERT
vid4 = 'TEST_NULL_' + str(uuid.uuid4())[:6]
test_null = {**test_data, 'video_id': vid4, 'id': str(uuid.uuid4()), 'published_at': None}
r4 = requests.post(url + '/rest/v1/influencer_videos', headers=h, json=test_null)
print(f'[4] published_at=NULL INSERT: {r4.status_code} → {r4.text[:300]}')
if r4.status_code in [200, 201]:
    requests.delete(url + '/rest/v1/influencer_videos', headers=h, params={'video_id': f'eq.{vid4}'})

# 5. 실제 안유화 영상 ID로 테스트 (공개 영상 중 하나)
# ztPwQOHkU88 - 로그에서 추출 추출 시도된 영상
vid5 = 'ztPwQOHkU88'
r5 = requests.get(url + '/rest/v1/influencer_videos', headers=h,
                  params={'video_id': f'eq.{vid5}', 'select': 'id'})
print(f'[5] 안유화 영상 조회 ({vid5}): {r5.status_code} → {r5.text[:200]}')

# 6. 이미 처리된 안유화 영상 UUID로 INSERT 시도 (중복 케이스)
vid6 = 'ztPwQOHkU88'
test6 = {
    'id': str(uuid.uuid4()),
    'video_id': vid6,
    'channel_id': ANYU_CH,
    'title': '테스트 중복',
    'published_at': '2026-01-01T00:00:00+00:00',
    'duration_seconds': 500,
    'created_at': '2026-03-12T00:00:00+00:00'
}
r6 = requests.post(url + '/rest/v1/influencer_videos', headers=h, json=test6)
print(f'[6] 중복 video_id INSERT: {r6.status_code} → {r6.text[:300]}')

# 7. upload_date 없는 경우 (published_at 없이) - 실제 파이프라인 케이스
vid7 = 'NODATE_' + str(uuid.uuid4())[:6]
test7 = {
    'id': str(uuid.uuid4()),
    'video_id': vid7,
    'channel_id': ANYU_CH,
    'title': '날짜 없음 테스트',
    'duration_seconds': None,
    'created_at': '2026-03-12T00:00:00+00:00'
    # published_at 없음
}
r7 = requests.post(url + '/rest/v1/influencer_videos', headers=h, json=test7)
print(f'[7] published_at 없음 INSERT: {r7.status_code} → {r7.text[:300]}')
if r7.status_code in [200, 201]:
    requests.delete(url + '/rest/v1/influencer_videos', headers=h, params={'video_id': f'eq.{vid7}'})
