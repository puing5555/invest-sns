import httpx, os, json
from dotenv import load_dotenv
load_dotenv('.env.local')
url = os.environ['NEXT_PUBLIC_SUPABASE_URL'] + '/rest/v1/influencer_signals'
key = os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
r = httpx.get(url, headers={'apikey': key, 'Authorization': f'Bearer {key}'}, params={
    'select': 'id,ticker,stock,signal,speakers(name),influencer_videos(title,published_at,influencer_channels(channel_name))',
    'order': 'created_at.desc',
    'limit': '50'
})
data = r.json()
print(f"Total returned: {len(data)}")
for s in data:
    speaker = (s.get('speakers') or {}).get('name', '?')
    ch = ((s.get('influencer_videos') or {}).get('influencer_channels') or {}).get('channel_name', '?')
    print(f"  {speaker} | {ch} | {s['stock']} | {s['signal']}")
