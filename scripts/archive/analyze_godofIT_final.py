import urllib.request, json

url = 'https://arypzhotxflimroprmdk.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
h = {'apikey': key, 'Authorization': f'Bearer {key}'}

def fetch(ep):
    req = urllib.request.Request(f'{url}/rest/v1/{ep}', headers=h)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

CHANNEL_ID = '227ad970-4f05-4fea-9a94-90f9649ca714'

# GODofIT 비디오 (모두)
vids = fetch(f'influencer_videos?channel_id=eq.{CHANNEL_ID}&select=id,video_id,title&limit=500')
print(f'비디오 수: {len(vids)}')

# 제목 확인 (YouTube ID가 제목으로 들어갔는지)
ytid_as_title = [v for v in vids if v.get('title') == v.get('video_id')]
print(f'제목=YouTube ID (비어있는 제목): {len(ytid_as_title)}개')
print(f'제목 정상: {len(vids)-len(ytid_as_title)}개')

# 시그널을 비디오 하나씩 가져오기
all_sigs = []
for v in vids:
    try:
        s = fetch(f'influencer_signals?video_id=eq.{v["id"]}&select=id,timestamp,stock,signal&limit=200')
        all_sigs.extend(s)
    except:
        pass

print(f'\n총 시그널: {len(all_sigs)}')

# timestamp 분석
zero_ts = [s for s in all_sigs if not s.get('timestamp') or s['timestamp'] in ('0:00', '00:00', '0', '')]
valid_ts = [s for s in all_sigs if s.get('timestamp') and s['timestamp'] not in ('0:00', '00:00', '0', '')]

print(f'0:00/빈값: {len(zero_ts)} ({round(len(zero_ts)/len(all_sigs)*100,1) if all_sigs else 0}%)')
print(f'유효 타임스탬프: {len(valid_ts)} ({round(len(valid_ts)/len(all_sigs)*100,1) if all_sigs else 0}%)')

if valid_ts:
    print('\n유효 타임스탬프 예시:')
    for s in valid_ts[:5]:
        print(f"  stock={s['stock']} | ts={s['timestamp']} | signal={s['signal']}")

if zero_ts:
    print('\n0:00 타임스탬프 예시:')
    for s in zero_ts[:5]:
        print(f"  stock={s['stock']} | ts={repr(s['timestamp'])} | signal={s['signal']}")

# pipeline_version 분포
pv_dist = {}
for s in all_sigs:
    pv = 'unknown'
    pv_dist[pv] = pv_dist.get(pv, 0) + 1

# 더 상세히: pipeline version
all_sigs2 = []
for v in vids[:20]:  # 샘플 20개만
    try:
        s = fetch(f'influencer_signals?video_id=eq.{v["id"]}&select=id,timestamp,stock,pipeline_version&limit=200')
        all_sigs2.extend(s)
    except:
        pass

pv_dist = {}
for s in all_sigs2:
    pv = s.get('pipeline_version', 'unknown')
    pv_dist[pv] = pv_dist.get(pv, 0) + 1

print(f'\n파이프라인 버전 분포 (샘플 20 비디오):')
for k, v in sorted(pv_dist.items()):
    print(f'  {k}: {v}건')
