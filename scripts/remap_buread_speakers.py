# -*- coding: utf-8 -*-
"""부읽남TV speaker 재매핑 스크립트"""
import os, re, json, sys
from pathlib import Path
from dotenv import load_dotenv
import requests

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv(Path(__file__).parent.parent / '.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
BUREAD_CHANNEL_ID = '12facb47-407d-4fd3-a310-12dd5a802d1f'

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json; charset=utf-8',
    'Prefer': 'return=representation'
}

# Known speakers (full UUID)
KNOWN_SPEAKERS = {
    '조진표': '6b2696ff-f6a6-424b-a6de-0cd837f7bbb0',
    '배재규': 'd5ea4443-d1cb-4927-aabc-68061f59a3e0',
    '이정윤': 'fcc6738d-49b6-48f0-9ec7-b20ec5594536',
    '김학주': '289de288-d587-4381-9f3d-b03ab63baf21',
    '한정수': 'd4219d6b-f423-423c-9527-7c8dec839618',
}

def api_get(table, params):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{'&'.join(f'{k}={v}' for k,v in params.items())}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()

def api_patch(table, filter_params, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{'&'.join(f'{k}={v}' for k,v in filter_params.items())}"
    r = requests.patch(url, headers=HEADERS, json=data)
    r.raise_for_status()
    return r

def api_post(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS, json=data)
    r.raise_for_status()
    return r.json()

def extract_guest_from_buread_title(title):
    """부읽남TV 제목에서 게스트명 추출
    패턴: [게스트명 직함 부수] 또는 제목 끝에 [게스트명 ...]
    예: "... [배재규 대표]", "... [이정윤 세무사 1부]", "... [김학주 교수]"
    """
    # Find all [...] blocks
    brackets = re.findall(r'\[([^\]]+)\]', title)
    for block in brackets:
        # Skip pure content blocks (no Korean name pattern)
        # Look for "이름 직함" pattern
        match = re.match(r'([가-힣]{2,3})\s+(대표|교수|세무사|작가|PB|애널|본부장|센터장|부사장|사장|이사|팀장|위원|연구원|박사)', block)
        if match:
            return match.group(1)
        # Also try: "이름 직함 N부"
        match2 = re.match(r'([가-힣]{2,3})\s+\S+', block)
        if match2:
            name = match2.group(1)
            # Filter out common non-name words
            if name not in ('투자', '경제', '부동', '주식', '미국', '한국', '글로', '오늘', '내일', '이번', '다음'):
                return name
    return None

def find_or_create_speaker(name):
    if name in KNOWN_SPEAKERS:
        return KNOWN_SPEAKERS[name], False
    
    # Search DB
    results = api_get('speakers', {'name': f'eq.{name}', 'select': 'id,name', 'limit': '1'})
    if results:
        KNOWN_SPEAKERS[name] = results[0]['id']
        return results[0]['id'], False
    
    # Create
    new = api_post('speakers', {'name': name})
    new_id = new[0]['id'] if isinstance(new, list) else new['id']
    KNOWN_SPEAKERS[name] = new_id
    print(f"  ✨ 새 speaker 생성: {name} → {new_id[:8]}")
    return new_id, True

def main():
    # 1. Get videos
    print("1. 부읽남TV 영상 조회...")
    videos = api_get('influencer_videos', {
        'channel_id': f'eq.{BUREAD_CHANNEL_ID}',
        'select': 'id,title'
    })
    print(f"   영상 {len(videos)}개")
    
    video_map = {v['id']: v['title'] for v in videos}
    
    # 2. Get signals per video
    print("2. 시그널 조회...")
    all_signals = []
    for vid in video_map:
        sigs = api_get('influencer_signals', {
            'video_id': f'eq.{vid}',
            'select': 'id,video_id,speaker_id,stock,key_quote,signal'
        })
        all_signals.extend(sigs)
    print(f"   시그널 {len(all_signals)}개")
    
    # 3. Remap
    print("\n3. Speaker 재매핑 시작...")
    changes = []
    errors = []
    kept = 0
    
    for sig in all_signals:
        title = video_map.get(sig['video_id'], '')
        guest_name = extract_guest_from_buread_title(title)
        old_speaker_id = sig['speaker_id']
        
        if not guest_name:
            errors.append({
                'signal_id': sig['id'],
                'title': title[:80],
                'reason': 'no_guest_in_title'
            })
            continue
        
        try:
            new_speaker_id, created = find_or_create_speaker(guest_name)
        except Exception as e:
            errors.append({'signal_id': sig['id'], 'name': guest_name, 'error': str(e)})
            continue
        
        if old_speaker_id == new_speaker_id:
            kept += 1
            continue
        
        # Find old name
        old_name = next((k for k,v in KNOWN_SPEAKERS.items() if v == old_speaker_id), old_speaker_id[:8])
        
        changes.append({
            'signal_id': sig['id'],
            'stock': sig.get('stock', ''),
            'old_speaker': old_name,
            'new_speaker': guest_name,
            'old_id': old_speaker_id,
            'new_id': new_speaker_id,
            'title': title[:80]
        })
        
        # UPDATE
        api_patch('influencer_signals',
                  {'id': f'eq.{sig["id"]}'},
                  {'speaker_id': new_speaker_id})
    
    # Report
    print(f"\n{'='*60}")
    print(f"부읽남TV 재매핑 완료!")
    print(f"변경: {len(changes)}개, 유지: {kept}개, 에러: {len(errors)}개")
    print(f"{'='*60}")
    
    if changes:
        print("\n변경 내역:")
        # Group by new speaker
        by_speaker = {}
        for c in changes:
            ns = c['new_speaker']
            by_speaker.setdefault(ns, []).append(c)
        
        for speaker, items in sorted(by_speaker.items()):
            print(f"\n  → {speaker} ({len(items)}개):")
            for c in items:
                print(f"    [{c['stock']}] {c['old_speaker']} → {c['new_speaker']}")
    
    if errors:
        print(f"\n에러/스킵: {len(errors)}개")
        for e in errors[:10]:
            print(f"  {e.get('title', e.get('name', ''))}: {e.get('reason', e.get('error', ''))}")
    
    # Save report
    report = {'changes': changes, 'errors': errors, 'kept': kept, 'total_signals': len(all_signals)}
    with open(Path(__file__).parent.parent / 'buread_remap_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n리포트: buread_remap_report.json")

if __name__ == '__main__':
    main()
