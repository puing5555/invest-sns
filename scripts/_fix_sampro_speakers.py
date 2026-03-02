#!/usr/bin/env python3
"""삼프로TV speaker 재매핑 - 영상 제목에서 첫 번째 출연자 추출하여 매핑"""
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

def post(ep, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(url+'/rest/v1/'+ep, data=body, method='POST',
        headers={'apikey':key,'Authorization':'Bearer '+key,'Content-Type':'application/json','Prefer':'return=representation'})
    return json.loads(urllib.request.urlopen(req).read())

# Load speakers
speakers = {s['name']: s['id'] for s in fetch('speakers?select=id,name')}
speakers_by_id = {s['id']: s['name'] for s in fetch('speakers?select=id,name')}

# Title -> speaker name mapping (first name after | is the main speaker)
def extract_speaker_from_title(title):
    """영상 제목에서 | 뒤의 첫 번째 출연자명 추출"""
    if '|' not in title and 'ㅣ' not in title:
        return None
    # Split on | or ㅣ
    parts = re.split(r'[|ㅣ]', title, maxsplit=1)
    if len(parts) < 2:
        return None
    after = parts[1].strip()
    # Extract first name - usually "이름 직함 [프로그램명]" or "이름, 이름2, 이름3 직함"
    # Remove [프로그램명] suffix
    after = re.sub(r'\[.*?\]', '', after).strip()
    # Get first name (Korean 2-3 chars)
    match = re.match(r'([가-힣]{2,4})', after)
    if match:
        return match.group(1)
    return None

# Get 삼프로TV signals + videos
sampro_ch = '4867e157-2126-4c67-aa5e-638372de8f03'
vids = {v['id']: v for v in fetch('influencer_videos?channel_id=eq.' + sampro_ch + '&select=id,title')}
sigs = fetch('influencer_signals?select=id,video_id,speaker_id,stock&limit=500')
sampro_sigs = [s for s in sigs if s['video_id'] in vids]

print(f"삼프로TV 시그널: {len(sampro_sigs)}개\n")

# Map each signal to correct speaker based on title
changes = []
for s in sampro_sigs:
    vid = vids[s['video_id']]
    title = vid['title']
    speaker_name = extract_speaker_from_title(title)
    current_name = speakers_by_id.get(s['speaker_id'], '?')
    
    if not speaker_name:
        print(f"  ⚠️ 화자 추출 실패: {title[:60]}")
        continue
    
    # Find or create speaker
    if speaker_name not in speakers:
        print(f"  🆕 새 speaker 생성: {speaker_name}")
        result = post('speakers', {'name': speaker_name, 'aliases': [speaker_name]})
        speakers[speaker_name] = result['id'] if isinstance(result, dict) else result[0]['id']
        speakers_by_id[speakers[speaker_name]] = speaker_name
    
    target_id = speakers[speaker_name]
    if s['speaker_id'] != target_id:
        changes.append({
            'signal_id': s['id'],
            'stock': s['stock'],
            'from': current_name,
            'to': speaker_name,
            'to_id': target_id,
            'title': title[:70]
        })

print(f"\n=== 변경 내역 ({len(changes)}개) ===")
for c in changes:
    print(f"  [{c['from']} → {c['to']}] {c['stock']} | {c['title']}")

# Apply changes
print(f"\n적용 중...")
for c in changes:
    patch(f"influencer_signals?id=eq.{c['signal_id']}", {"speaker_id": c['to_id']})

print(f"✅ {len(changes)}개 변경 완료")

# Verify
print(f"\n=== 변경 후 삼프로TV speaker 분포 ===")
sigs2 = fetch('influencer_signals?select=speaker_id&limit=500')
sampro_sigs2 = [s for s in fetch('influencer_signals?select=id,video_id,speaker_id&limit=500') if s['video_id'] in vids]
from collections import Counter
sp_cnt = Counter(speakers_by_id.get(s['speaker_id'], s['speaker_id'][:8]) for s in sampro_sigs2)
for name, cnt in sp_cnt.most_common():
    print(f"  {name}: {cnt}")
