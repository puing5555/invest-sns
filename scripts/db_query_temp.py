# -*- coding: utf-8 -*-
import os, sys, requests
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))

BASE = os.environ['NEXT_PUBLIC_SUPABASE_URL']
KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Accept': 'application/json',
     'Content-Type': 'application/json', 'Prefer': 'return=representation'}

# UPDATE 삼프로TV → interview
r = requests.patch(
    f'{BASE}/rest/v1/influencer_channels?channel_name=eq.%EC%82%BC%ED%94%84%EB%A1%9CTV',
    headers=H,
    json={'channel_type': 'interview'}
)
print(f'UPDATE status: {r.status_code}')
updated = r.json()
if updated:
    print(f'  → {updated[0].get("channel_name")} = {updated[0].get("channel_type")}')

# SELECT 전체 확인
r2 = requests.get(
    f'{BASE}/rest/v1/influencer_channels?select=channel_name,channel_type&order=channel_name.asc',
    headers=H
)
print('\nSELECT channel_name, channel_type:')
print(f'  {"채널명":<30} {"channel_type"}')
print('  ' + '-' * 45)
for row in r2.json():
    ct = row.get('channel_type') or 'NULL'
    marker = ' ← interview' if ct == 'interview' else ''
    print(f'  {row["channel_name"]:<30} {ct}{marker}')
