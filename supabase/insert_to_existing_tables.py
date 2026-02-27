#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 Supabase 테이블에 인플루언서 데이터 삽입
"""
import json
import uuid
import requests
from datetime import datetime, timezone

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRirixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"

def insert_to_supabase(table, data):
    """Supabase에 데이터 삽입"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 201:
            print(f"[성공] {table}에 데이터 삽입 완료")
            return True
        else:
            print(f"[실패] {table} 삽입 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"[오류] {table} 삽입 중 에러: {e}")
        return False

def insert_influencer_data():
    """삼프로TV 인플루언서 데이터 삽입"""
    
    # 기존 influencers 테이블 구조에 맞춘 데이터
    influencer_data = {
        'profile_id': 'samprotv_channel',
        'platform': 'youtube',
        'platform_url': 'https://www.youtube.com/@3protv',
        'follower_count': 500000,
        'total_calls': 42,  # 3protv 시그널 수
        'successful_calls': 35,  # 임시값
        'win_rate': 83.3,  # 임시값 (35/42)
        'avg_return': 15.7,  # 임시값
        'style': '삼성증권 프로 분석',
        'main_sectors': '반도체,증권,전기차',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat()
    }
    
    return insert_to_supabase('influencers', influencer_data)

def load_3protv_signals():
    """3protv 시그널 데이터 로드"""
    try:
        with open('C:/Users/Mario/work/3protv_signals.json', 'r', encoding='utf-8') as f:
            signals_data = json.load(f)
        print(f"[로드] 3protv 시그널 {len(signals_data)}개 로드 완료")
        return signals_data
    except FileNotFoundError:
        print("[오류] 3protv_signals.json 파일을 찾을 수 없습니다")
        return []

def create_posts_from_signals(signals):
    """시그널 데이터를 posts 테이블 형태로 변환"""
    
    posts = []
    
    for i, signal in enumerate(signals[:5]):  # 처음 5개만 테스트
        post_data = {
            'id': str(uuid.uuid4()),
            'user_id': 'samprotv_channel',
            'title': f"{signal.get('speaker', 'Unknown')}의 {signal.get('stock', '')} 분석",
            'content': f"시그널: {signal.get('signal', 'NEUTRAL')}\n발언: {signal.get('quote', '')}\n타임스탬프: {signal.get('ts', '')}",
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        posts.append(post_data)
    
    return posts

def main():
    print("[시작] 기존 테이블에 3protv 데이터 삽입")
    
    # 1. 인플루언서 데이터 삽입
    if insert_influencer_data():
        print("[완료] 삼프로TV 인플루언서 데이터 삽입 완료")
    
    # 2. 시그널 데이터 로드
    signals = load_3protv_signals()
    if not signals:
        print("[중단] 시그널 데이터가 없어서 중단합니다")
        return
    
    # 3. 시그널을 posts로 변환하여 삽입
    posts = create_posts_from_signals(signals)
    
    for i, post in enumerate(posts):
        if insert_to_supabase('posts', post):
            print(f"[완료] 포스트 {i+1}/{len(posts)} 삽입 완료")
        else:
            print(f"[실패] 포스트 {i+1} 삽입 실패")
    
    print(f"\n[완료] 작업 완료")
    print(f"- 인플루언서: 1명 (삼프로TV)")
    print(f"- 포스트: {len(posts)}개")
    print(f"- 원본 시그널: {len(signals)}개")

if __name__ == "__main__":
    main()