# -*- coding: utf-8 -*-
import requests
import json
import sys

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

env = {}
with open('.env.local', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v

base_url = env['NEXT_PUBLIC_SUPABASE_URL'] + '/rest/v1'
headers = {
    'apikey': env['SUPABASE_SERVICE_ROLE_KEY'],
    'Authorization': 'Bearer ' + env['SUPABASE_SERVICE_ROLE_KEY'],
    'Content-Type': 'application/json; charset=utf-8',
    'Prefer': 'return=representation'
}

channel_name = '안경투 (안유화의 경제투자론)'
channel_id = '6d6817ca-76ab-484e-ad7e-b537921c3d25'

# Update the channel_name with correct encoding
update_resp = requests.patch(
    base_url + '/influencer_channels',
    headers=headers,
    params={'id': f'eq.{channel_id}'},
    data=json.dumps({'channel_name': channel_name}, ensure_ascii=False).encode('utf-8')
)
print('Update status:', update_resp.status_code)

# Verify
resp = requests.get(
    base_url + '/influencer_channels',
    headers=headers,
    params={'channel_handle': 'eq.anyuhuatv', 'select': 'id,channel_name,channel_handle,platform'}
)
data = resp.json()
print('Verified channel_name:', data[0]['channel_name'] if data else 'NOT FOUND')
print('Channel ID:', data[0]['id'] if data else 'N/A')
