import sys, io, os, requests, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env.local')
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
h = {'apikey': key, 'Authorization': f'Bearer {key}'}

# Get a sample
r = requests.get(url + '/rest/v1/influencer_videos?select=video_id,subtitle_text&subtitle_text=not.is.null&limit=1', headers=h)
data = r.json()
if data:
    vid = data[0]['video_id']
    st = data[0]['subtitle_text']
    print(f'video_id: {vid}')
    print(f'length: {len(st)}')
    print(f'first 800 chars:\n{st[:800]}')
    print(f'\nHas -->: {"-->" in st}')

# Count
r2 = requests.get(url + '/rest/v1/influencer_videos?select=id&subtitle_text=not.is.null', headers=h)
print(f'\nVideos with subtitle: {len(r2.json())}')
r3 = requests.get(url + '/rest/v1/influencer_videos?select=id', headers=h)
print(f'Total videos: {len(r3.json())}')

# Get a signal with its video subtitle
r4 = requests.get(url + '/rest/v1/influencer_signals?select=id,key_quote,timestamp,video_id,influencer_videos(subtitle_text)&limit=3', headers=h)
for s in r4.json():
    vid_info = s.get('influencer_videos') or {}
    sub = vid_info.get('subtitle_text') or ''
    kq = s.get('key_quote', '')
    print(f'\nSignal: ts={s["timestamp"]}, quote={kq[:60]}')
    print(f'  subtitle exists: {bool(sub)}, len={len(sub)}')
    if sub and kq:
        # Try to find quote
        if kq[:20] in sub:
            print(f'  FOUND quote in subtitle!')
        else:
            print(f'  Quote NOT found. Sub sample: {sub[:200]}')
