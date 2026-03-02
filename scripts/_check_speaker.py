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

def patch(ep, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(url+'/rest/v1/'+ep, data=body, method='PATCH',
        headers={'apikey':key,'Authorization':'Bearer '+key,'Content-Type':'application/json','Prefer':'return=minimal'})
    return urllib.request.urlopen(req)

# Channel IDs
sesang_ch = 'd68f8efd-64c8-4c07-9d34-e98c2954f4e1'
hyoseok_ch = 'd153b75b-1843-4a99-b49f-c31081a8f566'

# 1. Get all sesang101 videos
sesang_vids = fetch('influencer_videos?channel_id=eq.'+sesang_ch+'&select=id')
sesang_vid_ids = set(v['id'] for v in sesang_vids)
print(f"세상학개론 videos in DB: {len(sesang_vid_ids)}")

# 2. Get ALL signals, check speaker-channel mismatch
all_sigs = fetch('influencer_signals?select=id,video_id,speaker_id,stock,signal&limit=1000')
print(f"Total signals: {len(all_sigs)}")

# 3. Build video->channel map
all_vids = fetch('influencer_videos?select=id,channel_id&limit=1000')
vid_to_ch = {v['id']: v['channel_id'] for v in all_vids}

# 4. For each signal, check if video's channel matches what we expect for the speaker
# First, figure out which speaker belongs to which channel
# Group signals by speaker, see which channels their videos come from
speaker_channels = {}
for s in all_sigs:
    sp = s['speaker_id']
    vid_ch = vid_to_ch.get(s['video_id'], '?')
    if sp not in speaker_channels:
        speaker_channels[sp] = set()
    speaker_channels[sp].add(vid_ch)

print("\n=== Speaker -> Channels ===")
for sp, chs in speaker_channels.items():
    ch_names = []
    for c in chs:
        if c == sesang_ch: ch_names.append('세상학개론')
        elif c == hyoseok_ch: ch_names.append('이효석아카데미')
        elif c == '4867e157-2126-4c67-aa5e-638372de8f03': ch_names.append('삼프로TV')
        elif c == 'c9c4dc38-c108-4988-b1d2-b177c3b324fc': ch_names.append('코린이아빠')
        elif c == '12facb47-407d-4fd3-a310-12dd5a802d1f': ch_names.append('부읽남TV')
        elif c == 'dde0918d-5237-4402-9782-e2d968958f64': ch_names.append('슈카월드')
        elif c == '08642417-1b38-4295-a36f-3ed53713cfd5': ch_names.append('달란트투자')
        elif c is None: ch_names.append('NO_CHANNEL')
        else: ch_names.append(c[:8])
    if len(chs) > 1:
        print(f"  ⚠️ MISMATCH speaker {sp[:8]}... -> {ch_names}")
    else:
        print(f"  ✅ speaker {sp[:8]}... -> {ch_names}")

# 5. Find sesang101 signals with wrong speaker
# The hardcoded speaker in sesang101_insert_v2.py
bad_speaker = 'b07d8758-493a-4a51-9bc5-7ef75f0be67c'
# Check if this speaker has signals in sesang101 videos
bad_sigs = [s for s in all_sigs if s['video_id'] in sesang_vid_ids and s['speaker_id'] == bad_speaker]
print(f"\n=== Bad speaker signals (sesang videos with speaker {bad_speaker[:8]}): {len(bad_sigs)} ===")

# Also find ALL sesang101 signals regardless of speaker
sesang_sigs = [s for s in all_sigs if s['video_id'] in sesang_vid_ids]
print(f"All sesang101 signals: {len(sesang_sigs)}")
sesang_speakers = set(s['speaker_id'] for s in sesang_sigs)
print(f"Speakers used in sesang101 signals: {sesang_speakers}")

# Check what speaker b07d8758 is - look at hyoseok signals
hyoseok_vids = set(v['id'] for v in all_vids if v['channel_id'] == hyoseok_ch)
hyoseok_sigs_with_bad = [s for s in all_sigs if s['video_id'] in hyoseok_vids and s['speaker_id'] == bad_speaker]
print(f"\n이효석 videos with speaker {bad_speaker[:8]}: {len(hyoseok_sigs_with_bad)}")
