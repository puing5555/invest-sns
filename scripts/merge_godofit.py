#!/usr/bin/env python3
"""
Godofit + 이형수 인플루언서 통합 스크립트
- speakers 테이블에서 두 레코드 찾기
- 시그널 전부 이형수 (IT의신) 으로 통합
- Godofit speaker 레코드 삭제 (채널은 유지)
- profile_image_url 업데이트
"""
import requests, json, sys

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

# ── 1. speakers 전체 조회 ────────────────────────────────────────────
r = requests.get(url + '/rest/v1/speakers', headers=h, params={'select': 'id,name,aliases,profile_image_url'})
speakers = r.json()
print(f'전체 speakers: {len(speakers)}개')

godofit_spk = None
hyoseok_spk = None

for spk in speakers:
    name = str(spk.get('name', ''))
    aliases = str(spk.get('aliases', ''))
    key = (name + aliases).lower()
    print(f"  [{spk['id'][:8]}] {name} | aliases={aliases[:60]}")
    if any(k in key for k in ['godofit', 'it의신', 'godof']):
        godofit_spk = spk
        print(f"    *** GODOFIT 발견 ***")
    if any(k in key for k in ['이형수']):
        hyoseok_spk = spk
        print(f"    *** 이형수 발견 ***")

if not godofit_spk and not hyoseok_spk:
    print('\n⚠️ 두 speaker 모두 못 찾음. 이름으로 다시 검색...')
    # 채널명 Godofit으로 연결된 video → signal → speaker_id 역추적
    ch_r = requests.get(url + '/rest/v1/influencer_channels', headers=h,
                        params={'channel_handle': 'eq.@GODofIT', 'select': 'id'})
    channels = ch_r.json()
    if channels:
        ch_id = channels[0]['id']
        vid_r = requests.get(url + '/rest/v1/influencer_videos', headers=h,
                             params={'channel_id': f'eq.{ch_id}', 'select': 'id', 'limit': '5'})
        vids = vid_r.json()
        if vids:
            vid_ids = [v['id'] for v in vids[:3]]
            # 해당 videos의 시그널에서 speaker_id 추출
            sig_r = requests.get(url + '/rest/v1/influencer_signals', headers=h,
                                 params={'video_id': f'in.({",".join(vid_ids)})', 'select': 'speaker_id', 'limit': '5'})
            sigs = sig_r.json()
            sp_ids = list(set(s['speaker_id'] for s in sigs if s.get('speaker_id')))
            print(f'Godofit 채널 → speaker_ids: {sp_ids}')
            for sp_id in sp_ids:
                spk_r = requests.get(url + '/rest/v1/speakers', headers=h,
                                     params={'id': f'eq.{sp_id}', 'select': '*'})
                spk_data = spk_r.json()
                if spk_data:
                    print(f"  speaker: {json.dumps(spk_data[0], ensure_ascii=False)}")
                    if not godofit_spk:
                        godofit_spk = spk_data[0]

print('\n=== 통합 계획 ===')
print(f'Godofit speaker: {json.dumps(godofit_spk, ensure_ascii=False) if godofit_spk else "NOT FOUND"}')
print(f'이형수 speaker:  {json.dumps(hyoseok_spk, ensure_ascii=False) if hyoseok_spk else "NOT FOUND"}')

if not godofit_spk:
    print('\n❌ Godofit speaker를 찾지 못했습니다. 스크립트 종료.')
    sys.exit(1)

# 대상 speaker_id 결정
GODOFIT_ID = godofit_spk['id']
PROFILE_IMAGE = 'https://yt3.googleusercontent.com/SzJXzmXqT1gNFdrf8uZk8-gUfu8liLyJ6lVGD3o05acZVLOFwhYFNdIg8sYMF43QsO5R7AsH=s900-c-k-c0x00ffffff-no-rj'

if hyoseok_spk:
    # 이형수 레코드가 별도로 있는 경우: Godofit → 이형수 ID로 시그널 이전 후 Godofit 삭제
    TARGET_ID = hyoseok_spk['id']
    print(f'\n▶ 전략: 이형수 기존 레코드({TARGET_ID[:8]})로 통합, Godofit 레코드 삭제')
else:
    # Godofit 레코드를 이름만 바꿔서 이형수 (IT의신)으로 업데이트
    TARGET_ID = GODOFIT_ID
    print(f'\n▶ 전략: Godofit 레코드를 이형수 (IT의신)으로 이름/프로필 변경')

# ── 2. 각 speaker의 시그널 카운트 ────────────────────────────────────
def count_signals(speaker_id):
    r = requests.get(url + '/rest/v1/influencer_signals', headers={**h, 'Prefer': 'count=exact'},
                     params={'speaker_id': f'eq.{speaker_id}', 'select': 'id', 'limit': '1'})
    cr = r.headers.get('Content-Range', '0/0')
    return int(cr.split('/')[-1]) if '/' in cr else 0

godofit_cnt = count_signals(GODOFIT_ID)
hyoseok_cnt = count_signals(TARGET_ID) if TARGET_ID != GODOFIT_ID else 0
print(f'\nGodofit 시그널: {godofit_cnt}개')
print(f'이형수 시그널: {hyoseok_cnt}개')
print(f'통합 후 예상: {godofit_cnt + hyoseok_cnt}개')

if DRY_RUN:
    print('\n[DRY RUN] 실제 변경 없음. --execute 로 실행하세요.')
    sys.exit(0)

# ── 3. 실제 통합 실행 ────────────────────────────────────────────────
print('\n=== 실행 시작 ===')

if TARGET_ID != GODOFIT_ID:
    # Case A: 이형수 레코드가 별도로 있음
    # 3a. Godofit 시그널 → 이형수 ID로 일괄 업데이트
    if godofit_cnt > 0:
        print(f'[1] 시그널 {godofit_cnt}건 speaker_id 변경: {GODOFIT_ID[:8]} → {TARGET_ID[:8]}')
        upd_r = requests.patch(url + '/rest/v1/influencer_signals', headers=h,
                               params={'speaker_id': f'eq.{GODOFIT_ID}'},
                               json={'speaker_id': TARGET_ID})
        print(f'    status: {upd_r.status_code}')
    
    # 3b. 이형수 speaker 레코드 업데이트 (이름 + 프로필)
    print(f'[2] 이형수 speaker 레코드 업데이트')
    upd2 = requests.patch(url + '/rest/v1/speakers', headers=h,
                          params={'id': f'eq.{TARGET_ID}'},
                          json={'name': '이형수 (IT의신)', 'profile_image_url': PROFILE_IMAGE,
                                'aliases': ['이형수', 'IT의신', 'Godofit', '이형수(IT의신)']})
    print(f'    status: {upd2.status_code}')
    
    # 3c. Godofit speaker 레코드 삭제
    print(f'[3] Godofit speaker 레코드 삭제 (id={GODOFIT_ID[:8]})')
    del_r = requests.delete(url + '/rest/v1/speakers', headers=h,
                            params={'id': f'eq.{GODOFIT_ID}'})
    print(f'    status: {del_r.status_code}')

else:
    # Case B: Godofit 레코드를 이형수 (IT의신)으로 변경
    print(f'[1] Godofit speaker 레코드를 이형수 (IT의신)으로 변경')
    upd_r = requests.patch(url + '/rest/v1/speakers', headers=h,
                           params={'id': f'eq.{GODOFIT_ID}'},
                           json={'name': '이형수 (IT의신)', 'profile_image_url': PROFILE_IMAGE,
                                 'aliases': ['이형수', 'IT의신', 'Godofit', '이형수(IT의신)']})
    print(f'    status: {upd_r.status_code}, body: {upd_r.text[:200]}')

# ── 4. 검증 ────────────────────────────────────────────────────────
print('\n=== 검증 ===')
final_cnt = count_signals(TARGET_ID)
print(f'통합 후 이형수 (IT의신) 시그널: {final_cnt}개')

# 최종 speaker 확인
spk_r = requests.get(url + '/rest/v1/speakers', headers=h, params={'id': f'eq.{TARGET_ID}', 'select': '*'})
print(f'최종 speaker: {json.dumps(spk_r.json(), ensure_ascii=False)}')

print('\n✅ 통합 완료!')
