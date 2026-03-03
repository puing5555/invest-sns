#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase REST API로 직접 시그널 조회
"""

import os
import re
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

def extract_video_id_from_url(video_url: str) -> str:
    """YouTube URL에서 video_id 추출"""
    if not video_url:
        return ""
    patterns = [
        r'v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'embed/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, video_url)
        if match:
            return match.group(1)
    return ""

def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("X Supabase 설정이 없습니다.")
        return
    
    # Supabase REST API 호출
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
    
    try:
        # 먼저 간단하게 전체 조회
        response = requests.get(url, headers=headers)
        
        print(f"HTTP Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
            return
        
        signals = response.json()
        total_count = len(signals)
        
        print(f"\n{'='*80}")
        print(f"Supabase DB 시그널 상태 분석")
        print(f"{'='*80}")
        print(f"총 시그널 수: {total_count}개\n")
        
        if total_count == 0:
            print("시그널이 없습니다.")
            return
        
        # 첫 번째 시그널 구조 확인
        if signals:
            print("첫 번째 시그널 구조:")
            first_signal = signals[0]
            for key, value in first_signal.items():
                print(f"  {key}: {type(value).__name__} = {str(value)[:100]}")
            print()
        
        # 타임스탬프 필드가 있는지 확인
        timestamp_field = None
        if signals:
            for field in ['timestamp_seconds', 'timestamp', 'time_seconds']:
                if field in signals[0]:
                    timestamp_field = field
                    break
        
        if not timestamp_field:
            print("타임스탬프 필드를 찾을 수 없습니다.")
            return
        
        print(f"타임스탬프 필드: {timestamp_field}")
        
        # 타임스탬프 분석
        zero_timestamps = []
        low_timestamps = []  # 60초 미만
        normal_timestamps = []
        
        for signal in signals:
            ts = signal.get(timestamp_field, 0)
            if isinstance(ts, (int, float)):
                if ts == 0:
                    zero_timestamps.append(signal)
                elif ts < 60:
                    low_timestamps.append(signal)
                else:
                    normal_timestamps.append(signal)
        
        print(f"\n타임스탬프 분석:")
        print(f"  - 0초 (시작부분): {len(zero_timestamps)}개")
        print(f"  - 60초 미만: {len(low_timestamps)}개")
        print(f"  - 60초 이상: {len(normal_timestamps)}개\n")
        
        # 필드 분석
        required_fields = ['video_url', 'key_quote']
        missing_fields = []
        
        for field in required_fields:
            if not any(field in signal for signal in signals):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"누락된 필수 필드: {missing_fields}")
        
        # 0초 타임스탬프 상세 분석 (처음 5개)
        if zero_timestamps:
            print(f"0초 타임스탬프 시그널 상세 분석 (처음 5개):")
            for i, signal in enumerate(zero_timestamps[:5]):
                print(f"  {i+1}. ID: {signal.get('id', 'N/A')}")
                video_url = signal.get('video_url', '')
                video_id = extract_video_id_from_url(video_url)
                print(f"     Video ID: {video_id}")
                key_quote = signal.get('key_quote', '')
                print(f"     Quote: {key_quote[:80]}...")
                print(f"     Stock: {signal.get('stock', 'N/A')}")
                print()
        
        print(f"타임스탬프 교정이 필요한 시그널: 약 {len(zero_timestamps) + len(low_timestamps)}개")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()