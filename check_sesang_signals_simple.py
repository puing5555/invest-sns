#!/usr/bin/env python3
"""
세상학개론 시그널 93개의 key_quote, reasoning 현재 상태 확인 (requests 사용)
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('.env.local')

# Supabase 설정
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# 세상학개론 speaker_id
SESANG_SPEAKER_ID = "b9496a5f-06fa-47eb-bc2d-47060b095534"

def main():
    print("Checking Sesang101 signals...")
    
    # Supabase REST API 호출
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
    headers = {
        'apikey': SERVICE_ROLE_KEY,
        'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json'
    }
    
    params = {'speaker_id': f'eq.{SESANG_SPEAKER_ID}'}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"API call failed: {response.status_code}")
        print(response.text)
        return
    
    signals = response.json()
    print(f"Total {len(signals)} signals found")
    
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
                'video_id': signal.get('video_id'),
                'key_quote': signal['key_quote'][:200] + '...' if len(signal['key_quote']) > 200 else signal['key_quote']
            })
        
        # 너무 짧은 reasoning (50자 이하)
        if reasoning_len < 50:
            short_reasoning.append({
                'id': signal['id'],
                'stock': signal['stock'],
                'signal': signal['signal'],
                'reasoning_len': reasoning_len,
                'video_id': signal.get('video_id'),
                'reasoning': signal['reasoning']
            })
    
    print(f"Long quotes (>100 chars): {len(long_quotes)} signals")
    print(f"Short reasoning (<50 chars): {len(short_reasoning)} signals")
    
    # 샘플 출력
    if long_quotes:
        print("\nLong key_quote samples:")
        for i, item in enumerate(long_quotes[:3]):
            print(f"{i+1}. {item['stock']} ({item['signal']}) - {item['quote_len']} chars")
            print(f"   {item['key_quote']}")
    
    if short_reasoning:
        print("\nShort reasoning samples:")
        for i, item in enumerate(short_reasoning[:3]):
            print(f"{i+1}. {item['stock']} ({item['signal']}) - {item['reasoning_len']} chars")
            print(f"   {item['reasoning']}")
    
    # 결과 저장
    result = {
        'total_signals': len(signals),
        'long_quotes': len(long_quotes),
        'short_reasoning': len(short_reasoning),
        'long_quote_samples': long_quotes[:10],
        'short_reasoning_samples': short_reasoning[:10],
        'need_fix_signals': [
            {'id': s['id'], 'stock': s['stock'], 'signal': s['signal'], 'video_id': s.get('video_id')} 
            for s in signals 
            if len(s.get('key_quote', '')) > 100 or len(s.get('reasoning', '')) < 50
        ]
    }
    
    with open('sesang_signal_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nAnalysis results saved to sesang_signal_analysis.json")
    print(f"Signals need fixing: {len(result['need_fix_signals'])}")

if __name__ == "__main__":
    main()