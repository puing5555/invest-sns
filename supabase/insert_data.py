#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase 데이터 삽입
"""
import json
import uuid
import requests
from datetime import datetime, timezone

SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"

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
            print(f"[성공] {table}에 {len(data) if isinstance(data, list) else 1}개 레코드 삽입")
            return True
        else:
            print(f"[실패] {table} 삽입 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"[오류] {table} 삽입 중 에러: {e}")
        return False

def main():
    print("[시작] 3protv 데이터 삽입")
    
    # 1. 채널 데이터 삽입
    channel_data = {
        'id': str(uuid.uuid4()),
        'channel_name': '삼프로TV',
        'channel_url': 'https://www.youtube.com/@3protv',
        'platform': 'youtube',
        'subscriber_count': 500000,
        'description': '삼성증권 프로 투자 전문 채널',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    if not insert_to_supabase('influencer_channels', channel_data):
        print("[중단] 채널 삽입 실패로 작업을 중단합니다")
        return
    
    channel_id = channel_data['id']
    
    # 2. 샘플 비디오 데이터 삽입
    video_data = {
        'id': str(uuid.uuid4()),
        'channel_id': channel_id,
        'video_id': '3protv_test_video',
        'title': '삼프로TV 테스트 비디오',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'duration_seconds': 600,
        'has_subtitle': True,
        'analyzed_at': datetime.now(timezone.utc).isoformat(),
        'pipeline_version': '3protv_v7',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    if not insert_to_supabase('influencer_videos', video_data):
        print("[중단] 비디오 삽입 실패로 작업을 중단합니다")
        return
        
    video_id = video_data['id']
    
    # 3. 샘플 시그널 데이터 삽입
    sample_signals = [
        {
            'id': str(uuid.uuid4()),
            'video_id': video_id,
            'speaker': '배재원',
            'stock': '삼성전자',
            'ticker': '005930',
            'market': 'KR',
            'mention_type': 'investment',
            'signal': 'STRONG_BUY',
            'confidence': 'high',
            'timestamp_in_video': '06:10',
            'key_quote': '영업이익 추정치가 계속 상향되고 있는데 매도할 이유가 없다. 지금이라도 들어가야 된다',
            'reasoning': '삼프로TV 분석 기반 - 결론',
            'context': '출처: 삼프로TV, 분석일: 2026-02-27',
            'review_status': 'approved',
            'pipeline_version': '3protv_v7',
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'video_id': video_id,
            'speaker': '고연수',
            'stock': '증권주전체',
            'ticker': None,
            'market': 'SECTOR',
            'mention_type': 'investment',
            'signal': 'STRONG_BUY',
            'confidence': 'high',
            'timestamp_in_video': '06:12',
            'key_quote': '증권주는 거의 다 편하게 가져가도 된다. 무조건 지금보다는 수익률이 더 나을 수 있다',
            'reasoning': '삼프로TV 분석 기반 - 결론',
            'context': '출처: 삼프로TV, 분석일: 2026-02-27',
            'review_status': 'approved',
            'pipeline_version': '3protv_v7',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
    ]
    
    for signal in sample_signals:
        if not insert_to_supabase('influencer_signals', signal):
            print(f"[경고] 시그널 삽입 실패: {signal['stock']}")
    
    print("[완료] 데이터 삽입 작업 완료")
    print(f"- 채널: {channel_data['channel_name']}")
    print(f"- 비디오: {video_data['title']}")
    print(f"- 시그널: {len(sample_signals)}개")

if __name__ == "__main__":
    main()