#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DB 구조 확인
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

def check_table(table_name, limit=5):
    """테이블 확인"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table_name}"
        params = {"limit": limit}
        
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nTable: {table_name}")
            print(f"Status: OK (found {len(data)} records)")
            if data:
                print("Sample record structure:")
                print(json.dumps(data[0], indent=2))
        else:
            print(f"\nTable: {table_name}")
            print(f"Status: ERROR {response.status_code}")
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"\nTable: {table_name}")
        print(f"Status: EXCEPTION - {e}")

def main():
    print("=== Database Structure Check ===")
    
    # 주요 테이블들 확인
    tables_to_check = [
        "influencer_channels",
        "influencer_videos", 
        "speakers",
        "signals",
        "users"
    ]
    
    for table in tables_to_check:
        check_table(table)
    
    # 채널 정보 자세히 확인
    print("\n=== Sesang Channel Details ===")
    try:
        url = f"{SUPABASE_URL}/rest/v1/influencer_channels"
        params = {
            "select": "*",
            "id": "eq.d68f8efd-64c8-4c07-9d34-e98c2954f4e1"
        }
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                print("Sesang channel details:")
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
            else:
                print("Sesang channel not found")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()