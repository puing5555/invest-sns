import os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import requests
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path('.env.local'))
SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
HEADERS = {'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}'}
CHANNEL_ID = '227ad970-4f05-4fea-9a94-90f9649ca714'

resp = requests.get(f'{SUPABASE_URL}/rest/v1/influencer_channels?id=eq.{CHANNEL_ID}&select=id,channel_name,channel_handle', headers=HEADERS)
print('채널:', resp.json())

resp2 = requests.get(f'{SUPABASE_URL}/rest/v1/influencer_videos?channel_id=eq.{CHANNEL_ID}&select=video_id,title&limit=5', headers=HEADERS)
for v in resp2.json():
    vid = v['video_id']
    title = v['title'][:60]
    print(f'  {vid} -> {title}')
