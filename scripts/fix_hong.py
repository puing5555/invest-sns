#!/usr/bin/env python3
"""Fix: create 홍선애 speaker and remap the 4 failed signals"""
import os, requests, json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env.local')

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
h = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

SAMPRO_CHANNEL = '4867e157-2126-4c67-aa5e-638372de8f03'

# 1. Delete the garbled test speaker if exists
r = requests.delete(f'{url}/rest/v1/speakers?name=eq.test_delete_me', headers=h)

# 2. Check if 홍선애 already exists (might be garbled)
r = requests.get(f'{url}/rest/v1/speakers?select=id,name', headers=h)
speakers = r.json()
hong_id = None
for s in speakers:
    if s['name'] == '홍선애':
        hong_id = s['id']
        break
    # Check for garbled version
    if 'ȫ' in s['name'] and len(s['name']) <= 5:
        # Delete garbled entry
        requests.delete(f'{url}/rest/v1/speakers?id=eq.{s["id"]}', headers=h)
        print(f"Deleted garbled speaker: {s['id']}")

if not hong_id:
    r = requests.post(f'{url}/rest/v1/speakers', headers=h, json={'name': '홍선애'})
    r.raise_for_status()
    hong_id = r.json()[0]['id']
    print(f'Created 홍선애: {hong_id}')
else:
    print(f'Found 홍선애: {hong_id}')

# 3. Get the 4 failed signal IDs and update them
failed_ids = [
    '55bf5a77-ff14-4c2b-9da8-a15c7a94ea74',
    '5a8d8634-625b-4e6a-b93b-47380dbe329c', 
    '19d07177-090a-4774-8504-38d177a8117d',
    '33078122-93ea-4001-83bd-58ee6dc8e4df',
]

for sig_id in failed_ids:
    r = requests.patch(
        f'{url}/rest/v1/influencer_signals?id=eq.{sig_id}',
        headers=h,
        json={'speaker_id': hong_id}
    )
    print(f'Updated {sig_id[:8]}: {r.status_code}')

# 4. The 2 "no name in title" signals - these are 김장열's own videos, keep as-is
print('\n김장열 본인 영상 2개 시그널은 변경 없음 (정상)')

# 5. Summary
print(f'\n완료! 홍선애 ID: {hong_id}')
print('총 변경: 17 + 4 = 21개 시그널 재매핑')
print('김장열 유지: 2 + 4(원래 김장열 맞는 것) = 6개')
