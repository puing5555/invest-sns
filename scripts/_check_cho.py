#!/usr/bin/env python3
import os, json, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; from pathlib import Path
load_dotenv(Path(__file__).parent.parent / '.env.local')
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY','') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY','')
def fetch(ep):
    req = urllib.request.Request(url+'/rest/v1/'+ep, headers={'apikey':key,'Authorization':'Bearer '+key})
    return json.loads(urllib.request.urlopen(req).read())

ch_map = {c['id']: c['channel_name'] for c in fetch('influencer_channels?select=id,channel_name')}

# 조진표 speaker
cho_sp = '6b2696ff-f6a6-424b-a6de-0cd837f7bbb0'
sigs = fetch('influencer_signals?speaker_id=eq.' + cho_sp + '&select=id,video_id,stock&limit=100')
print(f"조진표 총 시그널: {len(sigs)}")

vid_ids = list(set(s['video_id'] for s in sigs))
vids = {}
for vid in vid_ids:
    v = fetch('influencer_videos?id=eq.' + vid + '&select=id,channel_id,title')
    if v: vids[vid] = v[0]

# Group by channel
from collections import Counter
ch_counts = Counter()
for s in sigs:
    v = vids.get(s['video_id'], {})
    ch_name = ch_map.get(v.get('channel_id'), '?')
    ch_counts[ch_name] += 1

print("\n조진표 시그널 by channel:")
for ch, cnt in ch_counts.most_common():
    print(f"  {ch}: {cnt}")

# Show titles for bureadnam
print("\n부읽남TV 영상 제목:")
for s in sigs:
    v = vids.get(s['video_id'], {})
    ch_name = ch_map.get(v.get('channel_id'), '?')
    if ch_name == '부읽남TV':
        title = v.get('title', '?')[:80]
        print(f"  {s['stock']} | {title}")
