import urllib.request, json, os

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

# Check influencer_channels columns
req = urllib.request.Request(f'{URL}/rest/v1/influencer_channels?select=*&limit=2', headers=H)
resp = urllib.request.urlopen(req)
data = json.loads(resp.read().decode())
if data:
    print("influencer_channels columns:", list(data[0].keys()))
    print("Sample:", json.dumps(data[0], ensure_ascii=False, indent=2))

# Check speakers columns
req2 = urllib.request.Request(f'{URL}/rest/v1/speakers?select=*&limit=3', headers=H)
resp2 = urllib.request.urlopen(req2)
data2 = json.loads(resp2.read().decode())
if data2:
    print("\nspeakers columns:", list(data2[0].keys()))
    print("Sample:", json.dumps(data2[0], ensure_ascii=False, indent=2))
