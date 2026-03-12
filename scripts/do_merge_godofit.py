#!/usr/bin/env python3
"""
Godofit + 이형수 → 이형수 (IT의신) 통합
"""
import requests, json, sys
from collections import Counter

DRY_RUN = '--dry-run' in sys.argv

env = {}
with open('.env.local') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v

h = {'apikey': env['SUPABASE_SERVICE_ROLE_KEY'], 'Authorization': 'Bearer ' + env['SUPABASE_SERVICE_ROLE_KEY'],
     'Content-Type': 'application/json'}
url = env['NEXT_PUBLIC_SUPABASE_URL']

GODOFIT_CH_ID = '227ad970-4f05-4fea-9a94-90f9649ca714'
HYOSEOK_SPK_ID = '88892b60-9e6b-4390-ba3b-c6d1453b3cef'
PROFILE_IMAGE = 'https://yt3.googleusercontent.com/SzJXzmXqT1gNFdrf8uZk8-gUfu8liLyJ6lVGD3o05acZVLOFwhYFNdIg8sYMF43QsO5R7AsH=s900-c-k-c0x00ffffff-no-rj'

# ── 1. Godofit 채널의 모든 영상 ID 수집 ──────────────────────────────
r = requests.get(url + '/rest/v1/influencer_videos', headers=h,
                 params={'channel_id': f'eq.{GODOFIT_CH_ID}', 'select': 'id', 'limit': '500'})
videos = r.json()
vid_ids = [v['id'] for v in videos] if isinstance(videos, list) else []
print(f'Godofit 채널 영상: {len(vid_ids)}개')

# ── 2. Godofit 영상의 시그널 전체 수집 ──────────────────────────────
godofit_signals = []
for i in range(0, len(vid_ids), 100):
    batch = vid_ids[i:i+100]
    ids_str = ','.join(batch)
    r2 = requests.get(url + '/rest/v1/influencer_signals', headers=h,
                      params={'video_id': f'in.({ids_str})', 'select': 'id,speaker_id', 'limit': '2000'})
    data = r2.json()
    if isinstance(data, list):
        godofit_signals.extend(data)
    else:
        print(f'  ERROR: {data}')

print(f'Godofit 시그널: {len(godofit_signals)}개')

# speaker_id 분포
spk_cnt = Counter(s.get('speaker_id','') for s in godofit_signals)
print('speaker_id 분포:')
for spk_id, cnt in spk_cnt.most_common():
    print(f'  [{cnt}] {spk_id}')

# ── 3. 이형수 시그널 카운트 ──────────────────────────────────────────
r3 = requests.get(url + '/rest/v1/influencer_signals', headers={**h, 'Prefer': 'count=exact'},
                  params={'speaker_id': f'eq.{HYOSEOK_SPK_ID}', 'select': 'id', 'limit': '1'})
cr = r3.headers.get('Content-Range', '0/0')
hyoseok_cnt = int(cr.split('/')[-1]) if '/' in cr else 0
print(f'이형수 (기존) 시그널: {hyoseok_cnt}개')
print(f'통합 예상: {len(godofit_signals) + hyoseok_cnt}개')

# Godofit speaker_id들 (이형수 ID와 다른 것들)
godofit_spk_ids = [spk_id for spk_id in spk_cnt if spk_id and spk_id != HYOSEOK_SPK_ID]
print(f'\nGodofit 전용 speaker_ids: {godofit_spk_ids}')
null_cnt = spk_cnt.get(None, spk_cnt.get('None', 0))
print(f'speaker_id=NULL 시그널: {null_cnt}개 (Godofit 채널 시그널)')

if DRY_RUN:
    print('\n[DRY RUN] 변경 없음. --execute로 실행')
    sys.exit(0)

print('\n=== 실행 ===')

# ── 4a. speaker_id=NULL인 Godofit 시그널 → 이형수 ID로 ─────────────
if null_cnt > 0:
    print(f'[1] Godofit 시그널 {null_cnt}건 (speaker_id=NULL) → 이형수 ID로 변경...')
    # video_id in (godofit_video_ids) 조건으로 업데이트 (배치 처리)
    total_updated = 0
    for i in range(0, len(vid_ids), 100):
        batch = vid_ids[i:i+100]
        ids_str = ','.join(batch)
        upd = requests.patch(url + '/rest/v1/influencer_signals', headers=h,
                             params={'video_id': f'in.({ids_str})', 'speaker_id': 'is.null'},
                             json={'speaker_id': HYOSEOK_SPK_ID})
        print(f'    batch {i//100+1}: status={upd.status_code}')
        total_updated += len(batch)
    print(f'    총 {null_cnt}건 업데이트 완료')

# ── 4b. Godofit 전용 speaker_id 시그널 → 이형수 ID로 ────────────────
for spk_id in godofit_spk_ids:
    sig_cnt = spk_cnt[spk_id]
    print(f'[1b] speaker_id {spk_id[:8]} ({sig_cnt}건) → 이형수 ID로 변경...')
    upd = requests.patch(url + '/rest/v1/influencer_signals', headers=h,
                         params={'speaker_id': f'eq.{spk_id}'},
                         json={'speaker_id': HYOSEOK_SPK_ID})
    print(f'    status: {upd.status_code}, body: {upd.text[:100]}')

# Godofit 영상에서 이미 이형수 ID를 쓰고 있는 것도 있을 수 있으니
# 혹시 다른 speaker_id인데 이형수 ID와 다른 경우 모두 처리됨

# ── 5. 이형수 speaker 레코드 업데이트 ────────────────────────────────
print(f'\n[2] 이형수 speaker 레코드 업데이트...')
upd2 = requests.patch(url + '/rest/v1/speakers', headers=h,
                      params={'id': f'eq.{HYOSEOK_SPK_ID}'},
                      json={
                          'name': '이형수 (IT의신)',
                          'profile_image_url': PROFILE_IMAGE,
                          'aliases': ['이형수', 'IT의신', 'Godofit', '이형수(IT의신)', '이형수 대표']
                      })
print(f'    status: {upd2.status_code}, body: {upd2.text[:200]}')

# ── 6. 중복 Godofit speaker 레코드 삭제 ─────────────────────────────
for spk_id in godofit_spk_ids:
    print(f'\n[3] Godofit speaker 레코드 삭제 (id={spk_id[:8]})...')
    del_r = requests.delete(url + '/rest/v1/speakers', headers=h,
                            params={'id': f'eq.{spk_id}'})
    print(f'    status: {del_r.status_code}, body: {del_r.text[:100]}')

# ── 7. 검증 ─────────────────────────────────────────────────────────
print('\n=== 검증 ===')
r_final = requests.get(url + '/rest/v1/influencer_signals', headers={**h, 'Prefer': 'count=exact'},
                       params={'speaker_id': f'eq.{HYOSEOK_SPK_ID}', 'select': 'id', 'limit': '1'})
cr_final = r_final.headers.get('Content-Range', '0/0')
final_cnt = int(cr_final.split('/')[-1]) if '/' in cr_final else 0
print(f'통합 후 이형수 (IT의신) 시그널: {final_cnt}개')

spk_r = requests.get(url + '/rest/v1/speakers', headers=h, params={'id': f'eq.{HYOSEOK_SPK_ID}', 'select': '*'})
print(f'최종 speaker: {json.dumps(spk_r.json(), ensure_ascii=False)}')
print('\n✅ 완료!')
