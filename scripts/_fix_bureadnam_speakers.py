#!/usr/bin/env python3
"""부읽남TV speaker 재매핑 - 영상 제목 [게스트명] 기준"""
import os, json, sys, re, urllib.request
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
    urllib.request.urlopen(req)

def post_speaker(name):
    body = json.dumps({'name': name, 'aliases': [name]}).encode()
    req = urllib.request.Request(url+'/rest/v1/speakers', data=body, method='POST',
        headers={'apikey':key,'Authorization':'Bearer '+key,'Content-Type':'application/json','Prefer':'return=representation'})
    result = json.loads(urllib.request.urlopen(req).read())
    return result['id'] if isinstance(result, dict) else result[0]['id']

speakers = {s['name']: s['id'] for s in fetch('speakers?select=id,name')}
speakers_by_id = {v: k for k, v in speakers.items()}

buread_ch = '12facb47-407d-4fd3-a310-12dd5a802d1f'
vids = {v['id']: v for v in fetch('influencer_videos?channel_id=eq.' + buread_ch + '&select=id,title')}
sigs = fetch('influencer_signals?select=id,video_id,speaker_id,stock&limit=500')
buread_sigs = [s for s in sigs if s['video_id'] in vids]

def extract_guest(title):
    """부읽남TV: [게스트명 직함 부수] 패턴"""
    match = re.search(r'\[([가-힣]{2,4})\s', title)
    if match:
        return match.group(1)
    return None

print(f"부읽남TV 시그널: {len(buread_sigs)}개\n")

changes = []
for s in buread_sigs:
    vid = vids[s['video_id']]
    title = vid['title']
    guest = extract_guest(title)
    current = speakers_by_id.get(s['speaker_id'], '?')
    
    if not guest:
        print(f"  ⚠️ 추출 실패: {title[:60]}")
        continue
    
    if guest not in speakers:
        print(f"  🆕 새 speaker: {guest}")
        speakers[guest] = post_speaker(guest)
        speakers_by_id[speakers[guest]] = guest
    
    target_id = speakers[guest]
    if s['speaker_id'] != target_id:
        changes.append({
            'signal_id': s['id'],
            'stock': s['stock'],
            'from': current,
            'to': guest,
            'to_id': target_id,
            'title': title[:70]
        })

print(f"\n=== 변경 내역 ({len(changes)}개) ===")
for c in changes:
    print(f"  [{c['from']} → {c['to']}] {c['stock']} | {c['title']}")

print(f"\n적용 중...")
for c in changes:
    patch(f"influencer_signals?id=eq.{c['signal_id']}", {"speaker_id": c['to_id']})
print(f"✅ {len(changes)}개 변경 완료")

# Verify
from collections import Counter
buread_sigs2 = [s for s in fetch('influencer_signals?select=video_id,speaker_id&limit=500') if s['video_id'] in vids]
sp_cnt = Counter(speakers_by_id.get(s['speaker_id'], s['speaker_id'][:8]) for s in buread_sigs2)
print(f"\n=== 변경 후 부읽남TV speaker 분포 ===")
for name, cnt in sp_cnt.most_common():
    print(f"  {name}: {cnt}")
