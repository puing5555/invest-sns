import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests, json

key = open('.env.local').readlines()[2].split('=',1)[1].strip()
h = {'apikey': key, 'Authorization': 'Bearer ' + key}

# Get all signals
r1 = requests.get('https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals?select=id,video_id,stock', headers=h)
signals = r1.json()

# Get all videos
r2 = requests.get('https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_videos?select=id,video_id,title', headers=h)
videos = r2.json()

video_pks = set(v['id'] for v in videos)  # PK (UUID)
video_ytids = {v['video_id']: v['id'] for v in videos}  # YouTube ID -> PK

print(f"Signals: {len(signals)}")
print(f"Videos (PK): {len(video_pks)}")
print(f"Videos (YouTube ID): {len(video_ytids)}")

# Check: do signal.video_id match video PK or YouTube ID?
match_pk = 0
match_ytid = 0
no_match = 0
orphans = []

for s in signals:
    vid = s.get('video_id')
    if not vid:
        no_match += 1
        continue
    if vid in video_pks:
        match_pk += 1
    elif vid in video_ytids:
        match_ytid += 1
    else:
        no_match += 1
        orphans.append(s)

print(f"\nSignal video_id matches:")
print(f"  Match video PK (correct FK): {match_pk}")
print(f"  Match YouTube ID (wrong FK): {match_ytid}")
print(f"  No match at all: {no_match}")

if orphans:
    print(f"\nOrphan signals (no video found): {len(orphans)}")
    unique_vids = set(s['video_id'] for s in orphans)
    print(f"Unique orphan video_ids: {len(unique_vids)}")
    for vid in list(unique_vids)[:5]:
        print(f"  {vid}")
