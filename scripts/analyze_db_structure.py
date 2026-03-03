#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DB 구조 상세 분석 및 video_url 필드 확인
"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

def main():
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # 1. influencer_signals 테이블 분석
    print("=== influencer_signals 테이블 분석 ===")
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
    response = requests.get(f"{url}?limit=3", headers=headers)
    
    if response.status_code == 200:
        signals = response.json()
        if signals:
            print("샘플 시그널 필드:")
            for key, value in signals[0].items():
                print(f"  {key}: {type(value).__name__} = {str(value)[:100]}")
        print()
    
    # 2. influencer_videos 테이블 확인
    print("=== influencer_videos 테이블 확인 ===")
    videos_url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
    response = requests.get(f"{videos_url}?limit=3", headers=headers)
    
    if response.status_code == 200:
        videos = response.json()
        print(f"videos 테이블: {len(videos)}개")
        if videos:
            print("샘플 비디오 필드:")
            for key, value in videos[0].items():
                print(f"  {key}: {type(value).__name__} = {str(value)[:100]}")
        print()
    else:
        print(f"videos 테이블 조회 실패: {response.status_code}")
    
    # 3. JOIN 쿼리로 video_url 정보 가져오기
    print("=== JOIN 쿼리 시도 ===")
    join_url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
    params = {
        'select': 'id,timestamp,key_quote,stock,video_id,influencer_videos(video_id,title)',
        'limit': '5'
    }
    response = requests.get(join_url, headers=headers, params=params)
    
    if response.status_code == 200:
        joined_data = response.json()
        print("JOIN 결과:")
        for item in joined_data:
            print(f"  Signal ID: {item.get('id')}")
            print(f"  Video ID: {item.get('video_id')}")
            print(f"  Timestamp: {item.get('timestamp')}")
            print(f"  Video Info: {item.get('influencer_videos')}")
            print()
    else:
        print(f"JOIN 쿼리 실패: {response.status_code}")
        print(response.text)
    
    # 4. 시그널에서 타임스탬프 형식 분석
    print("=== 타임스탬프 형식 분석 ===")
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
    response = requests.get(f"{url}?limit=10", headers=headers)
    
    if response.status_code == 200:
        signals = response.json()
        timestamp_formats = {}
        
        for signal in signals:
            timestamp = signal.get('timestamp', '')
            if timestamp:
                # 형식 분류
                if ':' in timestamp:
                    if timestamp.count(':') == 1:
                        timestamp_formats['MM:SS'] = timestamp_formats.get('MM:SS', 0) + 1
                    else:
                        timestamp_formats['HH:MM:SS'] = timestamp_formats.get('HH:MM:SS', 0) + 1
                elif timestamp.isdigit():
                    timestamp_formats['seconds'] = timestamp_formats.get('seconds', 0) + 1
                else:
                    timestamp_formats['other'] = timestamp_formats.get('other', 0) + 1
        
        print("타임스탬프 형식 분포:")
        for fmt, count in timestamp_formats.items():
            print(f"  {fmt}: {count}개")
        
        # 샘플 타임스탬프들
        print("\n샘플 타임스탬프들:")
        for i, signal in enumerate(signals[:5]):
            print(f"  {i+1}. {signal.get('timestamp')} | {signal.get('key_quote', '')[:50]}...")

if __name__ == '__main__':
    main()