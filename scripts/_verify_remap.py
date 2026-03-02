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

speakers = {s['id']: s['name'] for s in fetch('speakers?select=id,name')}
ch_map = {c['id']: c['channel_name'] for c in fetch('influencer_channels?select=id,channel_name')}

# Get ALL signals
sigs = fetch('influencer_signals?select=id,video_id,speaker_id,stock,signal&limit=500')

# Get all videos
all_vids = {}
for v in fetch('influencer_videos?select=id,channel_id,title&limit=500'):
    all_vids[v['id']] = v

# 삼프로TV 시그널 현재 상태
sampro_ch = '4867e157-2126-4c67-aa5e-638372de8f03'
sampro_sigs = [s for s in sigs if all_vids.get(s['video_id'], {}).get('channel_id') == sampro_ch]

print(f"=== 삼프로TV 시그널 현재 상태 ({len(sampro_sigs)}개) ===")
for s in sorted(sampro_sigs, key=lambda x: speakers.get(x['speaker_id'], '?')):
    sp_name = speakers.get(s['speaker_id'], s['speaker_id'][:8])
    vid = all_vids.get(s['video_id'], {})
    title = vid.get('title', '?')[:70]
    print(f"  [{sp_name}] {s['stock']} | {title}")

# 박지훈 시그널 확인
print(f"\n=== 박지훈 시그널 전체 ===")
parkjihoon = [s for s in sigs if speakers.get(s['speaker_id']) == '박지훈']
for s in parkjihoon:
    vid = all_vids.get(s['video_id'], {})
    ch_name = ch_map.get(vid.get('channel_id'), '?')
    title = vid.get('title', '?')[:70]
    print(f"  [{ch_name}] {s['stock']} | {title}")

# Speaker distribution
print(f"\n=== 전체 speaker 분포 ===")
from collections import Counter
sp_cnt = Counter(speakers.get(s['speaker_id'], s['speaker_id'][:8]) for s in sigs)
for name, cnt in sp_cnt.most_common():
    print(f"  {name}: {cnt}")
