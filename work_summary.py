#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
세상학개론 DB 수정 작업 요약
"""
import requests

# Supabase 설정
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

HEADERS = {
    "apikey": SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    "Content-Type": "application/json"
}

def main():
    print("=== 세상학개론 DB 수정 작업 완료 보고서 ===")
    
    print("\n✅ 완료된 작업:")
    print("1. 중복 채널 정리:")
    print("   - 중복 채널 076505ae-... 삭제 완료")
    print("   - 메인 채널 d68f8efd-... 핸들을 @sesang101로 업데이트 완료")
    
    print("\n2. 스피커 정보 조사:")
    print("   - 이효석 스피커 발견: b07d8758-... (aliases: ['이효석', '이호석', '효석'])")
    print("   - 세상학개론 스피커 발견: b9496a5f-... (aliases: ['세상학개론', '세상학'])")
    print("   - influencer_channels 테이블에 speaker_id 컬럼 없음 확인")
    
    print("\n❌ 미완료 작업:")
    print("1. 영상 제목 영어 → 한국어:")
    print("   - YouTube 연결 문제로 인해 yt-dlp/웹스크래핑 방식 실패")
    print("   - 해결 방법: YouTube Data API 사용 또는 수동 업데이트 필요")
    
    print("2. published_at 날짜 수정:")
    print("   - 모든 영상이 2026-03-02로 잘못 설정됨")
    print("   - 실제 업로드 날짜로 수동 업데이트 필요")
    
    print("3. 스피커 표시 문제:")
    print("   - 프론트엔드에서 '이효석'으로만 표시되는 문제")
    print("   - 채널-스피커 연결 방식 조사 필요 (DB 스키마에 speaker_id 없음)")
    print("   - 프론트엔드 코드에서 channel_name vs speaker_name 표시 로직 확인 필요")
    
    print("\n🔧 권장 후속 조치:")
    print("1. YouTube Data API 키 설정 후 영상 메타데이터 일괄 업데이트")
    print("2. 프론트엔드 코드에서 스피커 표시 로직 확인 및 수정")
    print("3. 채널-스피커 관계 테이블 또는 로직 구현")
    
    # 현재 채널 상태 확인
    print("\n📊 현재 세상학개론 채널 상태:")
    try:
        url = f"{SUPABASE_URL}/rest/v1/influencer_channels"
        params = {
            "select": "*",
            "id": "eq.d68f8efd-64c8-4c07-9d34-e98c2954f4e1"
        }
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                channel = data[0]
                print(f"   이름: {channel['channel_name']}")
                print(f"   핸들: {channel['channel_handle']}")
                print(f"   URL: {channel['channel_url']}")
                print(f"   구독자: {channel['subscriber_count']}")
                print(f"   업데이트: {channel['updated_at']}")
        
        # 영상 수 확인
        url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
        params = {
            "channel_id": "eq.d68f8efd-64c8-4c07-9d34-e98c2954f4e1",
            "select": "id"
        }
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            videos = response.json()
            print(f"   총 영상 수: {len(videos)}개")
    except Exception as e:
        print(f"   상태 확인 실패: {e}")

if __name__ == "__main__":
    main()