import sys, os, requests, json
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env.local')
url = os.environ['NEXT_PUBLIC_SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
h = {'apikey': key, 'Authorization': f'Bearer {key}'}
r = requests.get(f'{url}/rest/v1/influencer_channels?select=channel_name,channel_handle,channel_url', headers=h)
for c in r.json():
    print(f"{c['channel_name']} | {c.get('channel_handle','')} | {c.get('channel_url','')}")
