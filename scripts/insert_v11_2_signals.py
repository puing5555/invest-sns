#!/usr/bin/env python3
"""V11.2 세상학개론 시그널 INSERT + 기존 잘못된 시그널 DELETE"""
import sys, requests, json
sys.stdout.reconfigure(encoding='utf-8')

env = {}
with open(r'C:\Users\Mario\work\invest-sns\.env.local') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            k, v = line.strip().split('=', 1)
            env[k] = v

URL = env['NEXT_PUBLIC_SUPABASE_URL']
KEY = env['SUPABASE_SERVICE_ROLE_KEY']
H = {'apikey': KEY, 'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'Prefer': 'return=representation'}

SESANG_CH = 'd68f8efd-64c8-4c07-9d34-e98c2954f4e1'

# ── STEP 1: 잘못된 기존 시그널 3개 삭제 (코스피/금 = INDEX/원자재) ──
DELETE_IDS = ['8a39cf9d', 'fadf60d1', 'e9aedc29']  # 앞 8자리로 부분 일치
r = requests.get(f'{URL}/rest/v1/influencer_signals?video_id=in.({",".join(["0f17e179-ff3b-4c6e-9c9e-a26fd99f5ae7","34eea767-47ec-4e9f-8f72-1a9f3f5f6e8e","dde613a8-5e8e-4a8e-9a8e-8a8e8a8e8a8e"])})',
                 headers={'apikey': KEY, 'Authorization': 'Bearer ' + KEY})

# 전체 세상학개론 시그널 중 INDEX/원자재인 것 삭제
r_sigs = requests.get(
    f'{URL}/rest/v1/influencer_signals?stock=in.(코스피,금)&select=id,stock,signal,video_id',
    headers={'apikey': KEY, 'Authorization': 'Bearer ' + KEY}
)
bad_sigs = r_sigs.json()
print(f'삭제 대상 시그널 ({len(bad_sigs)}개):')
for s in bad_sigs:
    print(f'  [{s["signal"]}] {s["stock"]} | id: {s["id"]}')

deleted = 0
for s in bad_sigs:
    dr = requests.delete(
        f'{URL}/rest/v1/influencer_signals?id=eq.{s["id"]}',
        headers={'apikey': KEY, 'Authorization': 'Bearer ' + KEY}
    )
    if dr.status_code in [200, 204]:
        print(f'  ✅ 삭제: [{s["signal"]}] {s["stock"]}')
        deleted += 1
    else:
        print(f'  ❌ 삭제 실패: {dr.status_code} {dr.text[:100]}')

print(f'삭제 완료: {deleted}개\n')

# ── STEP 2: 영상 등록 (8Nn3qerCt44, Xv-wNA91EPE) ──
videos_to_add = [
    {
        'video_id': '8Nn3qerCt44',
        'channel_id': SESANG_CH,
        'title': '올해는 피지컬 AI 해 - 현대차 로봇 자율주행 전망 | 이정윤',
        'platform': 'youtube',
        'url': 'https://www.youtube.com/watch?v=8Nn3qerCt44'
    },
    {
        'video_id': 'Xv-wNA91EPE',
        'channel_id': SESANG_CH,
        'title': '삼성전자 20만원, 새로운 랠리의 시작점 | 조진표',
        'platform': 'youtube',
        'url': 'https://www.youtube.com/watch?v=Xv-wNA91EPE'
    }
]

vid_db_ids = {}
for v in videos_to_add:
    # 이미 있는지 확인
    r = requests.get(f'{URL}/rest/v1/influencer_videos?video_id=eq.{v["video_id"]}&select=id,video_id',
                     headers={'apikey': KEY, 'Authorization': 'Bearer ' + KEY})
    existing = r.json()
    if existing:
        vid_db_ids[v['video_id']] = existing[0]['id']
        print(f'영상 이미 존재: {v["video_id"]} → {existing[0]["id"]}')
    else:
        r2 = requests.post(f'{URL}/rest/v1/influencer_videos', headers=H, json=v)
        if r2.status_code == 201:
            new_id = r2.json()[0]['id']
            vid_db_ids[v['video_id']] = new_id
            print(f'영상 등록: {v["video_id"]} → {new_id}')
        else:
            print(f'영상 등록 실패: {r2.status_code} {r2.text[:200]}')

print()

# ── STEP 3: 스피커 등록/조회 (이정윤, 조진표) ──
speakers_to_add = [
    {'name': '이정윤', 'aliases': ['이정윤', '이정원', '이정윤세무사']},
    {'name': '조진표', 'aliases': ['조진표', '조진표대표']}
]

speaker_ids = {}
for sp in speakers_to_add:
    r = requests.get(f'{URL}/rest/v1/speakers?name=eq.{sp["name"]}&select=id,name',
                     headers={'apikey': KEY, 'Authorization': 'Bearer ' + KEY})
    existing = r.json()
    if existing:
        speaker_ids[sp['name']] = existing[0]['id']
        print(f'스피커 이미 존재: {sp["name"]} → {existing[0]["id"]}')
    else:
        r2 = requests.post(f'{URL}/rest/v1/speakers', headers=H, json=sp)
        if r2.status_code == 201:
            new_id = r2.json()[0]['id']
            speaker_ids[sp['name']] = new_id
            print(f'스피커 등록: {sp["name"]} → {new_id}')
        else:
            print(f'스피커 등록 실패: {r2.status_code} {r2.text[:200]}')

print()

# ── STEP 4: 8개 시그널 INSERT ──
# 8Nn3qerCt44 vid_id
v1 = vid_db_ids.get('8Nn3qerCt44', '')
v2 = vid_db_ids.get('Xv-wNA91EPE', '')
sp_이정윤 = speaker_ids.get('이정윤', '')
sp_조진표 = speaker_ids.get('조진표', '')

signals = [
    # VIDEO: 8Nn3qerCt44 (이정윤)
    {
        'video_id': v1, 'speaker_id': sp_이정윤,
        'stock': '현대차', 'ticker': '005380', 'market': 'KR',
        'mention_type': '결론', 'signal': '긍정', 'confidence': 'high',
        'timestamp': '00:30',
        'key_quote': '현대차 그룹주가 1순위... 피지컬 AI 두 가지(로봇+자율주행)를 다 생산할 수 있는 회사',
        'reasoning': '이정윤은 2025년을 피지컬AI 원년으로 보고, 로봇+자율주행 두 축에서 현대차 그룹주가 1순위라고 명확하게 방향성 의견 제시. V11.2 기준 방향성 의견 = 긍정.'
    },
    {
        'video_id': v1, 'speaker_id': sp_이정윤,
        'stock': '에이피알', 'ticker': '278470', 'market': 'KR',
        'mention_type': '결론', 'signal': '긍정', 'confidence': 'high',
        'timestamp': '07:20',
        'key_quote': '화장품 대장주인 APR 갔어요... 역사적 신고가를 돌파했거든요. 성장성+실적 받쳐 주고 있다',
        'reasoning': '이정윤은 APR이 미국 성공 스토리 + 실적 확인 + 신고가 돌파를 근거로 긍정 평가. 명확한 방향성 의견.'
    },
    {
        'video_id': v1, 'speaker_id': sp_이정윤,
        'stock': '하이브', 'ticker': '352820', 'market': 'KR',
        'mention_type': '결론', 'signal': '긍정', 'confidence': 'medium',
        'timestamp': '09:15',
        'key_quote': 'BTS 아리랑 앨범으로 수년만의 월드투어... 저는 공개 지지를 해야겠다. 굉장히 큰 이슈가 될 것',
        'reasoning': '이정윤은 BTS 복귀(아리랑 앨범, 월드투어), 넷플릭스 데몬헌터스 효과로 신규 팬층 증가를 근거로 하이브 긍정 평가.'
    },
    {
        'video_id': v1, 'speaker_id': sp_이정윤,
        'stock': '방산', 'ticker': None, 'market': 'SECTOR',
        'mention_type': '결론', 'signal': '긍정', 'confidence': 'medium',
        'timestamp': '05:00',
        'key_quote': '방산주는 우리나라에 너무나 최적화된 산업... 역사적 신고가를 다시 뚫었거든요',
        'reasoning': '이정윤은 우크라이나전쟁 수혜 지속+각국 방위비 증가(트럼프 압박)+우주항공 추가 모멘텀으로 방산 섹터 긍정 평가.'
    },
    {
        'video_id': v1, 'speaker_id': sp_이정윤,
        'stock': '우주항공', 'ticker': None, 'market': 'SECTOR',
        'mention_type': '결론', 'signal': '긍정', 'confidence': 'medium',
        'timestamp': '05:45',
        'key_quote': '우주항공 중소형주들이 움직임이 나오더라고요... 성장주 라인의 득세가 예상',
        'reasoning': '이정윤은 스페이스X 관련 모멘텀으로 우주항공 중소형주 득세 예상. 명확한 방향성 의견.'
    },
    {
        'video_id': v1, 'speaker_id': sp_이정윤,
        'stock': '화장품', 'ticker': None, 'market': 'SECTOR',
        'mention_type': '결론', 'signal': '긍정', 'confidence': 'medium',
        'timestamp': '07:00',
        'key_quote': '화장품 관련주들도 좀 지켜볼 필요가 있다. 미국에서 잘 팔리고 있고 일본-중국 관계 악화 호재',
        'reasoning': '이정윤은 K뷰티 미국 성장+중일 관계 악화로 인한 대체 수요를 호재로 언급. 화장품 섹터 긍정.'
    },
    {
        'video_id': v1, 'speaker_id': sp_이정윤,
        'stock': '삼성SDI', 'ticker': '006400', 'market': 'KR',
        'mention_type': '결론', 'signal': '긍정', 'confidence': 'medium',
        'timestamp': '11:30',
        'key_quote': '전고체 배터리 관련주들의 라인... 로봇과의 연관성이에요. 삼성SDI 어제 15% 올랐는데요',
        'reasoning': '이정윤은 2차전지가 전기차 → 로봇 배터리로 전환되며, 전고체 배터리(삼성SDI)가 로봇 연관성으로 상승 탄력이 있다고 긍정 평가.'
    },
    # VIDEO: Xv-wNA91EPE (조진표)
    {
        'video_id': v2, 'speaker_id': sp_조진표,
        'stock': '삼성전자', 'ticker': '005930', 'market': 'KR',
        'mention_type': '결론', 'signal': '긍정', 'confidence': 'high',
        'timestamp': '01:00',
        'key_quote': '20만 원이 새로운 랠리의 시작점이 아닐까라고 말씀드리고 싶습니다. AI 토탈 솔루션 기업으로 전환',
        'reasoning': '조진표는 삼성전자 목표주가 26~29만원, 영업이익 200~300조 전망, AI토탈솔루션 전환, 자사주 소각을 근거로 20만원을 랠리 시작점으로 긍정 평가.'
    }
]

print(f'INSERT할 시그널: {len(signals)}개')
inserted = 0
for sig in signals:
    if not sig['video_id'] or not sig['speaker_id']:
        print(f'  ⚠️ video_id 또는 speaker_id 없음: {sig["stock"]} (건너뜀)')
        continue
    r = requests.post(f'{URL}/rest/v1/influencer_signals', headers=H, json=sig)
    if r.status_code == 201:
        print(f'  ✅ INSERT: [{sig["signal"]}] {sig["stock"]}')
        inserted += 1
    else:
        print(f'  ❌ INSERT 실패: {r.status_code} {r.text[:200]}')

print(f'\n완료: 삭제 {deleted}개, INSERT {inserted}개')
