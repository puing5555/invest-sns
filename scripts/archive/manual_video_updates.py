#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수동 영상 제목/날짜 업데이트 (몇 개 샘플)
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

SESANG_CHANNEL_ID = "d68f8efd-64c8-4c07-9d34-e98c2954f4e1"

# 수동 업데이트할 영상들 (유튜브에서 직접 확인한 정보)
MANUAL_UPDATES = [
    {
        "video_id": "BeEHwOe-J98", 
        "title": "새해 시장 폭락 속에서 팰런티어의 미래",  # 예시
        "published_at": "2025-01-15T00:00:00+00:00"  # 예시
    },
    {
        "video_id": "J5_S29fQybw",
        "title": "엔비디아 주가 4년만에 30조가 사라질까?",  # 예시  
        "published_at": "2025-01-20T00:00:00+00:00"  # 예시
    }
]

def get_videos():
    """세상학개론 영상 목록 가져오기"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
    params = {
        "channel_id": f"eq.{SESANG_CHANNEL_ID}",
        "select": "id,title,video_id,published_at",
        "order": "created_at.desc",
        "limit": 10
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def update_video_info(db_id, title=None, published_at=None):
    """영상 정보 업데이트"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
    params = {"id": f"eq.{db_id}"}
    data = {}
    
    if title:
        data["title"] = title
    if published_at:
        data["published_at"] = published_at
    
    if not data:
        return False
        
    response = requests.patch(url, headers=HEADERS, params=params, json=data)
    return response.status_code == 204

def main():
    print("=== Manual Video Updates ===")
    
    # 영상 목록 가져오기
    videos = get_videos()
    print(f"Found {len(videos)} videos")
    
    success_count = 0
    
    # 수동 업데이트 적용
    for update in MANUAL_UPDATES:
        target_video_id = update["video_id"]
        
        # 해당 영상 찾기
        target_video = None
        for video in videos:
            if video["video_id"] == target_video_id:
                target_video = video
                break
        
        if target_video:
            print(f"\nUpdating video: {target_video_id}")
            print(f"Current title: {target_video['title']}")
            print(f"New title: {update['title']}")
            print(f"Current date: {target_video['published_at']}")
            print(f"New date: {update['published_at']}")
            
            if update_video_info(target_video["id"], update["title"], update["published_at"]):
                print("SUCCESS: Updated")
                success_count += 1
            else:
                print("ERROR: Update failed")
        else:
            print(f"Video not found: {target_video_id}")
    
    print(f"\n=== Summary ===")
    print(f"Manual updates completed: {success_count}/{len(MANUAL_UPDATES)}")
    
    # 업데이트된 데이터 확인
    updated_videos = get_videos()
    print(f"\nUpdated video list (first 5):")
    for i, video in enumerate(updated_videos[:5]):
        print(f"{i+1}. {video['title'][:60]}... ({video['published_at'][:10]})")

if __name__ == "__main__":
    main()