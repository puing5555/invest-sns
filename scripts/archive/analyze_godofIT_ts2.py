import urllib.request, json

url = 'https://arypzhotxflimroprmdk.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
h = {'apikey': key, 'Authorization': f'Bearer {key}'}

def fetch(ep):
    req = urllib.request.Request(f'{url}/rest/v1/{ep}', headers=h)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

CHANNEL_ID = '227ad970-4f05-4fea-9a94-90f9649ca714'

# 비디오 샘플 1개 확인 (UUID + video_id)
vids = fetch(f'influencer_videos?channel_id=eq.{CHANNEL_ID}&select=id,video_id,title&limit=3')
print("비디오 샘플:")
for v in vids:
    print(f"  UUID={v['id']} | yt_id={v.get('video_id')} | title={v.get('title','')[:40]}")

# 시그널 샘플 - 전체에서 video_id 타입 확인
sigs_sample = fetch('influencer_signals?select=id,video_id,timestamp_seconds,stock&limit=5')
print("\n시그널 샘플:")
for s in sigs_sample:
    print(f"  sig_id={s['id'][:8]}... | video_id={s.get('video_id')} | ts={s.get('timestamp_seconds')} | stock={s.get('stock')}")

# 비디오 UUID로 시그널 조회
if vids:
    vid_uuid = vids[0]['id']
    sig_by_uuid = fetch(f'influencer_signals?video_id=eq.{vid_uuid}&select=id,timestamp_seconds,stock&limit=5')
    print(f"\nUUID({vid_uuid[:8]}...)로 시그널: {len(sig_by_uuid)}")
    
    vid_ytid = vids[0].get('video_id')
    if vid_ytid:
        sig_by_ytid = fetch(f'influencer_signals?video_id=eq.{vid_ytid}&select=id,timestamp_seconds,stock&limit=5')
        print(f"YouTube ID({vid_ytid})로 시그널: {len(sig_by_ytid)}")
        if sig_by_ytid:
            print("  =>", sig_by_ytid[:2])
