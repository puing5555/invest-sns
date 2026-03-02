#!/usr/bin/env python3
"""세상학개론 87개 시그널 → Supabase INSERT (v2)"""
import json, requests, time, sys

URL = 'https://arypzhotxflimroprmdk.supabase.co'
KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
H = {'apikey': KEY, 'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'Prefer': 'return=representation'}
SPEAKER_ID = 'b07d8758-493a-4a51-9bc5-7ef75f0be67c'

def get(path):
    return requests.get(URL + '/rest/v1/' + path, headers=H, timeout=15)

def post(path, data):
    return requests.post(URL + '/rest/v1/' + path, headers=H, json=data, timeout=15)

# 1. Load all existing videos (youtube_id -> uuid)
print('1. Loading existing videos...', flush=True)
r = get('influencer_videos?select=video_id,id&limit=1000')
existing_vids = {v['video_id']: v['id'] for v in r.json()} if r.ok else {}
print('  Found: ' + str(len(existing_vids)), flush=True)

# 2. Load existing signals for this speaker
print('2. Loading existing signals...', flush=True)
r = get('influencer_signals?speaker_id=eq.' + SPEAKER_ID + '&select=video_id,stock')
existing_sigs = set()
if r.ok:
    for s in r.json():
        existing_sigs.add((s['video_id'], s['stock']))
print('  Found: ' + str(len(existing_sigs)), flush=True)

# 3. Get channel id
print('3. Getting channel...', flush=True)
r = get('influencer_channels?channel_handle=eq.@sesang101&select=id')
if not r.ok or not r.json():
    print('ERROR: channel not found', flush=True)
    sys.exit(1)
channel_id = r.json()[0]['id']
print('  Channel: ' + channel_id, flush=True)

# 4. Load signals
print('4. Loading signals...', flush=True)
signals = json.load(open('sesang101_supabase_upload.json', 'r', encoding='utf-8'))
print('  Total: ' + str(len(signals)), flush=True)

# 5. Process
SIGNAL_MAP = {
    '매수': '매수', '긍정': '긍정', '중립': '중립', '경계': '경계', '매도': '매도',
    'STRONG_BUY': '매수', 'BUY': '매수', 'POSITIVE': '긍정',
    'NEUTRAL': '중립', 'HOLD': '중립', 'CONCERN': '경계',
    'SELL': '매도', 'STRONG_SELL': '매도'
}

inserted = 0
skipped = 0
errors = 0
vids_created = 0

print('5. Inserting...', flush=True)
for i, s in enumerate(signals):
    yt_vid = s['video_id']
    
    # Create video if needed
    if yt_vid not in existing_vids:
        title = s.get('video_title', 'sesang101 ' + yt_vid)
        r = post('influencer_videos', {
            'channel_id': channel_id, 'video_id': yt_vid, 'title': title[:500],
            'has_subtitle': True, 'subtitle_language': 'ko',
            'pipeline_version': 'V9.1', 'signal_count': 1
        })
        if r.ok and r.json():
            existing_vids[yt_vid] = r.json()[0]['id']
            vids_created += 1
        elif r.status_code == 409:
            r2 = get('influencer_videos?video_id=eq.' + yt_vid + '&select=id')
            if r2.ok and r2.json():
                existing_vids[yt_vid] = r2.json()[0]['id']
        else:
            print('  ERR video ' + yt_vid + ': ' + str(r.status_code), flush=True)
            errors += 1
            continue
    
    video_uuid = existing_vids.get(yt_vid)
    if not video_uuid:
        errors += 1
        continue
    
    # Skip duplicates
    if (video_uuid, s['stock']) in existing_sigs:
        skipped += 1
        continue
    
    sig_type = SIGNAL_MAP.get(s.get('signal', ''), '중립')
    
    row = {
        'video_id': video_uuid,
        'speaker_id': SPEAKER_ID,
        'stock': s['stock'],
        'ticker': s.get('ticker'),
        'market': s.get('market', 'KR'),
        'mention_type': s.get('mention_type', '분석'),
        'signal': sig_type,
        'confidence': s.get('confidence', 'medium'),
        'timestamp': s.get('timestamp'),
        'key_quote': (s.get('key_quote', '') or '')[:1000],
        'reasoning': (s.get('reasoning', '') or '')[:2000],
        'review_status': 'pending',
        'pipeline_version': 'V9.1'
    }
    
    r = post('influencer_signals', row)
    if r.ok:
        inserted += 1
        existing_sigs.add((video_uuid, s['stock']))
        if inserted % 10 == 0:
            print('  ...inserted ' + str(inserted), flush=True)
    else:
        err_text = r.text[:150] if r.text else 'unknown'
        print('  ERR signal ' + s['stock'] + ': ' + str(r.status_code) + ' ' + err_text, flush=True)
        errors += 1
    
    time.sleep(0.05)

print('', flush=True)
print('=== DONE ===', flush=True)
print('Inserted: ' + str(inserted), flush=True)
print('Skipped (dup): ' + str(skipped), flush=True)
print('Errors: ' + str(errors), flush=True)
print('Videos created: ' + str(vids_created), flush=True)
print('Total signals now: ' + str(len(existing_sigs)), flush=True)
