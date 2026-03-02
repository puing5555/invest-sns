import os, requests
from dotenv import load_dotenv
load_dotenv('C:/Users/Mario/work/invest-sns/.env.local')
url = os.environ['NEXT_PUBLIC_SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}
r = requests.get(
    f'{url}/rest/v1/influencer_videos?channel_id=eq.d68f8efd-64c8-4c07-9d34-e98c2954f4e1&select=video_id,title,published_at&order=published_at.desc&limit=15',
    headers=headers
)
for v in r.json():
    date = v['published_at'][:10] if v['published_at'] else 'N/A'
    title = v['title'][:60] if v['title'] else 'N/A'
    print(f"{date} | {v['video_id']} | {title}")
