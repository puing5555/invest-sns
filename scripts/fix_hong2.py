# -*- coding: utf-8 -*-
"""Fix 홍선애 speaker name encoding"""
import os, sys, requests
from pathlib import Path
from dotenv import load_dotenv

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv(Path(__file__).parent.parent / '.env.local')
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
h = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json; charset=utf-8',
    'Prefer': 'return=representation'
}

# Delete garbled entry
r = requests.delete(f'{url}/rest/v1/speakers?id=eq.380a7535-0ba3-4a05-b7bd-fef1dd6f90b1', headers=h)
print(f'Deleted garbled: {r.status_code}')

# Create with proper UTF-8 name
name = '\ud64d\uc120\uc560'  # 홍선애
r = requests.post(f'{url}/rest/v1/speakers', headers=h, json={'name': name})
print(f'Created: {r.status_code}')
if r.ok:
    new_id = r.json()[0]['id']
    print(f'New ID: {new_id}')
    
    # Verify
    r2 = requests.get(f'{url}/rest/v1/speakers?id=eq.{new_id}&select=id,name', headers=h)
    print(f'Verify: {repr(r2.json()[0]["name"])}')
    
    # Update the 4 signals
    for sig_id in ['55bf5a77-ff14-4c2b-9da8-a15c7a94ea74','5a8d8634-625b-4e6a-b93b-47380dbe329c','19d07177-090a-4774-8504-38d177a8117d','33078122-93ea-4001-83bd-58ee6dc8e4df']:
        r3 = requests.patch(f'{url}/rest/v1/influencer_signals?id=eq.{sig_id}', headers=h, json={'speaker_id': new_id})
        print(f'Updated {sig_id[:8]}: {r3.status_code}')
