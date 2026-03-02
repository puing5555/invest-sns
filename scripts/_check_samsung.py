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

# Speaker map
speakers = {s['id']: s['name'] for s in fetch('speakers?select=id,name')}

# 김장열 시그널
kim_sp = '8234cd75-1d0d-458c-b01c-62080c7d91e3'
kim_sigs = fetch('influencer_signals?speaker_id=eq.' + kim_sp + '&select=id,video_id,stock,signal,key_quote&limit=50')
print(f"김장열 총 시그널: {len(kim_sigs)}")

# Get video titles for context
vid_ids = list(set(s['video_id'] for s in kim_sigs))
vids = {}
for vid in vid_ids:
    v = fetch('influencer_videos?id=eq.' + vid + '&select=id,title,channel_id')
    if v:
        vids[vid] = v[0]

# Show 김장열 삼성전자 signals with video context
samsung_sigs = [s for s in kim_sigs if '삼성' in (s.get('stock') or '')]
print(f"김장열 삼성전자 시그널: {len(samsung_sigs)}")
for s in samsung_sigs:
    vid = vids.get(s['video_id'], {})
    title = vid.get('title', '?')[:60]
    quote = (s.get('key_quote') or '')[:80]
    print(f"  {s['stock']} | {s['signal']} | 영상: {title}")
    print(f"    quote: {quote}")

# Check ALL speakers for samsung signals
print("\n=== 삼성전자 전체 시그널 ===")
all_sigs = fetch('influencer_signals?select=id,speaker_id,stock,signal&limit=500')
samsung_all = [s for s in all_sigs if '삼성' in (s.get('stock') or '')]
print(f"총 {len(samsung_all)}개")
from collections import Counter
for sp_id, cnt in Counter(s['speaker_id'] for s in samsung_all).most_common():
    print(f"  {speakers.get(sp_id, sp_id[:8])}: {cnt}개")

# Check if 김장열 is actually a real 삼프로TV speaker
print(f"\n=== 김장열 speaker info ===")
print(f"Name: 김장열, ID: {kim_sp}")
print(f"All stocks: {[s['stock'] for s in kim_sigs]}")
