import urllib.request, json

url = 'https://arypzhotxflimroprmdk.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
h = {'apikey': key, 'Authorization': f'Bearer {key}', 'Range': '0-499', 'Prefer': 'count=exact'}

def fetch(ep, use_range=False):
    hdrs = dict(h) if use_range else {'apikey': key, 'Authorization': f'Bearer {key}'}
    req = urllib.request.Request(f'{url}/rest/v1/{ep}', headers=hdrs)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except Exception as e:
        return f"ERROR: {e}"

CHANNEL_ID = '227ad970-4f05-4fea-9a94-90f9649ca714'

# 비디오 UUID 하나로 시그널 조회
vid_uuid = 'daa02849-d7ca-428e-9cf2-cebd076886d5'
r1 = fetch(f'influencer_signals?video_id=eq.{vid_uuid}&select=id,timestamp_seconds,stock&limit=10')
print(f"UUID 방식: {r1}")

# 시그널 전체에서 컬럼 확인 (Range 사용)
r2 = fetch('influencer_signals?select=id,video_id,timestamp_seconds,stock&limit=3&order=id', use_range=True)
print(f"\n시그널 샘플(Range): {r2}")

# GODofIT 채널 전체 시그널 - speaker나 channel로 필터 시도
# speakers 테이블 확인
r3 = fetch('speakers?channel_handle=eq.@GODofIT&select=id,name&limit=5')
print(f"\nspeakers @GODofIT: {r3}")

r4 = fetch('speakers?name=ilike.*GOD*&select=id,name&limit=5')
print(f"speakers GOD 검색: {r4}")
