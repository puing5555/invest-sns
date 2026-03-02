#!/usr/bin/env python3
"""
세상학개론 시그널 93개의 key_quote, reasoning 현재 상태 확인
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import json

load_dotenv('.env.local')

# Supabase 설정
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase: Client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

# 세상학개론 speaker_id
SESANG_SPEAKER_ID = "b9496a5f-06fa-47eb-bc2d-47060b095534"

def main():
    print("🔍 세상학개론 시그널 데이터 조회 중...")
    
    # 세상학개론 시그널 조회
    response = supabase.table('investment_signals').select('*').eq('speaker_id', SESANG_SPEAKER_ID).execute()
    
    signals = response.data
    print(f"📊 총 {len(signals)}개 시그널 발견")
    
    # key_quote, reasoning 길이 통계
    long_quotes = []
    short_reasoning = []
    
    for signal in signals:
        quote_len = len(signal.get('key_quote', ''))
        reasoning_len = len(signal.get('reasoning', ''))
        
        # 너무 긴 key_quote (100자 이상)
        if quote_len > 100:
            long_quotes.append({
                'id': signal['id'],
                'stock': signal['stock'],
                'signal': signal['signal'],
                'quote_len': quote_len,
                'key_quote': signal['key_quote'][:200] + '...' if len(signal['key_quote']) > 200 else signal['key_quote']
            })
        
        # 너무 짧은 reasoning (50자 이하)
        if reasoning_len < 50:
            short_reasoning.append({
                'id': signal['id'],
                'stock': signal['stock'],
                'signal': signal['signal'],
                'reasoning_len': reasoning_len,
                'reasoning': signal['reasoning']
            })
    
    print(f"⚠️ key_quote 100자 초과: {len(long_quotes)}개")
    print(f"⚠️ reasoning 50자 미만: {len(short_reasoning)}개")
    
    # 샘플 출력
    if long_quotes:
        print("\n🔍 긴 key_quote 샘플:")
        for i, item in enumerate(long_quotes[:3]):
            print(f"{i+1}. {item['stock']} ({item['signal']}) - {item['quote_len']}자")
            print(f"   {item['key_quote']}")
    
    if short_reasoning:
        print("\n🔍 짧은 reasoning 샘플:")
        for i, item in enumerate(short_reasoning[:3]):
            print(f"{i+1}. {item['stock']} ({item['signal']}) - {item['reasoning_len']}자")
            print(f"   {item['reasoning']}")
    
    # 결과 저장
    result = {
        'total_signals': len(signals),
        'long_quotes': len(long_quotes),
        'short_reasoning': len(short_reasoning),
        'long_quote_samples': long_quotes[:5],
        'short_reasoning_samples': short_reasoning[:5],
        'all_signals': [{'id': s['id'], 'stock': s['stock'], 'signal': s['signal'], 'video_id': s.get('video_id')} for s in signals]
    }
    
    with open('sesang_signal_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 분석 결과를 sesang_signal_analysis.json에 저장했습니다.")

if __name__ == "__main__":
    main()