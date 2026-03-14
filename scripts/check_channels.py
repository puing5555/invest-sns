import os, requests, json
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))

url = os.environ['NEXT_PUBLIC_SUPABASE_URL'] + '/rest/v1/influencer_channels?select=*&order=created_at.asc'
headers = {
    'apikey': os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY'],
    'Authorization': 'Bearer ' + os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY'],
    'Accept': 'application/json'
}
r = requests.get(url, headers=headers)
channels = r.json()
print(f'Total channels: {len(channels)}')
for c in channels:
    print(json.dumps(c, ensure_ascii=False, indent=2))
    print('---')
