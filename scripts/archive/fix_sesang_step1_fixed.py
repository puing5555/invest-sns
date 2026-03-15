#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
세상학개론 DB 수정 - 1단계: 제목과 날짜 수정
"""
import requests
import json
import time
import subprocess
import re
from datetime import datetime
import sys
import os

# 한글 출력 설정
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Supabase 설정
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

HEADERS = {
    "apikey": SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    "Content-Type": "application/json"
}

SESANG_CHANNEL_ID = "d68f8efd-64c8-4c07-9d34-e98c2954f4e1"

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

def get_youtube_title(video_id):
    """yt-dlp로 유튜브 영상 제목 가져오기"""
    try:
        cmd = ["python", "-m", "yt_dlp", "--get-title", f"https://youtube.com/watch?v={video_id}"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout:
            title = result.stdout.strip()
            print(f"[OK] 제목 획득: {video_id} -> {title}")
            return title
        else:
            print(f"[ERROR] 제목 오류 {video_id}: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print(f"[ERROR] 제목 타임아웃: {video_id}")
        return None
    except Exception as e:
        print(f"[ERROR] 제목 예외 {video_id}: {e}")
        return None

def get_youtube_upload_date(video_id):
    """yt-dlp로 유튜브 영상 업로드 날짜 가져오기"""
    try:
        cmd = ["python", "-m", "yt_dlp", "--get-filename", "-o", "%(upload_date)s", f"https://youtube.com/watch?v={video_id}"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout:
            date_str = result.stdout.strip()
            # YYYYMMDD 형식을 YYYY-MM-DD로 변환
            if len(date_str) == 8 and date_str.isdigit():
                year = date_str[:4]
                month = date_str[4:6]
                day = date_str[6:8]
                formatted_date = f"{year}-{month}-{day}T00:00:00+00:00"
                print(f"[OK] 날짜 획득: {video_id} -> {formatted_date}")
                return formatted_date
            else:
                print(f"[ERROR] 날짜 형식 오류: {video_id} -> {date_str}")
                return None
        else:
            print(f"[ERROR] 날짜 오류 {video_id}: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print(f"[ERROR] 날짜 타임아웃: {video_id}")
        return None
    except Exception as e:
        print(f"[ERROR] 날짜 예외 {video_id}: {e}")
        return None

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
        update_fields = []
        if title: update_fields.append("제목")
        if published_at: update_fields.append("날짜")
        print(f"[OK] 업데이트 완료: {video_id} ({', '.join(update_fields)})")
        return True
    else:
        print(f"[ERROR] 업데이트 실패: {video_id} -> {response.status_code}")
        return False

def main():
    print("=== 세상학개론 제목/날짜 수정 시작 ===")
    
    # 영상 목록 가져오기
    videos = get_videos()
    print(f"\n총 {len(videos)}개 영상 처리 시작")
    
    success_count = 0
    error_count = 0
    
    for i, video in enumerate(videos):
        print(f"\n[{i+1}/{len(videos)}] 처리 중: {video['video_id']}")
        print(f"현재 제목: {video['title']}")
        print(f"현재 날짜: {video['published_at']}")
        
        # 제목 가져오기
        new_title = get_youtube_title(video['video_id'])
        time.sleep(1)  # 레이트 리밋 방지
        
        # 날짜 가져오기
        new_date = get_youtube_upload_date(video['video_id'])
        time.sleep(2)  # 레이트 리밋 방지
        
        # 업데이트할 내용이 있으면 DB 업데이트
        if new_title or new_date:
            if update_video(video['id'], new_title, new_date):
                success_count += 1
            else:
                error_count += 1
        else:
            print(f"[ERROR] 업데이트할 데이터 없음: {video['video_id']}")
            error_count += 1
        
        # 진행상황 출력
        print(f"진행: {i+1}/{len(videos)} (성공: {success_count}, 실패: {error_count})")
        
        # 처음 3개만 테스트
        if i >= 2:
            print("\n=== 테스트 완료 (처음 3개만) ===")
            break
    
    print(f"\n=== 최종 결과 ===")
    print(f"성공: {success_count}")
    print(f"실패: {error_count}")

if __name__ == "__main__":
    main()