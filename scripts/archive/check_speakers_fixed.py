#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
문제 4: 스피커 표시 확인 (수정됨)
"""
import requests
import json

# Supabase 설정
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

HEADERS = {
    "apikey": SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    "Content-Type": "application/json"
}

SESANG_CHANNEL_ID = "d68f8efd-64c8-4c07-9d34-e98c2954f4e1"

def get_speakers():
    """모든 스피커 확인"""
    url = f"{SUPABASE_URL}/rest/v1/speakers"
    params = {
        "select": "id,name,aliases"
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def get_channel_details():
    """세상학개론 채널 상세 정보"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_channels"
    params = {
        "select": "*",
        "id": f"eq.{SESANG_CHANNEL_ID}"
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def create_new_speaker(name, aliases=None):
    """새 스피커 생성"""
    url = f"{SUPABASE_URL}/rest/v1/speakers"
    data = {
        "name": name,
        "aliases": aliases or [name]
    }
    
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code == 201:
        return response.json()[0]['id']
    else:
        print(f"Error creating speaker: {response.status_code} - {response.text}")
        return None

def main():
    print("=== Speaker Analysis ===")
    
    # 모든 스피커 확인
    speakers = get_speakers()
    print(f"Total speakers: {len(speakers)}")
    
    hyoseok_found = False
    for speaker in speakers:
        name = speaker.get('name', '')
        aliases = speaker.get('aliases', [])
        print(f"Speaker: {speaker['id'][:8]}... - {name} (aliases: {aliases})")
        
        if any("효석" in str(alias) for alias in aliases + [name]):
            print(f"  -> HYOSEOK FOUND: {name}")
            hyoseok_found = True
    
    if not hyoseok_found:
        print("No Hyoseok speaker found")
    
    # 채널 상세 정보
    channel_details = get_channel_details()
    if channel_details:
        channel = channel_details[0]
        print(f"\nSesang Channel:")
        print(f"Name: {channel['channel_name']}")
        print(f"Handle: {channel['channel_handle']}")
        print(f"Speaker ID: {channel.get('speaker_id', 'None')}")
    
    # 해결 방법: 새 스피커 생성
    print(f"\n=== Creating Solution ===")
    new_speaker_name = "세상학개론 이효석"
    new_speaker_aliases = ["세상학개론 이효석", "이효석", "Lee Hyoseok", "Sesang Hakgaeron"]
    
    new_speaker_id = create_new_speaker(new_speaker_name, new_speaker_aliases)
    if new_speaker_id:
        print(f"SUCCESS: Created speaker '{new_speaker_name}' with ID: {new_speaker_id}")
        
        # 채널에 새 스피커 연결
        url = f"{SUPABASE_URL}/rest/v1/influencer_channels"
        params = {"id": f"eq.{SESANG_CHANNEL_ID}"}
        data = {"speaker_id": new_speaker_id}
        
        response = requests.patch(url, headers=HEADERS, params=params, json=data)
        if response.status_code == 204:
            print(f"SUCCESS: Updated channel speaker to {new_speaker_id}")
        else:
            print(f"ERROR: Failed to update channel speaker - {response.status_code}")
    else:
        print("FAILED: Could not create new speaker")

if __name__ == "__main__":
    main()