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

# Get all signals with their video info
sigs = fetch('influencer_signals?select=id,video_id,speaker_id,stock,signal,key_quote&limit=500')
vids = fetch('influencer_videos?select=id,channel_id,title&limit=500')
channels = fetch('influencer_channels?select=id,channel_name')

vid_map = {v['id']: v for v in vids}
ch_map = {c['id']: c['channel_name'] for c in channels}

# Find all unique speaker_ids and which channels they appear in
speaker_channels = {}
for s in sigs:
    sp = s['speaker_id']
    vid = vid_map.get(s['video_id'], {})
    ch_id = vid.get('channel_id', '?')
    ch_name = ch_map.get(ch_id, (ch_id or '?')[:8])
    if sp not in speaker_channels:
        speaker_channels[sp] = {'channels': set(), 'count': 0, 'stocks': []}
    speaker_channels[sp]['channels'].add(ch_name)
    speaker_channels[sp]['count'] += 1
    speaker_channels[sp]['stocks'].append(s['stock'])

print("=== Speaker → Channel mapping ===")
for sp, info in sorted(speaker_channels.items(), key=lambda x: -x[1]['count']):
    chs = list(info['channels'])
    flag = '⚠️' if len(chs) > 1 else '✅'
    print(f"{flag} {sp[:8]}... ({info['count']} sigs) → {chs}")

# Now specifically check which speaker_ids map to 김장열
# We need to check the frontend - how does it resolve speaker_name?
# Check if there's a speakers/speaker_name join or if it's stored directly
print("\n=== Checking speaker_id frequency ===")
from collections import Counter
sp_counter = Counter(s['speaker_id'] for s in sigs)
for sp_id, cnt in sp_counter.most_common(10):
    chs = list(speaker_channels[sp_id]['channels'])
    print(f"  {sp_id[:12]}... : {cnt} signals, channels: {chs}")
