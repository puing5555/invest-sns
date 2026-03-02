#!/usr/bin/env python3
"""
세상학개론 영상 정보를 influencer_videos 테이블에 먼저 INSERT
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

def get_speaker_id():
    """세상학개론 speaker ID 조회"""
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/speakers?name=eq.세상학개론",
        headers=headers
    )
    
    if resp.status_code == 200:
        speakers = resp.json()
        if speakers:
            return speakers[0]['id']
    
    return None

def insert_videos():
    """영상 정보 INSERT"""
    # 1. 결과 파일 로드
    with open('data/sesang_analysis_b1.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 2. Speaker ID 확보
    speaker_id = get_speaker_id()
    if not speaker_id:
        print("Speaker ID를 찾을 수 없습니다.")
        return
    
    # 3. 영상 목록 추출
    videos_to_insert = []
    for result in data['results']:
        video_id = result['video_id']
        title = result['title']
        
        # 기존 영상 확인
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/influencer_videos?youtube_video_id=eq.{video_id}",
            headers=headers
        )
        
        if resp.status_code == 200 and resp.json():
            print(f"이미 존재: {video_id} - {title[:30]}...")
            continue
        
        videos_to_insert.append({
            'youtube_video_id': video_id,
            'title': title,
            'speaker_id': speaker_id,
            'channel_url': 'https://www.youtube.com/@sesang101',
            'published_at': datetime.now().isoformat(),  # 임시값
            'created_at': datetime.now().isoformat()
        })
    
    print(f"INSERT할 영상: {len(videos_to_insert)}개")
    
    # 4. 영상 INSERT
    inserted_count = 0
    
    for video in videos_to_insert:
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/influencer_videos",
            headers=headers,
            json=video
        )
        
        if resp.status_code == 201:
            inserted_count += 1
            print(f"OK {video['youtube_video_id']} - {video['title'][:40]}...")
        else:
            print(f"ERROR INSERT failed: {resp.status_code} - {resp.text}")
    
    print(f"\n완료! {inserted_count}개 영상이 INSERT되었습니다.")
    return inserted_count

if __name__ == '__main__':
    insert_videos()