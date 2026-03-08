import urllib.request, json

url = 'https://arypzhotxflimroprmdk.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
h = {'apikey': key, 'Authorization': f'Bearer {key}'}
CHANNEL_ID = '227ad970-4f05-4fea-9a94-90f9649ca714'

def fetch(ep):
    req = urllib.request.Request(f'{url}/rest/v1/{ep}', headers=h)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# channel info
ch = fetch(f'influencer_channels?id=eq.{CHANNEL_ID}&select=id,channel_name,channel_handle')
print(f'채널명: {ch[0]["channel_name"]} ({ch[0]["channel_handle"]})')

# videos
vids = fetch(f'influencer_videos?channel_id=eq.{CHANNEL_ID}&select=video_id,title&order=created_at.desc&limit=10')
print(f'\n최근 영상 {len(vids)}개:')
ytid_count = 0
for v in vids:
    is_ytid = v.get('title') == v.get('video_id')
    if is_ytid:
        ytid_count += 1
    label = 'X YT_ID' if is_ytid else 'O 한글'
    print(f'  [{label}] {v.get("title", "")}')

# count all videos
all_vids = fetch(f'influencer_videos?channel_id=eq.{CHANNEL_ID}&select=video_id,title&limit=500')
total = len(all_vids)
ytid_as_title = sum(1 for v in all_vids if v.get('title') == v.get('video_id'))
print(f'\n전체 영상: {total}개')
print(f'YouTube ID=제목 (문제): {ytid_as_title}개')
print(f'정상 한글 제목: {total - ytid_as_title}개')
