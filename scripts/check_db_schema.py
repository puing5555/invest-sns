import sys, io, os, requests, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env.local')
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
h = {'apikey': key, 'Authorization': f'Bearer {key}'}

# Check tables
for t in ['speakers', 'influencer_speakers', 'influencer_channels', 'influencer_videos', 'influencer_signals']:
    r = requests.get(f"{url}/rest/v1/{t}?select=*&limit=1", headers=h)
    if r.ok:
        data = r.json()
        cols = list(data[0].keys()) if data else "empty table"
        print(f"[OK] {t}: {cols}")
    else:
        print(f"[NO] {t}: {r.status_code}")

# Show existing channels
r = requests.get(f"{url}/rest/v1/influencer_channels?select=id,channel_name", headers=h)
if r.ok:
    print("\nExisting channels:")
    for ch in r.json():
        print(f"  {ch['id'][:8]}... = {ch['channel_name']}")

# Show existing speakers from signals
r = requests.get(f"{url}/rest/v1/influencer_signals?select=speaker_id&limit=5", headers=h)
if r.ok:
    speaker_ids = set(s['speaker_id'] for s in r.json() if s.get('speaker_id'))
    print(f"\nUnique speaker_ids in signals: {speaker_ids}")
