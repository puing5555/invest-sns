#!/usr/bin/env python3
"""
작업 2: 잘못된 종목 정리
- "라울 팔" (사람), "피델리티" (회사), "그레이스케일 비트코인 투자 신탁" 등은 종목이 아님
- 이런 항목은 삭제하거나 올바른 종목으로 수정
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
SESANG_SPEAKER_ID = "b9496a5f-06fa-47eb-bc2d-47060b095534"

SUPABASE_HEADERS = {
    'apikey': SERVICE_ROLE_KEY,
    'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
    'Content-Type': 'application/json'
}

# 잘못된 종목 목록 (사람, 회사, 기관 등 - 투자 대상이 아님)
WRONG_STOCKS = [
    # 사람
    "라울 팔", "라울팔", "Raoul Pal",
    # 회사/기관
    "피델리티", "Fidelity", 
    "그레이스케일", "Grayscale",
    "그레이스케일 비트코인 투자 신탁", 
    "블랙록", "BlackRock",
    "마이크로스트래티지", "MicroStrategy", "MSTR",  # 이건 애매하지만 회사명이라서
    # 기타
    "연준", "Fed", "연방준비제도",
    "SEC", "증권거래위원회",
    "ETF", "상장지수펀드"
]

# 올바른 종목으로 매핑 (회사 -> 주식 티커)
STOCK_MAPPING = {
    "마이크로스트래티지": "MSTR",
    "MicroStrategy": "MSTR",
    "블랙록": "BLK", 
    "BlackRock": "BLK",
    "피델리티": None,  # 삭제 대상
    "Fidelity": None,  # 삭제 대상
    "그레이스케일": "GBTC",  # 그레이스케일 비트코인 트러스트
    "Grayscale": "GBTC",
    "그레이스케일 비트코인 투자 신탁": "GBTC"
}

def get_sesang_signals():
    """세상학개론 시그널 모두 조회"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
    params = {'speaker_id': f'eq.{SESANG_SPEAKER_ID}', 'select': 'id,stock,signal'}
    
    response = requests.get(url, headers=SUPABASE_HEADERS, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting signals: {response.status_code}")
        return []

def update_stock_name(signal_id, new_stock):
    """시그널의 종목명 수정"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
    params = {'id': f'eq.{signal_id}'}
    
    data = {'stock': new_stock}
    
    response = requests.patch(url, headers=SUPABASE_HEADERS, params=params, json=data)
    return response.status_code in [200, 204]

def delete_signal(signal_id):
    """시그널 삭제"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
    params = {'id': f'eq.{signal_id}'}
    
    response = requests.delete(url, headers=SUPABASE_HEADERS, params=params)
    return response.status_code in [200, 204]

def main():
    print("🧹 Cleaning wrong stocks from Sesang101 signals...")
    
    # 모든 세상학개론 시그널 조회
    signals = get_sesang_signals()
    print(f"Found {len(signals)} signals to check")
    
    # 잘못된 종목 찾기
    wrong_signals = []
    for signal in signals:
        stock = signal['stock']
        if stock in WRONG_STOCKS or any(wrong in stock for wrong in WRONG_STOCKS):
            wrong_signals.append(signal)
    
    print(f"\n❌ Found {len(wrong_signals)} signals with wrong stocks:")
    for signal in wrong_signals:
        print(f"  {signal['stock']} ({signal['signal']})")
    
    if not wrong_signals:
        print("✅ No wrong stocks found!")
        return
    
    # 수정/삭제 계획
    to_update = []
    to_delete = []
    
    for signal in wrong_signals:
        stock = signal['stock']
        
        # 매핑 테이블에서 찾기
        new_stock = STOCK_MAPPING.get(stock)
        if new_stock is None:
            # 삭제 대상
            to_delete.append(signal)
        else:
            # 수정 대상
            to_update.append({
                'signal': signal,
                'new_stock': new_stock
            })
    
    print(f"\n📝 Action plan:")
    print(f"  To update: {len(to_update)} signals")
    for item in to_update:
        print(f"    {item['signal']['stock']} -> {item['new_stock']}")
    
    print(f"  To delete: {len(to_delete)} signals")
    for signal in to_delete:
        print(f"    {signal['stock']} (DELETE)")
    
    # 확인
    confirm = input(f"\nProceed with changes? (y/N): ").lower().strip()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # 실행
    updated = 0
    deleted = 0
    
    print(f"\n🚀 Executing changes...")
    
    # 종목명 수정
    for item in to_update:
        signal = item['signal']
        new_stock = item['new_stock']
        
        if update_stock_name(signal['id'], new_stock):
            print(f"  ✓ Updated: {signal['stock']} -> {new_stock}")
            updated += 1
        else:
            print(f"  ✗ Update failed: {signal['stock']}")
    
    # 시그널 삭제
    for signal in to_delete:
        if delete_signal(signal['id']):
            print(f"  ✓ Deleted: {signal['stock']}")
            deleted += 1
        else:
            print(f"  ✗ Delete failed: {signal['stock']}")
    
    print(f"\n🎉 Cleanup completed:")
    print(f"  Updated: {updated}/{len(to_update)}")
    print(f"  Deleted: {deleted}/{len(to_delete)}")
    
    # 결과 저장
    result = {
        'total_checked': len(signals),
        'wrong_found': len(wrong_signals),
        'updated': updated,
        'deleted': deleted,
        'updated_signals': [
            {'old_stock': item['signal']['stock'], 'new_stock': item['new_stock']}
            for item in to_update
        ],
        'deleted_signals': [signal['stock'] for signal in to_delete],
        'timestamp': __import__('time').strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open('stock_cleanup_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"  Results saved to stock_cleanup_result.json")

if __name__ == "__main__":
    main()