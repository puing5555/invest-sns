#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
현재 DB 자막 상태 분석 스크립트
"""

import os
import requests
from dotenv import load_dotenv

# .env.local 로드
load_dotenv('.env.local')

# Supabase 설정
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

HEADERS = {
    'apikey': SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json'
}

print("=== 현재 DB 자막 상태 분석 ===")

try:
    # 모든 영상의 자막 상태 조회
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos?select=video_id,subtitle_text"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"[ERROR] DB 조회 실패: {response.status_code}")
        exit(1)
    
    data = response.json()
    print(f"[OK] 총 {len(data)}개 영상 조회 완료")
    
    # 자막 상태 분석
    no_subtitle = 0         # 자막 없음
    subtitle_5000 = 0       # 정확히 5000자 (잘림 추정)
    subtitle_short = 0      # 5000자 미만
    subtitle_long = 0       # 5000자 초과
    
    need_update_videos = []  # 업데이트 필요한 영상들
    
    for row in data:
        video_id = row['video_id']
        subtitle = row.get('subtitle_text', '')
        
        if not subtitle:
            no_subtitle += 1
            need_update_videos.append({'video_id': video_id, 'reason': '자막없음', 'length': 0})
        elif len(subtitle) == 5000:
            subtitle_5000 += 1
            need_update_videos.append({'video_id': video_id, 'reason': '5000자잘림', 'length': 5000})
        elif len(subtitle) < 5000:
            subtitle_short += 1
        else:
            subtitle_long += 1
    
    print("\n=== 자막 상태 통계 ===")
    print(f"자막 없음: {no_subtitle}개")
    print(f"5000자 잘림: {subtitle_5000}개")
    print(f"5000자 미만: {subtitle_short}개")
    print(f"5000자 초과: {subtitle_long}개")
    print(f"업데이트 필요: {len(need_update_videos)}개")
    
    print("\n=== 업데이트 필요 영상 목록 ===")
    for i, video in enumerate(need_update_videos[:10], 1):  # 처음 10개만 표시
        print(f"{i}. {video['video_id']} ({video['reason']}, {video['length']}자)")
    
    if len(need_update_videos) > 10:
        print(f"... 및 {len(need_update_videos) - 10}개 더")
    
    # 샘플 자막 내용 확인 (5000자 잘림 추정)
    if subtitle_5000 > 0:
        print("\n=== 5000자 잘림 샘플 확인 ===")
        for row in data:
            if row.get('subtitle_text') and len(row['subtitle_text']) == 5000:
                video_id = row['video_id']
                subtitle = row['subtitle_text']
                print(f"샘플 영상: {video_id}")
                print("마지막 100자:")
                print(subtitle[-100:])
                print("잘림 추정:", subtitle.endswith('['))  # [ 로 끝나면 잘림 가능성
                break
                
    print(f"\n분석 완료. 업데이트 대상: {len(need_update_videos)}개 영상")
    
except Exception as e:
    print(f"[ERROR] 분석 중 예외 발생: {e}")