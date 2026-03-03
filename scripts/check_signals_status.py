#!/usr/bin/env python3
"""
현재 Supabase DB의 시그널 상태 확인
"""

import os
import re
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

def extract_video_id_from_url(video_url: str) -> str:
    """YouTube URL에서 video_id 추출"""
    patterns = [
        r'v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'embed/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, video_url)
        if match:
            return match.group(1)
    return ""

def main():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # 모든 시그널 조회
        response = supabase.table('influencer_signals') \
            .select('id,video_url,key_quote,timestamp_seconds,stock,signal') \
            .execute()
        
        if not response.data:
            print("❌ 시그널 조회 실패")
            return
        
        signals = response.data
        total_count = len(signals)
        
        print(f"\n{'='*80}")
        print(f"📊 Supabase DB 시그널 상태 분석")
        print(f"{'='*80}")
        print(f"📊 총 시그널 수: {total_count}개\n")
        
        # 타임스탬프 분석
        zero_timestamps = []
        low_timestamps = []  # 60초 미만
        normal_timestamps = []
        
        for signal in signals:
            ts = signal['timestamp_seconds']
            if ts == 0:
                zero_timestamps.append(signal)
            elif ts < 60:
                low_timestamps.append(signal)
            else:
                normal_timestamps.append(signal)
        
        print(f"⏰ 타임스탬프 분석:")
        print(f"  - 0초 (시작부분): {len(zero_timestamps)}개")
        print(f"  - 60초 미만: {len(low_timestamps)}개")
        print(f"  - 60초 이상: {len(normal_timestamps)}개\n")
        
        # 0초 타임스탬프 상세 분석
        if zero_timestamps:
            print(f"🔍 0초 타임스탬프 시그널 상세 분석 (처음 10개):")
            for i, signal in enumerate(zero_timestamps[:10]):
                video_id = extract_video_id_from_url(signal['video_url'])
                print(f"  {i+1:2d}. ID:{signal['id']} | {signal['stock']} | {signal['signal']} | {video_id}")
                print(f"      Quote: {signal['key_quote'][:80]}...")
                print(f"      URL: {signal['video_url']}")
                print()
        
        # 종목별 분석
        stock_counts = {}
        for signal in signals:
            stock = signal['stock']
            stock_counts[stock] = stock_counts.get(stock, 0) + 1
        
        print(f"📈 종목별 시그널 수 (상위 10개):")
        sorted_stocks = sorted(stock_counts.items(), key=lambda x: x[1], reverse=True)
        for i, (stock, count) in enumerate(sorted_stocks[:10]):
            print(f"  {i+1:2d}. {stock}: {count}개")
        
        print(f"\n💡 타임스탬프 교정이 필요한 시그널: 약 {len(zero_timestamps) + len(low_timestamps)}개")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == '__main__':
    main()