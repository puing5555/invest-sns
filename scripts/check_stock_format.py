import os, requests, re
from dotenv import load_dotenv
load_dotenv('.env.local')
url = os.environ['NEXT_PUBLIC_SUPABASE_URL']
key = os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

# Get all signals
r = requests.get(f"{url}/rest/v1/influencer_signals?select=id,stock,ticker&limit=200", headers=headers)
data = r.json()

# Find stocks that contain parenthesized ticker
has_paren = [s for s in data if s.get('stock') and re.search(r'\s*\(.*\)', s['stock'])]
print(f"Stock values containing parentheses: {len(has_paren)}")
for s in has_paren:
    print(f"  {s['id'][:8]} stock='{s['stock']}' ticker={s['ticker']}")

# Find 현대차그룹주
hyundai = [s for s in data if s.get('stock') and '그룹' in s['stock']]
print(f"\nStock containing '그룹': {len(hyundai)}")
for s in hyundai:
    print(f"  {s['id'][:8]} stock='{s['stock']}' ticker={s['ticker']}")
