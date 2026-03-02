import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests, json

key = open('.env.local').readlines()[2].split('=',1)[1].strip()
h = {'apikey': key, 'Authorization': 'Bearer ' + key}

# Get sesang101 channel
r = requests.get('https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_channels?name=eq.sesang101&select=id,youtube_channel_id', headers=h)
ch = r.json()
print('Channel:', json.dumps(ch, ensure_ascii=False))

if ch:
    cid = ch[0]['id']
    ytid = ch[0].get('youtube_channel_id', '')
    
    # Latest videos
    r2 = requests.get(
        f'https://arypzhotxflimroprmdk.supabase.co/rest/v1/videos?channel_id=eq.{cid}&select=id,title,published_at,youtube_id&order=published_at.desc&limit=10',
        headers=h
    )
    vids = r2.json()
    print(f'\nLatest {len(vids)} videos:')
    for v in vids:
        pa = v.get('published_at', '?')
        print(f"  {pa} | {v['title'][:60]}")
    
    # Total count
    r3 = requests.get(f'https://arypzhotxflimroprmdk.supabase.co/rest/v1/videos?channel_id=eq.{cid}&select=id', headers=h)
    all_vids = r3.json()
    print(f'\nTotal videos in DB: {len(all_vids)}')
    
    # Earliest and latest
    r4 = requests.get(
        f'https://arypzhotxflimroprmdk.supabase.co/rest/v1/videos?channel_id=eq.{cid}&select=published_at&order=published_at.asc&limit=1',
        headers=h
    )
    earliest = r4.json()
    if earliest:
        print(f"Earliest: {earliest[0].get('published_at')}")
    
    print(f"Latest: {vids[0].get('published_at') if vids else '?'}")
    print(f"\nYouTube Channel ID: {ytid}")
