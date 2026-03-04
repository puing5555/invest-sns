import json, os, urllib.request, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

env = {}
with open(os.path.join(os.path.dirname(__file__), '..', '.env.local'), 'r') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v

URL = env['NEXT_PUBLIC_SUPABASE_URL']
KEY = env['SUPABASE_SERVICE_ROLE_KEY']
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}'}

def get(path):
    req = urllib.request.Request(f'{URL}/rest/v1/{path}', headers=H)
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read().decode())

with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'hs_guest_signals_v2.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

# 이형수의 첫 번째 video_id 확인
hs_guest = [g for g in data['guests'] if g['name'] == '이형수'][0]
vid = hs_guest['videos'][0]['video_id']
print(f"이형수 첫 video_id: {vid}")

# 해당 video의 시그널 확인
sigs = get(f'influencer_signals?video_id=eq.{vid}&select=id,speaker_id&limit=5')
print(f"시그널 수: {len(sigs)}")
for s in sigs:
    print(f"  signal {s['id'][:8]}... speaker_id={s['speaker_id']}")

# 이형수 speaker 확인
from urllib.parse import quote
sp = get(f'speakers?name=eq.{quote("이형수")}&select=id,name')
print(f"\n이형수 speaker: {json.dumps(sp, ensure_ascii=False)}")

# 이형수 speaker_id로 시그널 검색
if sp:
    sid = sp[0]['id']
    h2 = {**H, 'Prefer': 'count=exact', 'Range-Unit': 'items', 'Range': '0-0'}
    req = urllib.request.Request(f'{URL}/rest/v1/influencer_signals?speaker_id=eq.{sid}&select=id', headers=h2)
    resp = urllib.request.urlopen(req)
    cr = resp.headers.get('Content-Range', '')
    print(f"이형수 시그널 수 (이미 할당됨): {cr}")
