#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase 시그널 데이터 변환 스크립트
- 3protv_signals.json과 3protv_v7_final.md 기반
- 코린이 아빠 데이터는 추후 추가 예정
"""
import json
import uuid
from datetime import datetime, timezone
import requests

# Supabase 설정
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"

# 시그널 타입 매핑 (8가지 고정)
SIGNAL_MAPPING = {
    'STRONG_BUY': 'STRONG_BUY',
    'BUY': 'BUY', 
    'POSITIVE': 'POSITIVE',
    'HOLD': 'HOLD',
    'NEUTRAL': 'NEUTRAL',
    'CONCERN': 'CONCERN',
    'SELL': 'SELL',
    'STRONG_SELL': 'STRONG_SELL'
}

def get_market_from_stock(stock_name):
    """종목명으로부터 마켓 추론"""
    kr_stocks = ['삼성전자', 'SK하이닉스', '신세계', '효성중공업', '솔브레인', '삼성전기', 'LG화학', '현대차', '현대건설', 'HD현대일렉트릭', 'NC소프트', '솔브레인']
    us_stocks = ['엔비디아', '서클']
    sectors = ['증권', '메모리 반도체', '반도체소부장', '비반도체섹터', '증권 섹터', '증권주전체']
    
    if stock_name in kr_stocks:
        return 'KR'
    elif stock_name in us_stocks:
        return 'US'  
    elif any(sector in stock_name for sector in sectors):
        return 'SECTOR'
    else:
        return 'UNKNOWN'

def get_ticker_from_stock(stock_name):
    """종목명으로부터 티커 추론"""
    ticker_map = {
        '삼성전자': '005930',
        'SK하이닉스': '000660',
        '엔비디아': 'NVDA',
        '현대차': '005380',
        '서클': 'CIRCLE',
        '코스피': 'KOSPI'
    }
    return ticker_map.get(stock_name, None)

def convert_3protv_signals():
    """3protv_signals.json을 Supabase 포맷으로 변환"""
    
    # JSON 파일 로드  
    try:
        with open('C:/Users/Mario/work/3protv_signals.json', 'r', encoding='utf-8') as f:
            signals_data = json.load(f)
    except FileNotFoundError:
        print("[오류] 3protv_signals.json 파일을 찾을 수 없습니다")
        return []
    
    converted_signals = []
    
    # 가상 채널/비디오 ID (실제 데이터가 없으므로)
    channel_id = str(uuid.uuid4())
    
    for i, signal in enumerate(signals_data):
        try:
            # 비디오 ID 생성
            video_id = str(uuid.uuid4())
            
            # 시그널 데이터 변환
            converted_signal = {
                'id': str(uuid.uuid4()),
                'video_id': video_id,
                'speaker': signal.get('speaker', 'Unknown'),
                'stock': signal.get('stock', ''),
                'ticker': get_ticker_from_stock(signal.get('stock', '')),
                'market': get_market_from_stock(signal.get('stock', '')),
                'mention_type': 'investment',  # 기본값
                'signal': SIGNAL_MAPPING.get(signal.get('signal'), 'NEUTRAL'),
                'confidence': 'high',  # 기본값
                'timestamp_in_video': signal.get('ts', ''),
                'key_quote': signal.get('quote', ''),
                'reasoning': f"3프로TV 분석 기반 - {signal.get('mention', '')}",
                'context': f"출처: 3프로TV, 분석일: 2026-02-27",
                'review_status': 'approved',  # 기본 승인
                'pipeline_version': '3protv_v7',
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            converted_signals.append(converted_signal)
            
        except Exception as e:
            print(f"[오류] 시그널 {i+1} 변환 실패: {e}")
            continue
    
    print(f"[완료] 3protv 시그널 {len(converted_signals)}개 변환 완료")
    return converted_signals

def create_mock_channel_video_data(signals):
    """Mock 채널과 비디오 데이터 생성"""
    
    # 채널 데이터
    channel_data = {
        'id': str(uuid.uuid4()),
        'channel_name': '삼프로TV',
        'channel_url': 'https://www.youtube.com/@3protv',
        'platform': 'youtube',
        'subscriber_count': 500000,  # 추정값
        'description': '삼성증권 프로 투자 전문 채널',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    # 비디오 데이터 (각 시그널별 가상 비디오)
    videos = []
    unique_speakers = list(set(signal['speaker'] for signal in signals))
    
    for i, speaker in enumerate(unique_speakers):
        video_data = {
            'id': str(uuid.uuid4()),
            'channel_id': channel_data['id'],
            'video_id': f'3protv_mock_{i+1}',
            'title': f'{speaker} 투자 전략 분석',
            'published_at': datetime.now(timezone.utc).isoformat(),
            'duration_seconds': 600,  # 10분 가정
            'has_subtitle': True,
            'analyzed_at': datetime.now(timezone.utc).isoformat(),
            'pipeline_version': '3protv_v7',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        videos.append(video_data)
    
    return channel_data, videos

def insert_to_supabase_rest(table, data):
    """Supabase REST API로 데이터 삽입"""
    
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
            print(f"[성공] {table} 테이블에 {len(data) if isinstance(data, list) else 1}개 레코드 삽입 성공")
            return True
        else:
            print(f"[실패] {table} 테이블 삽입 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"[오류] {table} 테이블 삽입 중 오류: {e}")
        return False

def generate_insert_sql(signals, channel_data, videos):
    """SQL INSERT 문 생성"""
    
    sql_statements = []
    
    # 채널 INSERT
    sql_statements.append(f"""
-- 채널 데이터 삽입
INSERT INTO public.influencer_channels (id, channel_name, channel_url, platform, subscriber_count, description, created_at)
VALUES ('{channel_data['id']}', '{channel_data['channel_name']}', '{channel_data['channel_url']}', 
        '{channel_data['platform']}', {channel_data['subscriber_count']}, '{channel_data['description']}', 
        '{channel_data['created_at']}');
""")
    
    # 비디오 INSERT  
    for video in videos:
        sql_statements.append(f"""
INSERT INTO public.influencer_videos (id, channel_id, video_id, title, published_at, duration_seconds, has_subtitle, analyzed_at, pipeline_version, created_at)
VALUES ('{video['id']}', '{video['channel_id']}', '{video['video_id']}', '{video['title']}', 
        '{video['published_at']}', {video['duration_seconds']}, {video['has_subtitle']}, 
        '{video['analyzed_at']}', '{video['pipeline_version']}', '{video['created_at']}');
""")
    
    # 시그널 INSERT
    for signal in signals:
        # SQL 인젝션 방지를 위해 작은따옴표 이스케이프
        quote_escaped = signal['key_quote'].replace("'", "''")
        reasoning_escaped = signal['reasoning'].replace("'", "''")
        context_escaped = signal['context'].replace("'", "''")
        
        sql_statements.append(f"""
INSERT INTO public.influencer_signals (id, video_id, speaker, stock, ticker, market, mention_type, signal, confidence, timestamp_in_video, key_quote, reasoning, context, review_status, pipeline_version, created_at)
VALUES ('{signal['id']}', '{signal['video_id']}', '{signal['speaker']}', '{signal['stock']}', 
        '{signal['ticker'] or 'NULL'}', '{signal['market']}', '{signal['mention_type']}', '{signal['signal']}', 
        '{signal['confidence']}', '{signal['timestamp_in_video']}', '{quote_escaped}', 
        '{reasoning_escaped}', '{context_escaped}', '{signal['review_status']}', 
        '{signal['pipeline_version']}', '{signal['created_at']}');
""")
    
    return '\n'.join(sql_statements)

def main():
    print("[시작] Supabase 시그널 데이터 변환 시작")
    
    # 1. 3protv 시그널 변환
    signals = convert_3protv_signals()
    if not signals:
        print("[오류] 변환할 시그널 데이터가 없습니다")
        return
    
    # 2. Mock 채널/비디오 데이터 생성
    channel_data, videos = create_mock_channel_video_data(signals)
    
    # 3. SQL 파일 생성
    sql_content = generate_insert_sql(signals, channel_data, videos)
    
    with open('C:/Users/Mario/work/invest-sns/supabase/3protv_signals_insert.sql', 'w', encoding='utf-8') as f:
        f.write("-- 삼프로TV 시그널 데이터 INSERT 문\n")
        f.write("-- 생성일: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
        f.write(sql_content)
    
    print(f"[완료] SQL INSERT 파일 생성 완료: 3protv_signals_insert.sql")
    print(f"   - 채널 1개, 비디오 {len(videos)}개, 시그널 {len(signals)}개")
    
    # 4. REST API 삽입 시도 (선택적)
    try_rest_api = input("\n[확인] Supabase REST API로 직접 삽입을 시도하시겠습니까? (y/n): ").lower().strip() == 'y'
    
    if try_rest_api:
        print("\n[시도] REST API 삽입 시도...")
        
        # 채널 삽입
        if insert_to_supabase_rest('influencer_channels', channel_data):
            # 비디오 삽입
            if insert_to_supabase_rest('influencer_videos', videos):
                # 시그널 삽입
                insert_to_supabase_rest('influencer_signals', signals)
    
    print("\n[완료] 변환 작업 완료!")
    print("[다음 단계]")
    print("1. Supabase 대시보드 SQL Editor에서 influencer-migration.sql 실행 (테이블 생성)")
    print("2. 3protv_signals_insert.sql 실행 (데이터 삽입)")
    print("3. 코린이 아빠 데이터 추가")

if __name__ == "__main__":
    main()