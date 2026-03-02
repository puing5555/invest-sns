import os, requests
from dotenv import load_dotenv
load_dotenv('.env.local')
url = os.environ['NEXT_PUBLIC_SUPABASE_URL']
key = os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
skey = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', key)
headers = {'apikey': skey, 'Authorization': f'Bearer {skey}', 'Content-Type': 'application/json', 'Prefer': 'return=representation'}

r = requests.patch(
    f"{url}/rest/v1/influencer_signals?stock=eq.마이크로스트라이즈",
    headers=headers,
    json={'stock': '마이크로스트래티지'}
)
print(f"Status: {r.status_code}, Updated: {len(r.json())} rows")
for s in r.json():
    print(f"  {s['id'][:8]} stock={s['stock']} ticker={s['ticker']}")
