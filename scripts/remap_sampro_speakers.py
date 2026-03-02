#!/usr/bin/env python3
"""삼프로TV speaker 재매핑 스크립트"""
import os, re, json, sys
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv(Path(__file__).parent.parent / '.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
SAMPRO_CHANNEL_ID = '4867e157-2126-4c67-aa5e-638372de8f03'

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

KNOWN_SPEAKERS = {
    '김장열': '8234cd75-1d0d-458c-b01c-62080c7d91e3',
    '배재원': '7fef30a4-a248-44d6-99b9-02bda6f47eb2',
    '고연수': '3508abce-70e0-4eaa-a0d4-686b61071dd9',
    '김동훈': '5783838f-af5f-4e74-bcbf-bbc20141b199',
    '박지훈': 'e59ed6f5-7a8d-4111-af1c-502ad3344e79',
    '박병창': '2720d0ee-b7e2-4006-80df-90bc9de07797',
    '박명성': '5d03d08f-abb4-453b-bf86-40e57a0ddfdb',
    '장우진': 'aa25b0e6-aadf-4bae-a2fa-afc0a067e315',
    '이건희': '731fe32d-f47a-432f-9899-305915138983',
    '김학주': '289de288-d587-4381-9f3d-b03ab63baf21',
    '이영수': '81dd42e4-ba1d-4f73-ba1d-f18682d7baf8',
    '배제기': '01b70353-c4e0-4583-bdb3-6ba46beca191',
}

def api(method, table, params=None, data=None):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if params:
        # PostgREST needs unencoded parens/commas
        qs = '&'.join(f'{k}={v}' for k,v in params.items())
        url += '?' + qs
    r = getattr(requests, method)(url, headers=HEADERS, json=data)
    r.raise_for_status()
    return r.json() if r.text else None

def extract_speakers_from_title(title):
    """제목에서 | 뒤의 출연자명 추출"""
    if '|' not in title:
        return []
    after_pipe = title.split('|')[-1].strip()
    # Remove affiliations like "유니스토리자산운용", "하나증권 PB" etc
    # Split by comma first
    parts = [p.strip() for p in after_pipe.split(',')]
    names = []
    for part in parts:
        # Take first 2-3 char Korean name from each part
        match = re.match(r'([가-힣]{2,3})', part.strip())
        if match:
            names.append(match.group(1))
    return names

def find_or_create_speaker(name):
    """speakers 테이블에서 찾거나 새로 생성"""
    if name in KNOWN_SPEAKERS:
        return KNOWN_SPEAKERS[name], False
    
    # Search in DB  
    results = api('get', 'speakers', {'name': f'eq.{name}', 'select': 'id,name', 'limit': '1'})
    if results:
        KNOWN_SPEAKERS[name] = results[0]['id']
        return results[0]['id'], False
    
    # Create new speaker
    new = api('post', 'speakers', data={
        'name': name,
        'channel_id': SAMPRO_CHANNEL_ID,
        'description': f'삼프로TV 출연자'
    })
    speaker_id = new[0]['id'] if isinstance(new, list) else new['id']
    KNOWN_SPEAKERS[name] = speaker_id
    print(f"  ✨ 새 speaker 생성: {name} → {speaker_id[:8]}")
    return speaker_id, True

def main():
    # 1. Get all videos for sampro channel
    print("1. 삼프로TV 영상 조회...")
    videos = api('get', 'influencer_videos', {
        'channel_id': f'eq.{SAMPRO_CHANNEL_ID}',
        'select': 'id,title'
    })
    print(f"   영상 {len(videos)}개")
    
    video_map = {v['id']: v['title'] for v in videos}
    video_ids = list(video_map.keys())
    
    # 2. Get all signals for these videos (per-video query)
    print("2. 시그널 조회...")
    all_signals = []
    for vid in video_ids:
        sigs = api('get', 'influencer_signals', {
            'video_id': f'eq.{vid}',
            'select': 'id,video_id,speaker_id,stock,key_quote,signal'
        })
        all_signals.extend(sigs)
    
    print(f"   시그널 {len(all_signals)}개")
    
    # 3. Remap speakers
    print("\n3. Speaker 재매핑 시작...")
    changes = []
    errors = []
    
    for sig in all_signals:
        title = video_map.get(sig['video_id'], '')
        names = extract_speakers_from_title(title)
        old_speaker = sig['speaker_id']
        
        if not names:
            errors.append({'signal_id': sig['id'], 'title': title, 'reason': 'no_name_in_title'})
            continue
        
        # If single speaker in title, use that
        # For multi-speaker, use first (most are single-guest episodes)
        target_name = names[0]
        
        try:
            new_speaker_id, created = find_or_create_speaker(target_name)
        except Exception as e:
            errors.append({'signal_id': sig['id'], 'name': target_name, 'error': str(e)})
            continue
        
        if new_speaker_id and old_speaker != new_speaker_id:
            # Find old speaker name
            old_name = next((k for k,v in KNOWN_SPEAKERS.items() if v == old_speaker), old_speaker[:8])
            changes.append({
                'signal_id': sig['id'],
                'stock': sig.get('stock', ''),
                'old_speaker': old_name,
                'new_speaker': target_name,
                'old_id': old_speaker,
                'new_id': new_speaker_id,
                'title': title[:60]
            })
            
            # UPDATE
            api('patch', 'influencer_signals', 
                params={'id': f'eq.{sig["id"]}'},
                data={'speaker_id': new_speaker_id})
    
    # Report
    print(f"\n{'='*60}")
    print(f"재매핑 완료!")
    print(f"변경: {len(changes)}개, 에러: {len(errors)}개")
    print(f"{'='*60}")
    
    if changes:
        print("\n변경 내역:")
        for c in changes:
            print(f"  [{c['stock']}] {c['old_speaker']} → {c['new_speaker']} | {c['title']}")
    
    if errors:
        print(f"\n에러/스킵: {len(errors)}개")
        for e in errors[:5]:
            print(f"  {e}")
    
    # Save report
    report = {'changes': changes, 'errors': errors, 'total_signals': len(all_signals)}
    with open(Path(__file__).parent.parent / 'sampro_remap_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n리포트 저장: sampro_remap_report.json")

if __name__ == '__main__':
    main()
