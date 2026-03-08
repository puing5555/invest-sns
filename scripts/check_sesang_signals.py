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
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}'}

SESANG_CH = 'd68f8efd-64c8-4c07-9d34-e98c2954f4e1'

# 세상학개론 영상
r = requests.get(f'{URL}/rest/v1/influencer_videos?channel_id=eq.{SESANG_CH}&select=id,video_id,title&limit=50', headers=H)
videos = r.json()
print(f'세상학개론 영상: {len(videos)}개')
vid_map = {}  # youtube_video_id -> db_uuid
for v in videos:
    vid_map[v['video_id']] = v['id']
    print(f"  {v['video_id']} | {v['title'][:60] if v['title'] else 'N/A'}")

print()

# 세상학개론 시그널 (video_id를 통해 필터)
sesang_vid_uuids = [v['id'] for v in videos]
if sesang_vid_uuids:
    uuids_str = ','.join(sesang_vid_uuids)
    r2 = requests.get(
        f'{URL}/rest/v1/influencer_signals?video_id=in.({uuids_str})&select=id,stock,signal,confidence,video_id,speaker_id',
        headers=H
    )
    sigs = r2.json()
    print(f'세상학개론 기존 시그널: {len(sigs)}개')
    for s in sigs:
        print(f"  ID:{s['id'][:8]}... [{s['signal']}] {s['stock']} | vid:{s['video_id'][:8]}...")

print()
# 이정윤, 조진표 speaker 확인
for name in ['이정윤', '조진표', '이정원']:
    r3 = requests.get(f'{URL}/rest/v1/influencer_speakers?name=ilike.*{name}*&select=id,name', headers=H)
    print(f'Speaker "{name}": {r3.text[:200]}')

# 8Nn3qerCt44 영상 DB ID
target_vids = ['8Nn3qerCt44', 'Xv-wNA91EPE']
for yt_id in target_vids:
    if yt_id in vid_map:
        print(f'{yt_id} DB UUID: {vid_map[yt_id]}')
    else:
        print(f'{yt_id}: DB에 없음 - 등록 필요')
