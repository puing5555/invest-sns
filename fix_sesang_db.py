#!/usr/bin/env python3
"""
세상학개론 DB 데이터 수정 스크립트
"""
import requests
import json
import time
import subprocess
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
DUPLICATE_CHANNEL_ID = "076505ae"

def get_videos():
    """세상학개론 영상 목록 가져오기"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
    params = {
        "channel_id": f"eq.{SESANG_CHANNEL_ID}",
        "select": "id,title,video_id,published_at"
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def get_channels():
    """채널 목록 확인"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_channels"
    params = {
        "select": "id,channel_name,channel_handle",
        "channel_name": "ilike.*세상학개론*"
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def get_speakers():
    """스피커 정보 확인"""
    url = f"{SUPABASE_URL}/rest/v1/speakers"
    params = {
        "select": "id,speaker_name",
        "id": "eq.b07d8758-9ac2-4d85-b123-456789abcdef"
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def get_youtube_title(video_id):
    """yt-dlp로 유튜브 영상 제목 가져오기"""
    try:
        cmd = ["yt-dlp", "--get-title", f"https://youtube.com/watch?v={video_id}"]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error getting title for {video_id}: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception getting title for {video_id}: {e}")
        return None

def get_youtube_upload_date(video_id):
    """yt-dlp로 유튜브 영상 업로드 날짜 가져오기"""
    try:
        cmd = ["yt-dlp", "--get-filename", "-o", "%(upload_date)s", f"https://youtube.com/watch?v={video_id}"]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            date_str = result.stdout.strip()
            # YYYYMMDD 형식을 YYYY-MM-DD로 변환
            if len(date_str) == 8 and date_str.isdigit():
                year = date_str[:4]
                month = date_str[4:6]
                day = date_str[6:8]
                return f"{year}-{month}-{day}"
            return None
        else:
            print(f"Error getting date for {video_id}: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception getting date for {video_id}: {e}")
        return None

def update_video_title(video_id, title):
    """영상 제목 업데이트"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
    params = {"id": f"eq.{video_id}"}
    data = {"title": title}
    
    response = requests.patch(url, headers=HEADERS, params=params, json=data)
    response.raise_for_status()
    return response.status_code == 204

def update_video_date(video_id, published_at):
    """영상 날짜 업데이트"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
    params = {"id": f"eq.{video_id}"}
    data = {"published_at": published_at}
    
    response = requests.patch(url, headers=HEADERS, params=params, json=data)
    response.raise_for_status()
    return response.status_code == 204

def main():
    print("=== 세상학개론 DB 데이터 수정 시작 ===")
    
    # 1. 현재 데이터 상태 확인
    print("\n1. 현재 데이터 확인 중...")
    videos = get_videos()
    channels = get_channels()
    
    print(f"세상학개론 영상 수: {len(videos)}")
    print(f"세상학개론 채널 수: {len(channels)}")
    
    print("\n채널 정보:")
    for channel in channels:
        print(f"- ID: {channel['id']}, 이름: {channel['channel_name']}, 핸들: {channel['channel_handle']}")
    
    print("\n영상 샘플 (처음 3개):")
    for i, video in enumerate(videos[:3]):
        print(f"- {video['title']} (ID: {video['video_id']}, 날짜: {video['published_at']})")
    
    return videos, channels

if __name__ == "__main__":
    videos, channels = main()