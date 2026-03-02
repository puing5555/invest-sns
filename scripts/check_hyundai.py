import os, requests
from dotenv import load_dotenv
load_dotenv('.env.local')
url = os.environ['NEXT_PUBLIC_SUPABASE_URL']
key = os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

# Check all signals with ticker 005380
r = requests.get(f"{url}/rest/v1/influencer_signals?select=id,stock,ticker,signal,key_quote,video_id&ticker=eq.005380", headers=headers)
for s in r.json():
    print(f"id={s['id'][:8]} stock={s['stock']} ticker={s['ticker']} signal={s['signal']}")
    print(f"  quote={s['key_quote'][:80] if s.get('key_quote') else 'N/A'}")
print(f"\nTotal: {len(r.json())}")

# Also check stock name variations
for name in ['현대차', '현대차그룹주']:
    r2 = requests.get(f"{url}/rest/v1/influencer_signals?select=id,stock,ticker&stock=eq.{name}", headers=headers)
    print(f"\nstock='{name}': {len(r2.json())}건")
    for s in r2.json():
        print(f"  {s['id'][:8]} ticker={s['ticker']}")
