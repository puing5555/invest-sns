import sys, io, os, requests, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env.local')
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
h = {'apikey': key, 'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'Prefer': 'return=minimal'}

with open('data/timestamp_correction_v2.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

for c in report['corrections']:
    sig_id = c['id']
    old_ts = c['old']
    new_ts = c['new']
    print(f"Rolling back {sig_id}: {new_ts} -> {old_ts}")
    r = requests.patch(f'{url}/rest/v1/influencer_signals?id=eq.{sig_id}', headers=h, json={'timestamp': old_ts})
    print(f"  Status: {r.status_code}")
