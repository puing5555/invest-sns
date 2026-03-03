#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두 번째 영상 테스트
"""

import os
import requests
from dotenv import load_dotenv

# .env.local 로드
load_dotenv('.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

HEADERS = {
    'apikey': SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json'
}

video_id = "1NUkBQ9MQf8"  # 두 번째 영상

print(f"두 번째 영상 테스트: {video_id}")

# 현재 DB의 자막 상태 확인
print("=== DB 자막 상태 확인 ===")
try:
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos?select=subtitle_text&video_id=eq.{video_id}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        if data and data[0].get('subtitle_text'):
            current_subtitle = data[0]['subtitle_text']
            print(f"현재 DB 자막 길이: {len(current_subtitle)} 문자")
            print("현재 DB 자막 첫 500자:")
            print(current_subtitle[:500])
            
            if len(current_subtitle) == 5000:
                print("[발견] 5000자로 잘려있는 자막입니다!")
                print("이 영상은 자막 업데이트 대상입니다.")
            elif '[' in current_subtitle and ']:' in current_subtitle:
                print("[발견] 이미 타임스탬프 형식의 자막이 있습니다.")
            else:
                print("[발견] 일반 텍스트 형식의 자막입니다.")
        else:
            print("현재 DB에 자막이 없습니다.")
            current_subtitle = None
    else:
        print(f"[ERROR] DB 조회 실패: {response.status_code}")
        current_subtitle = None
except Exception as e:
    print(f"[ERROR] DB 조회 중 예외: {e}")
    current_subtitle = None

print("테스트 완료")