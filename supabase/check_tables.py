#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase 테이블 존재 여부 확인
"""
import requests

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"

def check_table_exists(table_name):
    """테이블 존재 여부 확인"""
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?limit=1"
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"[존재] {table_name} 테이블이 존재합니다")
            return True
        elif response.status_code == 404:
            print(f"[없음] {table_name} 테이블이 없습니다")
            return False
        else:
            print(f"[오류] {table_name} 확인 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
    except Exception as e:
        print(f"[오류] {table_name} 확인 중 에러: {e}")
        return False

def main():
    print("[시작] Supabase 테이블 확인")
    
    tables = ['influencer_channels', 'influencer_videos', 'influencer_signals']
    
    for table in tables:
        check_table_exists(table)
        print()

if __name__ == "__main__":
    main()