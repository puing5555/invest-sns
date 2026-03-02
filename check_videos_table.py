#!/usr/bin/env python3
"""
influencer_videos 테이블 구조 확인
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

SUPABASE_HEADERS = {
    'apikey': SERVICE_ROLE_KEY,
    'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
    'Content-Type': 'application/json'
}

def main():
    print("Checking influencer_videos table...")
    
    # 테이블 구조 확인 (처음 5개 레코드)
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
    params = {'limit': 5}
    
    response = requests.get(url, headers=SUPABASE_HEADERS, params=params)
    
    if response.status_code == 200:
        videos = response.json()
        print(f"Found {len(videos)} videos")
        
        for i, video in enumerate(videos):
            print(f"\nVideo {i+1}:")
            for key, value in video.items():
                print(f"  {key}: {value}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

    # 특정 video_id로 조회 테스트
    print("\n" + "="*50)
    print("Testing specific video_id lookup...")
    
    # 분석 결과에서 video_id 하나 가져와서 테스트
    with open('sesang_signal_analysis.json', 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    test_video_id = analysis['need_fix_signals'][0]['video_id']
    print(f"Testing video_id: {test_video_id}")
    
    params = {'id': f'eq.{test_video_id}'}
    response = requests.get(url, headers=SUPABASE_HEADERS, params=params)
    
    if response.status_code == 200:
        videos = response.json()
        print(f"Found {len(videos)} matching videos")
        for video in videos:
            print("Video data:")
            for key, value in video.items():
                print(f"  {key}: {value}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()