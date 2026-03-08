import urllib.request, json, urllib.parse

url = 'https://arypzhotxflimroprmdk.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

CHANNEL_ID = '227ad970-4f05-4fea-9a94-90f9649ca714'

def fetch(endpoint):
    req = urllib.request.Request(f'{url}/rest/v1/{endpoint}', headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# influencer_signals에서 video foreign key join으로 채널 필터
# select with embedded filter: influencer_videos!inner(channel_id)
encoded_ch = urllib.parse.quote(CHANNEL_ID)
endpoint = (
    f'influencer_signals'
    f'?select=id,timestamp_seconds,stock'
    f'&influencer_videos.channel_id=eq.{encoded_ch}'
    f'&limit=1000'
)
# 대안: videos 먼저 가져오고 video_id로 직접 쿼리 (단건씩)
# 더 좋은 방법: video 테이블에서 channel_id 기준으로 JOIN
endpoint2 = (
    f'influencer_signals'
    f'?select=id,timestamp_seconds,stock,influencer_videos!inner(channel_id)'
    f'&influencer_videos.channel_id=eq.{CHANNEL_ID}'
    f'&limit=1000'
)
print("엔드포인트:", endpoint2)
try:
    all_sigs = fetch(endpoint2)
    print(f'JOIN 방식 결과: {len(all_sigs)}')
except Exception as e:
    print(f'JOIN 방식 실패: {e}')
    # 폴백: 비디오 ID 하나씩 (느리지만 확실)
    vids = fetch(f'influencer_videos?channel_id=eq.{CHANNEL_ID}&select=id&limit=500')
    print(f'비디오: {len(vids)}')
    all_sigs = []
    for v in vids:
        try:
            s = fetch(f'influencer_signals?video_id=eq.{v["id"]}&select=id,timestamp_seconds,stock&limit=100')
            all_sigs.extend(s)
        except:
            pass
    print(f'총 시그널 (폴백): {len(all_sigs)}')

zero = [s for s in all_sigs if not s.get('timestamp_seconds') or s['timestamp_seconds'] == 0]
nonzero = [s for s in all_sigs if s.get('timestamp_seconds') and s['timestamp_seconds'] > 0]
total = len(all_sigs)
pct_zero = round(len(zero)/total*100,1) if total else 0
pct_nz = round(len(nonzero)/total*100,1) if total else 0
print(f'\n==== 분석 결과 ====')
print(f'총 시그널: {total}')
print(f'0초/null: {len(zero)} ({pct_zero}%)')
print(f'유효(>0): {len(nonzero)} ({pct_nz}%)')
if nonzero:
    print('유효 예시:')
    for s in nonzero[:5]:
        print(f"  stock={s['stock']} ts={s['timestamp_seconds']}")
