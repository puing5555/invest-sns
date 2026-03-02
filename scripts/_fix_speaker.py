#!/usr/bin/env python3
"""세상학개론 시그널의 잘못된 speaker_id를 수정"""
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
        headers={'apikey':key,'Authorization':'Bearer '+key,'Content-Type':'application/json','Prefer':'return=representation'})
    return json.loads(urllib.request.urlopen(req).read())

sesang_ch = 'd68f8efd-64c8-4c07-9d34-e98c2954f4e1'
bad_speaker = 'b07d8758-493a-4a51-9bc5-7ef75f0be67c'  # 이효석
good_speaker = 'b9496a5f-06fa-47eb-bc2d-47060b095534'  # 세상학개론

# Get sesang101 video IDs
sesang_vids = fetch('influencer_videos?channel_id=eq.'+sesang_ch+'&select=id')
sesang_vid_ids = set(v['id'] for v in sesang_vids)
print(f"세상학개론 videos: {len(sesang_vid_ids)}")

# Get bad signals (sesang videos with 이효석 speaker)
bad_sigs = fetch('influencer_signals?speaker_id=eq.'+bad_speaker+'&select=id,video_id,stock&limit=500')
to_fix = [s for s in bad_sigs if s['video_id'] in sesang_vid_ids]
print(f"수정 대상: {len(to_fix)}개")

# Fix them - batch by updating where speaker_id=bad AND video_id in sesang videos
# Supabase REST doesn't support IN easily, so update one by one
fixed = 0
errors = 0
for s in to_fix:
    try:
        result = patch(
            f"influencer_signals?id=eq.{s['id']}",
            {"speaker_id": good_speaker}
        )
        fixed += 1
        if fixed % 20 == 0:
            print(f"  {fixed}/{len(to_fix)} done...")
    except Exception as e:
        print(f"  ERROR fixing {s['id']}: {e}")
        errors += 1

print(f"\n✅ 수정 완료: {fixed}개")
print(f"❌ 에러: {errors}개")

# Verify
after = fetch('influencer_signals?speaker_id=eq.'+bad_speaker+'&select=id,video_id&limit=500')
still_bad = [s for s in after if s['video_id'] in sesang_vid_ids]
print(f"검증 - 아직 잘못된 시그널: {len(still_bad)}")

# Check 이효석 only has 이효석 videos now
hyoseok_ch = 'd153b75b-1843-4a99-b49f-c31081a8f566'
hyoseok_vids = set(v['id'] for v in fetch('influencer_videos?channel_id=eq.'+hyoseok_ch+'&select=id'))
hyoseok_sigs = fetch('influencer_signals?speaker_id=eq.'+bad_speaker+'&select=id,video_id&limit=500')
clean = all(s['video_id'] in hyoseok_vids for s in hyoseok_sigs)
print(f"이효석 시그널 모두 이효석아카데미 영상: {'✅' if clean else '❌'} ({len(hyoseok_sigs)}개)")
