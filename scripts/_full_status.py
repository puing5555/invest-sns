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
all_vids = {v['id']: v for v in fetch('influencer_videos?select=id,channel_id,title&limit=1000')}
sigs = fetch('influencer_signals?select=id,video_id,speaker_id,stock,signal&limit=1000')

print(f"총 시그널: {len(sigs)}")

# 1. Speaker distribution
from collections import Counter
print(f"\n=== Speaker별 시그널 수 ===")
sp_cnt = Counter()
for s in sigs:
    sp_cnt[speakers.get(s['speaker_id'], s['speaker_id'][:8])] += 1
for name, cnt in sp_cnt.most_common():
    print(f"  {name}: {cnt}")

# 2. Channel별 시그널 수
print(f"\n=== Channel별 시그널 수 ===")
ch_cnt = Counter()
for s in sigs:
    vid = all_vids.get(s['video_id'], {})
    ch_name = ch_map.get(vid.get('channel_id'), '?')
    ch_cnt[ch_name] += 1
for name, cnt in ch_cnt.most_common():
    print(f"  {name}: {cnt}")

# 3. 각 시그널의 speaker + 영상제목 전체 리스트 (삼프로TV + 부읽남TV만)
sampro_ch = '4867e157-2126-4c67-aa5e-638372de8f03'
buread_ch = '12facb47-407d-4fd3-a310-12dd5a802d1f'

for ch_id, ch_name in [(sampro_ch, '삼프로TV'), (buread_ch, '부읽남TV')]:
    ch_sigs = [s for s in sigs if all_vids.get(s['video_id'], {}).get('channel_id') == ch_id]
    print(f"\n=== {ch_name} 시그널 상세 ({len(ch_sigs)}개) ===")
    for s in ch_sigs:
        vid = all_vids.get(s['video_id'], {})
        sp_name = speakers.get(s['speaker_id'], '?')
        title = vid.get('title', '?')[:80]
        print(f"  [{sp_name}] {s['stock']} | {title}")
