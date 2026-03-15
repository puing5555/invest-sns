#!/usr/bin/env python3
import requests
import json

# Supabase 설정
url = "https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals"
anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"

headers = {
    "apikey": anon_key,
    "Authorization": f"Bearer {anon_key}"
}

params = {
    "select": "id,stock,ticker,signal,key_quote,timestamp,reasoning,confidence,speakers(name),influencer_videos(title,published_at)",
    "order": "created_at"
}

try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    signals = response.json()
    
    print(f"총 시그널 개수: {len(signals)}")
    
    # 세부 이슈 분석
    issues = {
        'timestamp_zero': [],
        'confidence_text': [],
        'quote_short': [],
        'reasoning_short': [],
        'invalid_signal': []
    }
    
    for signal in signals:
        signal_id = signal.get('id')
        stock = signal.get('stock', '')
        
        # 타임스탬프 0:00 체크
        timestamp = signal.get('timestamp', '')
        if timestamp in ['0:00', '00:00']:
            issues['timestamp_zero'].append({
                'id': signal_id, 
                'stock': stock, 
                'timestamp': timestamp
            })
        
        # confidence 텍스트 체크 (숫자가 아닌 경우)
        confidence = signal.get('confidence')
        if confidence and isinstance(confidence, str) and confidence in ['high', 'medium', 'low']:
            issues['confidence_text'].append({
                'id': signal_id, 
                'stock': stock, 
                'confidence': confidence
            })
        
        # key_quote 15자 미만 체크
        key_quote = signal.get('key_quote', '')
        if len(key_quote) < 15:
            issues['quote_short'].append({
                'id': signal_id, 
                'stock': stock, 
                'quote_length': len(key_quote),
                'quote': key_quote
            })
        
        # reasoning 20자 미만 체크
        reasoning = signal.get('reasoning', '')
        if len(reasoning) < 20:
            issues['reasoning_short'].append({
                'id': signal_id, 
                'stock': stock, 
                'reasoning_length': len(reasoning),
                'reasoning': reasoning
            })
        
        # 시그널 타입 체크
        signal_type = signal.get('signal', '')
        valid_signals = ['매수', '긍정', '중립', '경계', '매도']
        if signal_type not in valid_signals:
            issues['invalid_signal'].append({
                'id': signal_id, 
                'stock': stock, 
                'signal': signal_type
            })
    
    # 결과 출력
    print("\n=== 상세 이슈 분석 ===")
    
    total_issues = 0
    for issue_type, issue_list in issues.items():
        count = len(issue_list)
        total_issues += count
        print(f"{issue_type}: {count}개")
        
        if count > 0 and count <= 5:  # 5개 이하면 전체 출력
            for issue in issue_list:
                if issue_type == 'timestamp_zero':
                    print(f"  - {issue['stock']} (ID: {issue['id'][:8]}...): {issue['timestamp']}")
                elif issue_type == 'confidence_text':
                    print(f"  - {issue['stock']} (ID: {issue['id'][:8]}...): {issue['confidence']}")
                elif issue_type == 'quote_short':
                    print(f"  - {issue['stock']} (ID: {issue['id'][:8]}...): {issue['quote_length']}자 '{issue['quote']}'")
                elif issue_type == 'reasoning_short':
                    print(f"  - {issue['stock']} (ID: {issue['id'][:8]}...): {issue['reasoning_length']}자 '{issue['reasoning']}'")
                elif issue_type == 'invalid_signal':
                    print(f"  - {issue['stock']} (ID: {issue['id'][:8]}...): '{issue['signal']}'")
        elif count > 5:  # 5개 초과면 샘플만 출력
            print(f"  샘플 5개:")
            for issue in issue_list[:5]:
                if issue_type == 'confidence_text':
                    print(f"    - {issue['stock']}: {issue['confidence']}")
                elif issue_type == 'quote_short':
                    print(f"    - {issue['stock']}: {issue['quote_length']}자")
                # 다른 타입들도 필요시 추가
    
    print(f"\n총 이슈 수: {total_issues}개")
    
    # 이슈 상세 정보 저장
    with open("detailed_issues.json", "w", encoding="utf-8") as f:
        json.dump({
            'total_signals': len(signals),
            'total_issues': total_issues,
            'issues': issues
        }, f, ensure_ascii=False, indent=2)
    
    print("상세 분석 결과가 detailed_issues.json에 저장되었습니다.")

except Exception as e:
    print(f"오류 발생: {e}")