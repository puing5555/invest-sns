import requests

url = 'https://arypzhotxflimroprmdk.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
headers = {'apikey': key, 'Authorization': f'Bearer {key}', 'Prefer': 'count=exact'}

# 안유화 채널 영상 목록
resp = requests.get(f'{url}/rest/v1/influencer_videos?channel_id=eq.6d6817ca-76ab-484e-ad7e-b537921c3d25&select=id&limit=1000', headers=headers)
videos = resp.json()
video_ids = [v['id'] for v in videos]
print(f'안유화 영상 수: {len(video_ids)}')

# 시그널 수 계산
total_signals = 0
for vid in video_ids:
    resp2 = requests.get(f'{url}/rest/v1/influencer_signals?video_id=eq.{vid}&select=id&limit=1', headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Prefer': 'count=exact'})
    cr = resp2.headers.get('Content-Range', '0/0')
    try:
        cnt = int(cr.split('/')[1])
        total_signals += cnt
    except:
        pass

print(f'안유화 총 시그널 수: {total_signals}')

# 전체 시그널
resp3 = requests.get(f'{url}/rest/v1/influencer_signals?select=id&limit=1', headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Prefer': 'count=exact'})
cr3 = resp3.headers.get('Content-Range', 'unknown')
print(f'전체 시그널 수: {cr3}')
