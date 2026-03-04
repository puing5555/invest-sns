import urllib.request, json, os, urllib.parse

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

def get(table, params=''):
    req = urllib.request.Request(f'{URL}/rest/v1/{table}?{params}', headers=H)
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read().decode())

# Find 이효석아카데미 channel
ch = get('influencer_channels', 'channel_name=eq.' + urllib.parse.quote('이효석아카데미') + '&select=id,channel_name')
print("Channel:", json.dumps(ch, ensure_ascii=False))

# Find 이효석 speaker
sp = get('speakers', 'name=eq.' + urllib.parse.quote('이효석') + '&select=*')
print("Speaker:", json.dumps(sp, ensure_ascii=False))

# Check influencer_signals columns
sig = get('influencer_signals', 'select=*&limit=1')
if sig:
    print("\ninfluencer_signals columns:", list(sig[0].keys()))

# Check influencer_videos columns  
vid = get('influencer_videos', 'select=*&limit=1')
if vid:
    print("\ninfluencer_videos columns:", list(vid[0].keys()))
