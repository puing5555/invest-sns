#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase 기존 테이블 목록 확인
"""
import requests

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"

def check_existing_tables():
    """기존 테이블들 확인"""
    
    # 알려진 테이블들 확인
    known_tables = [
        'influencers', 'profiles', 'posts', 'disclosures', 
        'disclosure_analysis', 'crawl_logs', 'user_settings', 
        'points', 'disclosure_votes', 'trade_reviews', 
        'analyst_reports', 'influencer_sector_stats',
        'influencer_calls'  # 힌트에서 나온 테이블
    ]
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("[확인] 기존 테이블 목록:")
    print("-" * 50)
    
    for table in known_tables:
        url = f"{SUPABASE_URL}/rest/v1/{table}?limit=1"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                print(f"✓ {table} - 존재함")
            else:
                print(f"✗ {table} - 없음 ({response.status_code})")
        except Exception as e:
            print(f"? {table} - 오류: {e}")

def check_influencers_table():
    """influencers 테이블 구조 확인"""
    url = f"{SUPABASE_URL}/rest/v1/influencers?limit=5"
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"\n[구조] influencers 테이블 샘플 데이터:")
            print("-" * 50)
            if data:
                print(f"컬럼들: {list(data[0].keys())}")
                print(f"샘플 레코드 수: {len(data)}")
                for i, record in enumerate(data[:2]):
                    print(f"\n레코드 {i+1}:")
                    for key, value in record.items():
                        print(f"  {key}: {value}")
            else:
                print("데이터가 없습니다")
        else:
            print(f"influencers 테이블 확인 실패: {response.status_code}")
    except Exception as e:
        print(f"influencers 테이블 확인 오류: {e}")

def main():
    check_existing_tables()
    check_influencers_table()

if __name__ == "__main__":
    main()