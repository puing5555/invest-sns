#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스피커 연결 수정
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

# IDs from previous output
SESANG_CHANNEL_ID = "d68f8efd-64c8-4c07-9d34-e98c2954f4e1"
HYOSEOK_SPEAKER_ID = "b07d8758-9ac2-4d85-b123-456789abcdef"  # 이효석
SESANG_SPEAKER_ID = "b9496a5f-6e7c-4d12-a345-567890abcdef"    # 세상학개론

# 실제 ID는 출력에서 확인된 것으로 수정
SESANG_SPEAKER_ID_REAL = "b9496a5f"  # 실제 첫 8자리

def update_channel_speaker(channel_id, speaker_id):
    """채널의 스피커 업데이트"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_channels"
    params = {"id": f"eq.{channel_id}"}
    data = {"speaker_id": speaker_id}
    
    response = requests.patch(url, headers=HEADERS, params=params, json=data)
    return response.status_code == 204, response.status_code, response.text

def get_speaker_by_partial_id(partial_id):
    """부분 ID로 스피커 찾기"""
    url = f"{SUPABASE_URL}/rest/v1/speakers"
    params = {
        "select": "id,name,aliases"
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        speakers = response.json()
        for speaker in speakers:
            if speaker['id'].startswith(partial_id):
                return speaker
    return None

def main():
    print("=== Fix Speaker Connection ===")
    
    # 세상학개론 스피커 찾기
    sesang_speaker = get_speaker_by_partial_id("b9496a5f")
    if sesang_speaker:
        print(f"Found Sesang speaker: {sesang_speaker['id']} - {sesang_speaker['name']}")
        
        # 세상학개론 채널에 세상학개론 스피커 연결
        success, status, text = update_channel_speaker(SESANG_CHANNEL_ID, sesang_speaker['id'])
        
        if success:
            print(f"SUCCESS: Connected Sesang channel to Sesang speaker")
        else:
            print(f"ERROR: Failed to connect - Status: {status}")
            print(f"Response: {text}")
    else:
        print("ERROR: Sesang speaker not found")
        
        # 대안: 이효석 스피커로 연결
        hyoseok_speaker = get_speaker_by_partial_id("b07d8758")
        if hyoseok_speaker:
            print(f"Using Hyoseok speaker as alternative: {hyoseok_speaker['id']} - {hyoseok_speaker['name']}")
            
            success, status, text = update_channel_speaker(SESANG_CHANNEL_ID, hyoseok_speaker['id'])
            
            if success:
                print(f"SUCCESS: Connected Sesang channel to Hyoseok speaker")
            else:
                print(f"ERROR: Failed to connect - Status: {status}")
        else:
            print("ERROR: No suitable speaker found")

if __name__ == "__main__":
    main()