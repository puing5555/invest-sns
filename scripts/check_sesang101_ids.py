#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
세상학개론 채널 ID와 스피커 ID 확인
"""

import requests

# Supabase 설정
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

def check_channels():
    """세상학개론 채널 확인"""
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/influencer_channels?channel_name=like.*세상학개론*",
            headers=headers
        )
        
        if response.status_code == 200:
            channels = response.json()
            print(f"[채널] 세상학개론 관련 채널: {len(channels)}개")
            for channel in channels:
                print(f"  - ID: {channel['id']}, 이름: {channel['channel_name']}")
            return channels
        else:
            print(f"[ERR] 채널 조회 실패: {response.status_code}")
            return []
    
    except Exception as e:
        print(f"[ERR] 채널 확인 실패: {e}")
        return []

def check_speakers():
    """세상학개론 스피커 확인"""
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/speakers?name=like.*세상*",
            headers=headers
        )
        
        if response.status_code == 200:
            speakers = response.json()
            print(f"\n[스피커] 세상 관련 스피커: {len(speakers)}개")
            for speaker in speakers:
                print(f"  - ID: {speaker['id']}, 이름: {speaker['name']}")
            return speakers
        else:
            print(f"[ERR] 스피커 조회 실패: {response.status_code}")
            return []
    
    except Exception as e:
        print(f"[ERR] 스피커 확인 실패: {e}")
        return []

def create_channel_if_needed():
    """세상학개론 채널이 없으면 생성"""
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # 먼저 존재하는지 확인
    channels = check_channels()
    if channels:
        return channels[0]['id']
    
    # 채널 생성
    try:
        channel_data = {
            "channel_name": "세상학개론",
            "channel_handle": "sesang101",
            "channel_url": "https://www.youtube.com/@sesang101",
            "platform": "youtube",
            "subscriber_count": 100000,
            "description": "경제/투자 교육 채널"
        }
        
        headers['Prefer'] = 'return=representation'
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/influencer_channels",
            headers=headers,
            json=channel_data
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            if result:
                channel_id = result[0]['id']
                print(f"[생성] 세상학개론 채널 생성: ID {channel_id}")
                return channel_id
            else:
                print("[ERR] 채널 생성 응답이 비어있음")
                return None
        else:
            print(f"[ERR] 채널 생성 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return None
    
    except Exception as e:
        print(f"[ERR] 채널 생성 실패: {e}")
        return None

def create_speaker_if_needed():
    """세상학개론 스피커가 없으면 생성"""
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # 먼저 존재하는지 확인
    speakers = check_speakers()
    for speaker in speakers:
        if '세상학개론' in speaker['name']:
            return speaker['id']
    
    # 스피커 생성
    try:
        speaker_data = {
            "name": "세상학개론",
            "bio": "경제/투자 교육 유튜버",
            "aliases": ["세상학개론", "세상학"]
        }
        
        headers['Prefer'] = 'return=representation'
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/speakers",
            headers=headers,
            json=speaker_data
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            if result:
                speaker_id = result[0]['id']
                print(f"[생성] 세상학개론 스피커 생성: ID {speaker_id}")
                return speaker_id
            else:
                print("[ERR] 스피커 생성 응답이 비어있음")
                return None
        else:
            print(f"[ERR] 스피커 생성 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return None
    
    except Exception as e:
        print(f"[ERR] 스피커 생성 실패: {e}")
        return None

def main():
    print("세상학개론 ID 확인 및 생성\n")
    
    # 1. 기존 채널/스피커 확인
    check_channels()
    check_speakers()
    
    # 2. 필요하면 생성
    channel_id = create_channel_if_needed()
    speaker_id = create_speaker_if_needed()
    
    print(f"\n[결과]")
    print(f"채널 ID: {channel_id}")
    print(f"스피커 ID: {speaker_id}")

if __name__ == "__main__":
    main()