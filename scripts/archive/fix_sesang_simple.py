#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
세상학개론 DB 수정 - 간단한 방법
"""
import requests
import json
import time
import re
from datetime import datetime

# Supabase 설정
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

HEADERS = {
    "apikey": SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    "Content-Type": "application/json"
}

SESANG_CHANNEL_ID = "d68f8efd-64c8-4c07-9d34-e98c2954f4e1"
DUPLICATE_CHANNEL_ID = "076505ae-efa7-4e7c-b176-de6d7f75520d"

def get_videos():
    """세상학개론 영상 목록 가져오기"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
    params = {
        "channel_id": f"eq.{SESANG_CHANNEL_ID}",
        "select": "id,title,video_id,published_at",
        "order": "created_at.desc"
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def get_channels():
    """채널 목록 가져오기"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_channels"
    params = {
        "select": "id,channel_name,channel_handle"
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    channels = response.json()
    
    # 세상학개론 채널만 필터링
    sesang_channels = [ch for ch in channels if "세상학개론" in ch.get('channel_name', '')]
    return sesang_channels

def get_youtube_info(video_id):
    """유튜브 페이지에서 제목과 날짜 가져오기"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        url = f"https://www.youtube.com/watch?v={video_id}"
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            html = response.text
            
            # 제목 추출
            title_match = re.search(r'"title":"([^"]+)"', html)
            title = None
            if title_match:
                title = title_match.group(1)
                # 유니코드 이스케이프 해제
                title = title.encode('utf-8').decode('unicode_escape')
                # HTML 엔티티 해제
                title = title.replace('\\u0026', '&').replace('\\u003c', '<').replace('\\u003e', '>')
            
            # 업로드 날짜 추출
            date_match = re.search(r'"uploadDate":"([^"]+)"', html)
            upload_date = None
            if date_match:
                upload_date = date_match.group(1)  # ISO 형식
            
            return title, upload_date
        
        return None, None
    
    except Exception as e:
        print(f"[ERROR] YouTube 정보 가져오기 실패 {video_id}: {e}")
        return None, None

def update_video(video_id, title=None, published_at=None):
    """영상 정보 업데이트"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
    params = {"id": f"eq.{video_id}"}
    data = {}
    
    if title:
        data["title"] = title
    if published_at:
        data["published_at"] = published_at
    
    if not data:
        return False
        
    response = requests.patch(url, headers=HEADERS, params=params, json=data)
    
    if response.status_code == 204:
        return True
    else:
        print(f"[ERROR] 업데이트 실패: {video_id} -> {response.status_code}")
        return False

def delete_channel(channel_id):
    """채널 삭제"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_channels"
    params = {"id": f"eq.{channel_id}"}
    
    response = requests.delete(url, headers=HEADERS, params=params)
    return response.status_code == 204

def update_channel_handle(channel_id, new_handle):
    """채널 핸들 업데이트"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_channels"
    params = {"id": f"eq.{channel_id}"}
    data = {"channel_handle": new_handle}
    
    response = requests.patch(url, headers=HEADERS, params=params, json=data)
    return response.status_code == 204

def main():
    print("=== 세상학개론 DB 수정 작업 ===")
    
    # 1. 채널 정리부터 시작
    print("\n=== 문제 3: 중복 채널 정리 ===")
    channels = get_channels()
    print(f"세상학개론 채널 수: {len(channels)}")
    
    for channel in channels:
        print(f"- ID: {channel['id'][:8]}..., 이름: {channel['channel_name']}, 핸들: {channel['channel_handle']}")
    
    # 중복 채널 삭제
    if delete_channel(DUPLICATE_CHANNEL_ID):
        print(f"[OK] 중복 채널 삭제 완료: {DUPLICATE_CHANNEL_ID}")
    else:
        print(f"[ERROR] 중복 채널 삭제 실패: {DUPLICATE_CHANNEL_ID}")
    
    # 메인 채널 핸들 업데이트
    if update_channel_handle(SESANG_CHANNEL_ID, "@sesang101"):
        print(f"[OK] 채널 핸들 업데이트 완료: @sesang101")
    else:
        print(f"[ERROR] 채널 핸들 업데이트 실패")
    
    # 2. 영상 제목/날짜 수정 (처음 5개만 테스트)
    print("\n=== 문제 1&2: 영상 제목/날짜 수정 ===")
    videos = get_videos()
    print(f"총 {len(videos)}개 영상 (처음 5개만 테스트)")
    
    success_count = 0
    error_count = 0
    
    for i, video in enumerate(videos[:5]):  # 처음 5개만
        print(f"\n[{i+1}/5] 처리 중: {video['video_id']}")
        print(f"현재 제목: {video['title']}")
        print(f"현재 날짜: {video['published_at']}")
        
        # YouTube에서 정보 가져오기
        new_title, new_date = get_youtube_info(video['video_id'])
        
        if new_title:
            print(f"새 제목: {new_title}")
        if new_date:
            print(f"새 날짜: {new_date}")
        
        # 업데이트
        if new_title or new_date:
            if update_video(video['id'], new_title, new_date):
                print(f"[OK] 업데이트 완료")
                success_count += 1
            else:
                error_count += 1
        else:
            print(f"[ERROR] 새 정보를 가져올 수 없음")
            error_count += 1
        
        time.sleep(2)  # 레이트 리밋 방지
    
    print(f"\n=== 테스트 결과 ===")
    print(f"성공: {success_count}, 실패: {error_count}")

if __name__ == "__main__":
    main()