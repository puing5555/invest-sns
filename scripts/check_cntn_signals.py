import urllib.request, json, urllib.parse
from pathlib import Path

env_file = Path(__file__).parent.parent / '.env.local'
env = {}
for line in env_file.read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip()

URL = env['NEXT_PUBLIC_SUPABASE_URL']
KEY = env['NEXT_PUBLIC_SUPABASE_ANON_KEY']

# CNTN 시그널 조회
api_url = URL + '/rest/v1/influencer_signals?select=id,stock,signal_date,channel_name&stock=eq.CNTN&limit=20'
req = urllib.request.Request(api_url, headers={'apikey': KEY, 'Authorization': 'Bearer ' + KEY})
with urllib.request.urlopen(req, timeout=15) as r:
    signals = json.loads(r.read())

print('CNTN 시그널 수:', len(signals))
for s in signals:
    print(s['id'][:8], '|', s['stock'], '|', s['signal_date'], '|', s['channel_name'])
