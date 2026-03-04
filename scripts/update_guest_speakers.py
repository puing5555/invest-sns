"""
게스트 스피커 DB 등록 + 시그널 speaker_id UPDATE
"""
import json, os, urllib.request, urllib.parse, sys, io
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
HEADERS = {
    'apikey': KEY,
    'Authorization': f'Bearer {KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def api(method, table, params='', data=None, extra_headers=None):
    url = f"{URL}/rest/v1/{table}?{params}"
    body = json.dumps(data).encode() if data else None
    h = {**HEADERS}
    if extra_headers:
        h.update(extra_headers)
    req = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode()
            return json.loads(content) if content else []
    except urllib.error.HTTPError as e:
        print(f"ERROR {e.code}: {e.read().decode()}")
        raise

def api_count(table, params=''):
    url = f"{URL}/rest/v1/{table}?{params}&select=id"
    h = {**HEADERS, 'Prefer': 'count=exact', 'Range-Unit': 'items', 'Range': '0-0'}
    req = urllib.request.Request(url, headers=h, method='GET')
    with urllib.request.urlopen(req) as resp:
        cr = resp.headers.get('Content-Range', '')
        if '/' in cr:
            return int(cr.split('/')[1])
        return 0

# Load guest data
with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'hs_guest_signals_v2.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

guests = data['guests']
print(f"게스트 수: {len(guests)}, 총 시그널: {data['summary']['total_affected_signals']}")

# 이효석 speaker_id
hs_speaker_id = 'b07d8758-493a-4a51-9bc5-7ef75f0be67c'
print(f"이효석 speaker_id: {hs_speaker_id}")

# Before count
before_count = api_count('influencer_signals', f'speaker_id=eq.{hs_speaker_id}')
print(f"\n[BEFORE] 이효석 시그널 수: {before_count}")

# Step 1: 게스트 스피커 등록
print("\n=== Step 1: 게스트 스피커 등록 ===")
guest_names = [g['name'] for g in guests]
speaker_map = {}

# Get all existing speakers
existing = api('GET', 'speakers', 'select=id,name&limit=1000')
existing_by_name = {s['name']: s['id'] for s in existing}

for n in guest_names:
    if n in existing_by_name:
        speaker_map[n] = existing_by_name[n]

print(f"이미 존재하는 스피커: {len(speaker_map)}명")

# Insert new
new_names = [n for n in guest_names if n not in speaker_map]
if new_names:
    rows = [{'name': n} for n in new_names]
    result = api('POST', 'speakers', '', rows)
    for s in result:
        speaker_map[s['name']] = s['id']
    print(f"새로 등록: {len(result)}명")
else:
    print("새로 등록할 스피커 없음")

print(f"총 매핑된 스피커: {len(speaker_map)}명")

# Step 2: 시그널 speaker_id UPDATE
print("\n=== Step 2: 시그널 speaker_id UPDATE ===")
total_updated = 0
issues = []

for guest in guests:
    name = guest['name']
    speaker_id = speaker_map.get(name)
    if not speaker_id:
        issues.append(f"{name}: speaker_id 없음")
        continue
    
    video_ids = [v['video_id'] for v in guest['videos']]
    expected = sum(v['signal_count'] for v in guest['videos'])
    
    updated_count = 0
    for vid in video_ids:
        result = api('PATCH', 'influencer_signals',
            f'video_id=eq.{vid}&speaker_id=eq.{hs_speaker_id}',
            {'speaker_id': speaker_id})
        updated_count += len(result)
    
    total_updated += updated_count
    status = "✓" if updated_count == expected else "⚠"
    if updated_count != expected:
        issues.append(f"{name}: expected {expected}, got {updated_count}")
    print(f"  {status} {name}: {updated_count}/{expected}")

print(f"\n총 UPDATE: {total_updated}개")

# Step 3: 검증
print("\n=== Step 3: 검증 ===")
after_count = api_count('influencer_signals', f'speaker_id=eq.{hs_speaker_id}')
print(f"[AFTER] 이효석 시그널 수: {after_count}")
print(f"감소량: {before_count - after_count} (기대: 242)")

# 게스트별 시그널 합계
guest_total = 0
for guest in guests:
    name = guest['name']
    sid = speaker_map.get(name)
    if sid:
        cnt = api_count('influencer_signals', f'speaker_id=eq.{sid}')
        guest_total += cnt

print(f"게스트별 시그널 합계: {guest_total}")

if issues:
    print(f"\n⚠ 이슈 {len(issues)}건:")
    for i in issues:
        print(f"  - {i}")
else:
    print("\n✅ 이슈 없음")

print("\n=== 완료 ===")
