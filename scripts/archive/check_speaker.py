import sys, os, requests, json
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env.local')
url = os.environ['NEXT_PUBLIC_SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
h = {'apikey': key, 'Authorization': f'Bearer {key}'}
r = requests.get(f'{url}/rest/v1/speakers?channel_id=eq.d68f8efd-64c8-4c07-9d34-e98c2954f4e1&select=*', headers=h)
print(json.dumps(r.json(), ensure_ascii=False, indent=2))
# Also check with no filter
r2 = requests.get(f'{url}/rest/v1/speakers?select=id,name,channel_id&limit=20', headers=h)
for s in r2.json():
    print(f"{s['name']} | {s['id']} | ch:{s.get('channel_id')}")
