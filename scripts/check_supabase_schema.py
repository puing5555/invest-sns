#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase 테이블 스키마 확인 스크립트
"""

import requests
import json

# Supabase 설정
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

def check_table_schema(table_name):
    """테이블 스키마 확인"""
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        # 테이블에서 1개 레코드만 가져와서 컬럼 확인
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table_name}?limit=1",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data:
                columns = list(data[0].keys())
                print(f"\n[{table_name}] 테이블 컬럼:")
                for col in sorted(columns):
                    print(f"  - {col}")
                return columns
            else:
                print(f"[{table_name}] 테이블이 비어있음")
                return []
        else:
            print(f"[ERR] {table_name} 조회 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return []
    
    except Exception as e:
        print(f"[ERR] {table_name} 스키마 확인 실패: {e}")
        return []

def main():
    print("Supabase 테이블 스키마 확인\n")
    
    # 주요 테이블들 확인
    tables = [
        'influencer_signals',
        'influencer_channels',
        'influencer_videos',
        'speakers'
    ]
    
    for table in tables:
        check_table_schema(table)

if __name__ == "__main__":
    main()