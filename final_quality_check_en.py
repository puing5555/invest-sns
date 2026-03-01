#!/usr/bin/env python3
import requests
import json
from collections import defaultdict

# Supabase 설정
url = "https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals"
anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"

headers = {
    "apikey": anon_key,
    "Authorization": f"Bearer {anon_key}"
}

params = {
    "select": "id,stock,ticker,signal,key_quote,timestamp,reasoning,confidence,speakers(name),influencer_videos(title,published_at,id)",
    "order": "created_at"
}

try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    signals = response.json()
    
    # 1영상 1종목 1시그널 규칙 검증
    video_stock_combinations = defaultdict(int)
    violations = []
    
    for signal in signals:
        video_info = signal.get('influencer_videos', {})
        if video_info:
            video_id = video_info.get('id')
            stock = signal.get('stock')
            key = f"{video_id}_{stock}"
            video_stock_combinations[key] += 1
            
            if video_stock_combinations[key] > 1:
                violations.append({
                    'video_title': video_info.get('title', 'Unknown'),
                    'stock': stock,
                    'count': video_stock_combinations[key],
                    'signal_id': signal.get('id')
                })
    
    issues = {
        'timestamp_zero': [],
        'confidence_text': [],
        'quote_short': [],
        'reasoning_short': [],
        'invalid_signal': [],
        'video_stock_violations': violations,
        'quote_quality': [],
        'reasoning_quality': []
    }
    
    for signal in signals:
        signal_id = signal.get('id')
        stock = signal.get('stock', '')
        
        # 기존 검증들
        timestamp = signal.get('timestamp', '')
        if timestamp in ['0:00', '00:00']:
            issues['timestamp_zero'].append({
                'id': signal_id, 'stock': stock, 'timestamp': timestamp
            })
        
        confidence = signal.get('confidence')
        if confidence and isinstance(confidence, str) and confidence in ['high', 'medium', 'low']:
            issues['confidence_text'].append({
                'id': signal_id, 'stock': stock, 'confidence': confidence
            })
        
        key_quote = signal.get('key_quote', '')
        if len(key_quote) < 15:
            issues['quote_short'].append({
                'id': signal_id, 'stock': stock, 'quote_length': len(key_quote), 'quote': key_quote
            })
        
        reasoning = signal.get('reasoning', '')
        if len(reasoning) < 20:
            issues['reasoning_short'].append({
                'id': signal_id, 'stock': stock, 'reasoning_length': len(reasoning), 'reasoning': reasoning
            })
        
        signal_type = signal.get('signal', '')
        valid_signals = ['매수', '긍정', '중립', '경계', '매도']
        if signal_type not in valid_signals:
            issues['invalid_signal'].append({
                'id': signal_id, 'stock': stock, 'signal': signal_type
            })
    
    # 결과 출력
    print(f"Total signals: {len(signals)}")
    print("\n=== FINAL QUALITY CHECK RESULTS ===")
    
    total_critical_issues = 0
    total_quality_issues = 0
    
    for issue_type, issue_list in issues.items():
        count = len(issue_list)
        
        if issue_type in ['timestamp_zero', 'confidence_text', 'quote_short', 'reasoning_short', 'invalid_signal']:
            total_critical_issues += count
            print(f"CRITICAL {issue_type}: {count}")
        elif issue_type in ['video_stock_violations']:
            total_critical_issues += count
            print(f"RULE_VIOLATION {issue_type}: {count}")
        else:
            total_quality_issues += count
            print(f"QUALITY {issue_type}: {count}")
        
        if count > 0 and count <= 3:
            for issue in issue_list[:3]:
                if issue_type == 'video_stock_violations':
                    print(f"  - {issue['stock']} ({issue['count']} duplicates)")
    
    print(f"\nSUMMARY:")
    print(f"Critical issues: {total_critical_issues}")
    print(f"Quality issues: {total_quality_issues}")
    
    # 개선 종료 조건 판단
    if total_critical_issues == 0:
        print("\nCONCLUSION: All critical issues resolved. STOP improvement loop.")
        recommendation = "STOP"
    elif total_critical_issues <= 5:
        print(f"\nCONCLUSION: {total_critical_issues} critical issues remain. Continue improvement.")
        recommendation = "CONTINUE"
    else:
        print(f"\nCONCLUSION: {total_critical_issues} critical issues. Major improvement needed.")
        recommendation = "MAJOR_IMPROVEMENT"
    
    # 상세 결과 저장
    with open("final_quality_report.json", "w", encoding="utf-8") as f:
        json.dump({
            'total_signals': len(signals),
            'critical_issues': total_critical_issues,
            'quality_issues': total_quality_issues,
            'issues': issues,
            'improvement_recommendation': recommendation
        }, f, ensure_ascii=False, indent=2)
    
    print("Final quality report saved to final_quality_report.json")

except Exception as e:
    print(f"Error: {e}")