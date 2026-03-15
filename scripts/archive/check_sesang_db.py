import sys, os, requests
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env.local')

url = os.environ['NEXT_PUBLIC_SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
h = {'apikey': key, 'Authorization': f'Bearer {key}'}

# Check existing videos
r = requests.get(f'{url}/rest/v1/influencer_videos?channel_id=eq.d68f8efd-64c8-4c07-9d34-e98c2954f4e1&select=video_id,title,published_at&order=published_at.desc', headers=h)
print("=== DB videos for sesang101 ===")
for v in r.json():
    print(f"{v['published_at']} | {v['title']} | {v['video_id']}")

# Check if these specific videos exist
targets = ['트럼프의 선택에 시장이 패닉', '언제 터질지 모르는 버블', '제2의 팔란티어']
print(f"\nTotal: {len(r.json())} videos")
