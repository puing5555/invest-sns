#!/usr/bin/env python3
"""
signal_prices.json 업데이트 및 public/ 동기화
"""
import os
import json
import shutil
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

SUPABASE_HEADERS = {
    'apikey': SERVICE_ROLE_KEY,
    'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
    'Content-Type': 'application/json'
}

def get_all_signals():
    """모든 시그널 조회"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
    params = {
        'select': 'id,stock,signal,speaker_id,created_at,key_quote,reasoning',
        'order': 'created_at.desc'
    }
    
    response = requests.get(url, headers=SUPABASE_HEADERS, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting signals: {response.status_code}")
        return []

def get_speaker_info():
    """스피커 정보 조회"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_speakers"
    params = {'select': 'id,name,profile_image,channel'}
    
    response = requests.get(url, headers=SUPABASE_HEADERS, params=params)
    
    if response.status_code == 200:
        speakers = response.json()
        return {speaker['id']: speaker for speaker in speakers}
    else:
        print(f"Error getting speakers: {response.status_code}")
        return {}

def group_signals_by_stock(signals, speakers):
    """종목별로 시그널 그룹화"""
    stock_signals = {}
    
    for signal in signals:
        stock = signal['stock']
        speaker_id = signal['speaker_id']
        speaker = speakers.get(speaker_id, {})
        
        if stock not in stock_signals:
            stock_signals[stock] = {
                'stock': stock,
                'signals': [],
                'latest_signal': None,
                'signal_count': 0,
                'speakers': set()
            }
        
        # 시그널 정보 추가
        signal_data = {
            'id': signal['id'],
            'signal': signal['signal'],
            'speaker_name': speaker.get('name', 'Unknown'),
            'speaker_id': speaker_id,
            'created_at': signal['created_at'],
            'key_quote': signal.get('key_quote', ''),
            'reasoning': signal.get('reasoning', '')
        }
        
        stock_signals[stock]['signals'].append(signal_data)
        stock_signals[stock]['signal_count'] += 1
        stock_signals[stock]['speakers'].add(speaker.get('name', 'Unknown'))
        
        # 최신 시그널 업데이트
        if (stock_signals[stock]['latest_signal'] is None or 
            signal['created_at'] > stock_signals[stock]['latest_signal']['created_at']):
            stock_signals[stock]['latest_signal'] = signal_data
    
    # set을 list로 변환
    for stock_data in stock_signals.values():
        stock_data['speakers'] = list(stock_data['speakers'])
    
    return stock_signals

def create_signal_prices_json(stock_signals):
    """signal_prices.json 형태로 변환"""
    
    signal_prices = {
        'updated_at': datetime.now().isoformat(),
        'total_stocks': len(stock_signals),
        'total_signals': sum(data['signal_count'] for data in stock_signals.values()),
        'stocks': []
    }
    
    # 종목별 데이터 생성
    for stock, data in stock_signals.items():
        stock_data = {
            'stock': stock,
            'signal_count': data['signal_count'],
            'latest_signal': data['latest_signal']['signal'] if data['latest_signal'] else None,
            'latest_speaker': data['latest_signal']['speaker_name'] if data['latest_signal'] else None,
            'latest_date': data['latest_signal']['created_at'] if data['latest_signal'] else None,
            'speakers': data['speakers'],
            'signals': [
                {
                    'signal': s['signal'],
                    'speaker': s['speaker_name'],
                    'date': s['created_at'],
                    'key_quote': s['key_quote'][:100] + '...' if len(s['key_quote']) > 100 else s['key_quote']
                }
                for s in sorted(data['signals'], key=lambda x: x['created_at'], reverse=True)[:5]  # 최신 5개만
            ]
        }
        
        signal_prices['stocks'].append(stock_data)
    
    # 시그널 수 기준으로 정렬
    signal_prices['stocks'].sort(key=lambda x: x['signal_count'], reverse=True)
    
    return signal_prices

def save_and_sync_files(signal_prices):
    """파일 저장 및 public/ 동기화"""
    
    # data/ 디렉토리에 저장
    os.makedirs('data', exist_ok=True)
    data_path = 'data/signal_prices.json'
    
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(signal_prices, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved to {data_path}")
    
    # public/ 디렉토리에 복사
    public_path = 'public/signal_prices.json'
    shutil.copy2(data_path, public_path)
    
    print(f"✅ Synced to {public_path}")
    
    return data_path, public_path

def main():
    print("📊 Updating signal_prices.json...")
    
    # 데이터 조회
    print("  Fetching signals...")
    signals = get_all_signals()
    
    print("  Fetching speakers...")
    speakers = get_speaker_info()
    
    print(f"  Found {len(signals)} signals, {len(speakers)} speakers")
    
    # 종목별 그룹화
    print("  Grouping signals by stock...")
    stock_signals = group_signals_by_stock(signals, speakers)
    
    # JSON 형태로 변환
    print("  Creating signal_prices.json...")
    signal_prices = create_signal_prices_json(stock_signals)
    
    # 파일 저장 및 동기화
    print("  Saving and syncing files...")
    data_path, public_path = save_and_sync_files(signal_prices)
    
    print(f"\n🎉 signal_prices.json updated!")
    print(f"  Total stocks: {signal_prices['total_stocks']}")
    print(f"  Total signals: {signal_prices['total_signals']}")
    print(f"  Updated at: {signal_prices['updated_at']}")
    print(f"  Files: {data_path}, {public_path}")

if __name__ == "__main__":
    main()