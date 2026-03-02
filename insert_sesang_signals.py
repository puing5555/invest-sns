#!/usr/bin/env python3
"""
세상학개론 시그널 DB INSERT 스크립트
"""

import json
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

headers = {
    'apikey': SERVICE_ROLE_KEY,
    'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
    'Content-Type': 'application/json'
}

def get_or_create_speaker():
    """세상학개론 speaker 조회/생성"""
    # 1. 기존 speaker 조회
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/speakers?name=eq.세상학개론",
        headers=headers
    )
    
    if resp.status_code == 200:
        speakers = resp.json()
        if speakers:
            print(f"기존 speaker 발견: {speakers[0]['id']}")
            return speakers[0]['id']
    
    # 2. speaker 생성
    speaker_data = {
        'name': '세상학개론',
        'platform': 'youtube',
        'channel_url': 'https://www.youtube.com/@sesang101',
        'created_at': datetime.now().isoformat()
    }
    
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/speakers",
        headers=headers,
        json=speaker_data
    )
    
    if resp.status_code == 201:
        speaker = resp.json()[0]
        print(f"새 speaker 생성: {speaker['id']}")
        return speaker['id']
    else:
        print(f"Speaker 생성 실패: {resp.status_code} - {resp.text}")
        return None

def get_video_uuid(youtube_video_id):
    """YouTube video_id로 influencer_videos 테이블의 UUID 조회"""
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/influencer_videos?youtube_video_id=eq.{youtube_video_id}",
        headers=headers
    )
    
    if resp.status_code == 200:
        videos = resp.json()
        if videos:
            return videos[0]['id']
    
    print(f"Warning: video_id {youtube_video_id}에 대한 UUID를 찾을 수 없습니다")
    return None

def insert_signals():
    """시그널 INSERT"""
    # 1. 결과 파일 로드
    with open('data/sesang_analysis_b1.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 2. Speaker ID 확보
    speaker_id = get_or_create_speaker()
    if not speaker_id:
        print("Speaker ID를 확보할 수 없어 작업을 중단합니다.")
        return
    
    # 3. 유효한 시그널 추출
    valid_signals = []
    for result in data['results']:
        if 'raw_result' in result and 'signals' in result['raw_result']:
            for signal in result['raw_result']['signals']:
                if (signal.get('stock') and 
                    signal.get('signal_type') and 
                    signal.get('key_quote') and 
                    signal.get('reasoning') and 
                    signal.get('timestamp')):
                    
                    # Video UUID 조회
                    video_uuid = get_video_uuid(result['video_id'])
                    if video_uuid:
                        valid_signals.append({
                            'video_id': video_uuid,
                            'youtube_video_id': result['video_id'],
                            'title': result['title'],
                            'signal': signal
                        })
    
    print(f"DB INSERT 대상: {len(valid_signals)}개 시그널")
    
    # 4. 시그널 INSERT
    inserted_count = 0
    
    for vs in valid_signals:
        signal = vs['signal']
        
        # 시그널 타입 매핑 (한글 → 한글 그대로)
        signal_type = signal.get('signal_type', '중립')
        
        # mention_type 설정 (기본값: 논거)
        mention_type = '논거'
        
        signal_data = {
            'video_id': vs['video_id'],
            'speaker_id': speaker_id,
            'stock': signal.get('stock', ''),
            'ticker': signal.get('ticker', ''),
            'market': 'US',  # 기본값
            'signal': signal_type,
            'confidence': int(signal.get('confidence', 5)),
            'timestamp': signal.get('timestamp', ''),
            'key_quote': signal.get('key_quote', ''),
            'reasoning': signal.get('reasoning', ''),
            'pipeline_version': 'V10.7',
            'review_status': 'pending',
            'mention_type': mention_type,
            'created_at': datetime.now().isoformat()
        }
        
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/influencer_signals",
            headers=headers,
            json=signal_data
        )
        
        if resp.status_code == 201:
            inserted_count += 1
            print(f"✓ {signal.get('stock')} - {signal_type} ({vs['youtube_video_id']})")
        else:
            print(f"✗ INSERT 실패: {resp.status_code} - {resp.text}")
            print(f"   데이터: {signal.get('stock')} - {signal_type}")
    
    print(f"\n완료! {inserted_count}개 시그널이 DB에 INSERT되었습니다.")
    return inserted_count

if __name__ == '__main__':
    insert_signals()