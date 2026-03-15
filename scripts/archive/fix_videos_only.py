#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
세상학개론 영상 정보만 수정 (한글 출력 최소화)
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
            
            # 제목 추출 (더 안전한 방법)
            title_patterns = [
                r'"videoDetails":\s*{[^}]*"title":"([^"]+)"',
                r'<meta property="og:title" content="([^"]*)"',
                r'"title":"([^"]+)"'
            ]
            
            title = None
            for pattern in title_patterns:
                match = re.search(pattern, html)
                if match:
                    title = match.group(1)
                    # 유니코드 이스케이프 및 HTML 엔티티 처리
                    try:
                        title = title.encode('latin1').decode('unicode_escape')
                    except:
                        pass
                    title = title.replace('\\u0026', '&').replace('\\u003c', '<').replace('\\u003e', '>')
                    break
            
            # 업로드 날짜 추출
            date_patterns = [
                r'"uploadDate":"([^"]+)"',
                r'"publishDate":"([^"]+)"',
                r'<meta itemprop="uploadDate" content="([^"]*)"'
            ]
            
            upload_date = None
            for pattern in date_patterns:
                match = re.search(pattern, html)
                if match:
                    upload_date = match.group(1)
                    # ISO 형식을 우리가 원하는 형식으로 변환
                    try:
                        if 'T' in upload_date:
                            upload_date = upload_date.split('T')[0] + 'T00:00:00+00:00'
                    except:
                        pass
                    break
            
            return title, upload_date
        
        return None, None
    
    except Exception as e:
        print(f"ERROR: YouTube info failed for {video_id}: {str(e)}")
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
        
    try:
        response = requests.patch(url, headers=HEADERS, params=params, json=data)
        return response.status_code == 204
    except Exception as e:
        print(f"ERROR: Update failed for {video_id}: {str(e)}")
        return False

def main():
    print("=== Video Update Process ===")
    
    # 영상 목록 가져오기
    videos = get_videos()
    total = len(videos)
    print(f"Total videos: {total}")
    
    success_count = 0
    error_count = 0
    processed = 0
    
    for video in videos:
        processed += 1
        video_id = video['video_id']
        
        print(f"[{processed}/{total}] Processing: {video_id}")
        
        # 현재 정보 (간단히)
        current_title_preview = video['title'][:50] + "..." if len(video['title']) > 50 else video['title']
        print(f"Current title: {current_title_preview}")
        print(f"Current date: {video['published_at']}")
        
        # YouTube에서 새 정보 가져오기
        new_title, new_date = get_youtube_info(video_id)
        
        has_update = False
        if new_title and new_title != video['title']:
            print(f"New title found (length: {len(new_title)})")
            has_update = True
        
        if new_date and new_date != video['published_at']:
            print(f"New date: {new_date}")
            has_update = True
        
        if has_update:
            if update_video(video['id'], new_title, new_date):
                print("SUCCESS: Updated")
                success_count += 1
            else:
                print("ERROR: Update failed")
                error_count += 1
        else:
            print("SKIP: No changes needed")
        
        print(f"Progress: {processed}/{total} (Success: {success_count}, Error: {error_count})")
        print("---")
        
        # 레이트 리밋
        time.sleep(3)
        
        # 처음 10개만 테스트
        if processed >= 10:
            print("=== TEST COMPLETE (First 10 videos) ===")
            break
    
    print(f"\n=== Final Results ===")
    print(f"Processed: {processed}/{total}")
    print(f"Success: {success_count}")
    print(f"Error: {error_count}")

if __name__ == "__main__":
    main()