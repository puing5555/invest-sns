#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase 연결 테스트 스크립트
"""

import os
import requests
from dotenv import load_dotenv

print("테스트 시작...")

# .env.local 로드
load_dotenv('.env.local')

print("환경변수 로딩 완료")

# Supabase 설정
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_SERVICE_KEY 길이: {len(SUPABASE_SERVICE_KEY) if SUPABASE_SERVICE_KEY else 0}")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("[ERROR] Supabase 환경변수가 없습니다.")
    exit(1)

# Supabase REST API 헤더
HEADERS = {
    'apikey': SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json'
}

print("헤더 설정 완료")

try:
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos?select=video_id&limit=3"
    print(f"요청 URL: {url}")
    
    response = requests.get(url, headers=HEADERS)
    print(f"응답 상태코드: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"데이터: {data}")
        print(f"[OK] Supabase 연결 성공. {len(data)}개 레코드 조회")
    else:
        print(f"[ERROR] Supabase 연결 실패: {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"[ERROR] 예외 발생: {e}")

print("테스트 완료")