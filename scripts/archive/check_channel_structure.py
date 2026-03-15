#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
채널 테이블 구조 상세 확인
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

def main():
    print("=== Channel Table Structure Analysis ===")
    
    # 채널 데이터 전체 구조 확인
    url = f"{SUPABASE_URL}/rest/v1/influencer_channels"
    params = {
        "select": "*",
        "limit": 1
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            print("Channel table columns:")
            channel = data[0]
            for key, value in channel.items():
                print(f"  {key}: {type(value).__name__}")
            
            print(f"\nFull sample record:")
            print(json.dumps(channel, indent=2, ensure_ascii=False))
        else:
            print("No channel data found")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    print("\n=== Speaker Relationship Check ===")
    
    # 다른 테이블에서 스피커 관계 찾기
    tables_to_check = [
        "influencer_videos",
        "signals"
    ]
    
    for table_name in tables_to_check:
        try:
            url = f"{SUPABASE_URL}/rest/v1/{table_name}"
            params = {"limit": 1, "select": "*"}
            
            response = requests.get(url, headers=HEADERS, params=params)
            if response.status_code == 200:
                data = response.json()
                if data:
                    print(f"\n{table_name} table columns:")
                    record = data[0]
                    for key, value in record.items():
                        print(f"  {key}: {type(value).__name__}")
        except Exception as e:
            print(f"Error checking {table_name}: {e}")

if __name__ == "__main__":
    main()