#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
문제 4: 스피커 표시 확인
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

def get_speakers():
    """모든 스피커 확인"""
    url = f"{SUPABASE_URL}/rest/v1/speakers"
    params = {
        "select": "id,speaker_name"
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def get_channels():
    """채널 정보 확인"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_channels"
    params = {
        "select": "id,channel_name,channel_handle,speaker_id"
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def create_new_speaker(name):
    """새 스피커 생성"""
    url = f"{SUPABASE_URL}/rest/v1/speakers"
    data = {"speaker_name": name}
    
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code == 201:
        return response.json()[0]['id']
    return None

def update_channel_speaker(channel_id, speaker_id):
    """채널의 스피커 업데이트"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_channels"
    params = {"id": f"eq.{channel_id}"}
    data = {"speaker_id": speaker_id}
    
    response = requests.patch(url, headers=HEADERS, params=params, json=data)
    return response.status_code == 204

def main():
    print("=== Speaker Check ===")
    
    # 모든 스피커 확인
    speakers = get_speakers()
    print(f"Total speakers: {len(speakers)}")
    
    # 이효석 스피커 찾기
    hyoseok_speaker = None
    for speaker in speakers:
        print(f"Speaker: {speaker['id'][:8]}... - {speaker['speaker_name']}")
        if "이효석" in speaker['speaker_name'] or "hyoseok" in speaker['speaker_name'].lower():
            hyoseok_speaker = speaker
    
    print(f"\nHyoseok speaker found: {hyoseok_speaker}")
    
    # 채널 정보 확인
    channels = get_channels()
    sesang_channels = [ch for ch in channels if "sesang" in ch.get('channel_name', '').lower() or "세상학개론" in ch.get('channel_name', '')]
    
    print(f"\nSesang channels: {len(sesang_channels)}")
    for channel in sesang_channels:
        print(f"Channel: {channel['id'][:8]}... - {channel['channel_name']} (@{channel['channel_handle']}) - Speaker: {channel.get('speaker_id', 'None')}")
    
    # 해결 방법 제안
    print("\n=== Solution Options ===")
    if hyoseok_speaker:
        print(f"Option 1: Keep existing speaker '{hyoseok_speaker['speaker_name']}' (ID: {hyoseok_speaker['id'][:8]}...)")
    
    print("Option 2: Create new speaker 'Sesang Hakgaeron Lee Hyoseok'")
    print("Option 3: Update existing speaker name")
    
    # 새 스피커 생성 (테스트)
    new_speaker_id = create_new_speaker("Sesang Hakgaeron Lee Hyoseok")
    if new_speaker_id:
        print(f"Created new speaker: {new_speaker_id}")
        
        # 세상학개론 채널에 새 스피커 연결
        sesang_channel_id = "d68f8efd-64c8-4c07-9d34-e98c2954f4e1"
        if update_channel_speaker(sesang_channel_id, new_speaker_id):
            print(f"Updated channel speaker successfully")
        else:
            print("Failed to update channel speaker")
    else:
        print("Failed to create new speaker")

if __name__ == "__main__":
    main()