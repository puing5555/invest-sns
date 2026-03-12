# -*- coding: utf-8 -*-
import sys, requests, json
sys.stdout.reconfigure(encoding='utf-8')

env = {}
with open('.env.local') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

key = env.get('SUPABASE_SERVICE_ROLE_KEY', '')
h = {'apikey': key, 'Authorization': 'Bearer ' + key}
SUPA = 'https://arypzhotxflimroprmdk.supabase.co'

r = requests.get(f'{SUPA}/rest/v1/influencer_signals?limit=1&select=*', headers=h)
data = r.json()
print('Status:', r.status_code)
if data:
    print('Columns:', list(data[0].keys()))

# Join으로 코린이아빠 시그널 가져오기
r2 = requests.get(
    f'{SUPA}/rest/v1/influencer_signals?select=id,stock,ticker,signal,'
    f'influencer_videos!inner(channel_id,influencer_channels!inner(channel_name))'
    f'&influencer_videos.influencer_channels.channel_name=eq.코린이 아빠&limit=50',
    headers=h
)
print('Join query status:', r2.status_code)
print(r2.text[:500])
