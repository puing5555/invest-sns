#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DB 업데이트 테스트
"""

import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# .env.local 로드
load_dotenv('.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

HEADERS = {
    'apikey': SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json'
}

video_id = "Ke7gQMbIFLI"

print(f"DB 업데이트 테스트: {video_id}")

# 1. 현재 DB의 자막 조회
print("=== 현재 DB 자막 조회 ===")
try:
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos?select=subtitle_text&video_id=eq.{video_id}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        if data and data[0].get('subtitle_text'):
            current_subtitle = data[0]['subtitle_text']
            print(f"현재 DB 자막 길이: {len(current_subtitle)} 문자")
            print("현재 DB 자막 첫 300자:")
            print(current_subtitle[:300])
        else:
            print("현재 DB에 자막이 없습니다.")
            current_subtitle = None
    else:
        print(f"[ERROR] DB 조회 실패: {response.status_code}")
        current_subtitle = None
except Exception as e:
    print(f"[ERROR] DB 조회 중 예외: {e}")
    current_subtitle = None

# 2. 변환된 새 자막 읽기
print("\n=== 새 자막 읽기 ===")
converted_file = Path(f"subs/{video_id}_converted.txt")
if converted_file.exists():
    with open(converted_file, 'r', encoding='utf-8') as f:
        new_subtitle = f.read()
    print(f"새 자막 길이: {len(new_subtitle)} 문자")
    print("새 자막 첫 300자:")
    print(new_subtitle[:300])
else:
    print("[ERROR] 변환된 파일이 없습니다.")
    exit(1)

# 3. 길이 비교
print("\n=== 길이 비교 ===")
if current_subtitle:
    print(f"현재 DB: {len(current_subtitle)} 문자")
    print(f"새 자막: {len(new_subtitle)} 문자")
    print(f"증가량: {len(new_subtitle) - len(current_subtitle)} 문자")
else:
    print(f"현재 DB: 0 문자 (자막 없음)")
    print(f"새 자막: {len(new_subtitle)} 문자")

# 4. DB 업데이트 테스트
print("\n=== DB 업데이트 테스트 ===")
response_input = input("DB에 새 자막을 업데이트하시겠습니까? (y/N): ")

if response_input.lower() == 'y':
    try:
        url = f"{SUPABASE_URL}/rest/v1/influencer_videos?video_id=eq.{video_id}"
        data = {"subtitle_text": new_subtitle}
        
        response = requests.patch(url, headers=HEADERS, json=data)
        
        if response.status_code == 204:
            print("[OK] DB 업데이트 성공!")
            
            # 업데이트 확인
            check_url = f"{SUPABASE_URL}/rest/v1/influencer_videos?select=subtitle_text&video_id=eq.{video_id}"
            check_response = requests.get(check_url, headers=HEADERS)
            
            if check_response.status_code == 200:
                check_data = check_response.json()
                if check_data and check_data[0].get('subtitle_text'):
                    updated_subtitle = check_data[0]['subtitle_text']
                    print(f"업데이트 후 DB 자막 길이: {len(updated_subtitle)} 문자")
                    print("업데이트 확인 완료!")
                    
        else:
            print(f"[ERROR] DB 업데이트 실패: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"[ERROR] DB 업데이트 중 예외: {e}")
else:
    print("업데이트를 취소했습니다.")

print("테스트 완료")