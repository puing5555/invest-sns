"""이효석아카데미 시그널 분석 - 빈 레코드, TSMC 중복, published_at 없는 것"""
from dotenv import load_dotenv
import os, requests, json
from collections import defaultdict

load_dotenv('.env.local')
URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
headers = {'apikey': KEY, 'Authorization': f'Bearer {KEY}'}

HYOSEOK_CHANNEL_ID = 'd153b75b-1843-4a99-b49f-c31081a8f566'

# 이효석아카데미 videos 전체
all_videos = []
offset = 0
while True:
    r = requests.get(
        f'{URL}/rest/v1/influencer_videos?channel_id=eq.{HYOSEOK_CHANNEL_ID}'
        f'&select=id,video_id,published_at&offset={offset}&limit=500',
        headers=headers
    )
    batch = r.json()
    if not isinstance(batch, list) or not batch:
        break
    all_videos.extend(batch)
    if len(batch) < 500:
        break
    offset += 500

print(f'이효석아카데미 videos: {len(all_videos)}건')
vid_ids = [v['id'] for v in all_videos]
video_pub_map = {v['id']: v['published_at'] for v in all_videos}

# 이효석아카데미의 시그널 가져오기 (배치로)
all_signals = []
batch_size = 100
for i in range(0, len(vid_ids), batch_size):
    batch = vid_ids[i:i+batch_size]
    vid_list = ','.join(batch)
    r = requests.get(
        f'{URL}/rest/v1/influencer_signals?video_id=in.({vid_list})'
        f'&select=id,video_id,stock,ticker,signal,key_quote,reasoning,created_at',
        headers=headers
    )
    data = r.json()
    if isinstance(data, list):
        all_signals.extend(data)

print(f'이효석 시그널 총: {len(all_signals)}건')

# 빈 레코드 찾기
blank = []
for s in all_signals:
    is_blank = (
        not s.get('signal') or s.get('signal', '').strip() == '' or
        (not s.get('stock') or s.get('stock', '').strip() == '') or
        (not s.get('key_quote') or s.get('key_quote', '').strip() == '')
    )
    if is_blank:
        blank.append(s)

print(f'\n빈/불완전 레코드: {len(blank)}건')
for b in blank[:10]:
    print(json.dumps(b, ensure_ascii=False))

# TSMC 중복 찾기
tsm_sigs = [s for s in all_signals if s.get('ticker') == 'TSM' or 'TSM' in str(s.get('stock', '')).upper()]
print(f'\nTSMC 시그널: {len(tsm_sigs)}건')
tsm_by_video = defaultdict(list)
for s in tsm_sigs:
    tsm_by_video[s['video_id']].append(s)

dup_count = 0
for vid_id, sigs in tsm_by_video.items():
    if len(sigs) > 1:
        dup_count += 1
        print(f'중복 video_id={vid_id}:')
        for s in sigs:
            pub = video_pub_map.get(s['video_id'], 'N/A')
            print(f'  id={s["id"]}, signal={s.get("signal")}, created={s["created_at"]}')

print(f'\nTSMC 중복 video: {dup_count}건')

# published_at이 필요한 레코드 확인 (created_at 기준)
# signals의 created_at vs video의 published_at 비교
print('\n=== published_at 현황 ===')
needs_update = 0
for s in all_signals:
    vid_pub = video_pub_map.get(s['video_id'])
    sig_created = s['created_at']
    # signal이 video 업로드 날짜와 다른 경우
    if vid_pub:
        v_date = vid_pub[:10]  # YYYY-MM-DD
        s_date = sig_created[:10]
        if v_date != s_date:
            needs_update += 1

print(f'video published_at과 signal created_at이 다른 건수: {needs_update}')
print(f'샘플 5건:')
count = 0
for s in all_signals:
    vid_pub = video_pub_map.get(s['video_id'])
    if vid_pub:
        v_date = vid_pub[:10]
        s_date = s['created_at'][:10]
        if v_date != s_date:
            print(f'  id={s["id"][:8]}... signal_created={s_date}, video_published={v_date}')
            count += 1
            if count >= 5:
                break
