#!/usr/bin/env python3
"""세상학개론 87개 시그널 → Supabase INSERT (v2 - fixed)"""
import json, requests, time, os, sys

URL = 'https://arypzhotxflimroprmdk.supabase.co'
KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json', 'Prefer': 'return=representation'}

SPEAKER_ID = 'b07d8758-493a-4a51-9bc5-7ef75f0be67c'  # 이효석

def p(msg):
    print(msg, flush=True)

def api(method, path, data=None):
    r = getattr(requests, method)(f'{URL}/rest/v1/{path}', headers=H, json=data)
    return r

# 1. 채널 확인/생성
print("=== 1. 채널 확인 ===")
r = api('get', 'influencer_channels?channel_handle=eq.@sesang101')
if r.ok and r.json():
    channel_id = r.json()[0]['id']
    print(f"채널 존재: {channel_id}")
else:
    r = api('post', 'influencer_channels', {
        'channel_name': '세상학개론',
        'channel_handle': '@sesang101',
        'channel_url': 'https://www.youtube.com/@sesang101',
        'platform': 'youtube'
    })
    channel_id = r.json()[0]['id']
    print(f"채널 생성: {channel_id}")

# 2. 시그널 데이터 로드
print("\n=== 2. 시그널 로드 ===")
signals = json.load(open('sesang101_supabase_upload.json', 'r', encoding='utf-8'))
print(f"시그널: {len(signals)}개")

# 3. 영상별로 그룹화
video_signals = {}
for s in signals:
    vid = s['video_id']
    if vid not in video_signals:
        video_signals[vid] = []
    video_signals[vid].append(s)
print(f"영상: {len(video_signals)}개")

# 4. 기존 영상 확인 (ALL videos, not just this channel)
print("\n=== 3. 기존 영상 확인 ===")
existing_videos = {}
# Supabase returns max 1000, paginate
offset = 0
while True:
    r = api('get', f'influencer_videos?select=video_id,id&offset={offset}&limit=1000')
    if r.ok and r.json():
        for v in r.json():
            existing_videos[v['video_id']] = v['id']
        if len(r.json()) < 1000:
            break
        offset += 1000
    else:
        break
print(f"기존 영상: {len(existing_videos)}개")

# 5. 기존 시그널 확인 (중복 방지)
print("\n=== 4. 기존 시그널 확인 ===")
r = api('get', f'influencer_signals?speaker_id=eq.{SPEAKER_ID}&select=video_id,stock')
existing_sigs = set()
if r.ok:
    for s in r.json():
        existing_sigs.add((s['video_id'], s['stock']))
print(f"기존 시그널: {len(existing_sigs)}개")

# 6. 영상 INSERT + 시그널 INSERT
print("\n=== 5. INSERT 시작 ===")
inserted = 0
skipped = 0
errors = 0

# 제목 파일 로드
titles = {}
titles_file = os.path.join(os.path.dirname(__file__), 'sesang101_videos.txt')
if os.path.exists(titles_file):
    for enc in ['utf-8', 'cp949']:
        try:
            with open(titles_file, 'r', encoding=enc) as f:
                for line in f:
                    if '|||' in line:
                        vid, title = line.strip().split('|||', 1)
                        titles[vid.strip()] = title.strip()
            break
        except:
            continue

for youtube_vid, sigs in video_signals.items():
    # 영상 INSERT (없으면)
    if youtube_vid not in existing_videos:
        title = sigs[0].get('video_title', titles.get(youtube_vid, f'세상학개론 {youtube_vid}'))
        r = api('post', 'influencer_videos', {
            'channel_id': channel_id,
            'video_id': youtube_vid,
            'title': title[:500],
            'has_subtitle': True,
            'subtitle_language': 'ko',
            'pipeline_version': 'V9.1',
            'signal_count': len(sigs)
        })
        if r.ok and r.json():
            video_uuid = r.json()[0]['id']
            existing_videos[youtube_vid] = video_uuid
            print(f"  영상 추가: {youtube_vid[:12]}... → {video_uuid[:8]}")
        else:
            print(f"  [ERROR] 영상 추가 실패: {youtube_vid} - {r.status_code} {r.text[:200]}")
            errors += 1
            continue
    
    video_uuid = existing_videos[youtube_vid]
    
    # 시그널 INSERT
    for s in sigs:
        # 중복 체크
        if (video_uuid, s['stock']) in existing_sigs:
            skipped += 1
            continue
        
        # 시그널 타입 매핑
        signal_map = {
            '매수': '매수', 'STRONG_BUY': '매수', 'BUY': '매수',
            '긍정': '긍정', 'POSITIVE': '긍정',
            '중립': '중립', 'NEUTRAL': '중립', 'HOLD': '중립',
            '경계': '경계', 'CONCERN': '경계', 'SELL': '경계',
            '매도': '매도', 'STRONG_SELL': '매도',
        }
        signal_type = signal_map.get(s.get('signal', ''), s.get('signal', '중립'))
        
        row = {
            'video_id': video_uuid,
            'speaker_id': SPEAKER_ID,
            'stock': s['stock'],
            'ticker': s.get('ticker'),
            'market': s.get('market', 'KR'),
            'mention_type': s.get('mention_type', '분석'),
            'signal': signal_type,
            'confidence': s.get('confidence', 'medium'),
            'timestamp': s.get('timestamp'),
            'key_quote': (s.get('key_quote', '') or '')[:1000],
            'reasoning': (s.get('reasoning', '') or '')[:2000],
            'review_status': 'pending',
            'pipeline_version': 'V9.1'
        }
        
        r = api('post', 'influencer_signals', row)
        if r.ok:
            inserted += 1
            existing_sigs.add((video_uuid, s['stock']))
        else:
            print(f"  [ERROR] 시그널 INSERT 실패: {s['stock']} - {r.status_code} {r.text[:200]}")
            errors += 1
        
        time.sleep(0.1)  # 가벼운 딜레이

print(f"\n=== 완료 ===")
print(f"INSERT: {inserted}, 스킵(중복): {skipped}, 에러: {errors}")
print(f"총 시그널: {len(existing_sigs)}개 (기존+신규)")
