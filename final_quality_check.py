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
    
    # 기존 이슈 + 새로운 검증
    issues = {
        'timestamp_zero': [],
        'confidence_text': [],
        'quote_short': [],
        'reasoning_short': [],
        'invalid_signal': [],
        'video_stock_violations': violations,  # 새로운 검증
        'quote_quality': [],  # key_quote 품질 검증
        'reasoning_quality': []  # reasoning 품질 검증
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
        
        # 새로운 품질 검증
        # key_quote 품질 체크 (너무 일반적이거나 구체적이지 않은 경우)
        if key_quote:
            generic_phrases = ['좋다', '나쁘다', '추천', '생각', '봅니다', '같습니다']
            if any(phrase in key_quote for phrase in generic_phrases) and len(key_quote) < 25:
                issues['quote_quality'].append({
                    'id': signal_id, 'stock': stock, 'quote': key_quote, 'issue': 'too_generic'
                })
        
        # reasoning 품질 체크 (너무 짧거나 구체적이지 않은 경우)
        if reasoning and len(reasoning) < 50:  # 20자 이상이지만 50자 미만은 품질 이슈
            issues['reasoning_quality'].append({
                'id': signal_id, 'stock': stock, 'reasoning': reasoning, 'issue': 'could_be_more_detailed'
            })
    
    # 결과 출력
    print(f"총 시그널 개수: {len(signals)}")
    print("\n=== 최종 품질 검증 결과 ===")
    
    total_critical_issues = 0
    total_quality_issues = 0
    
    for issue_type, issue_list in issues.items():
        count = len(issue_list)
        
        if issue_type in ['timestamp_zero', 'confidence_text', 'quote_short', 'reasoning_short', 'invalid_signal']:
            total_critical_issues += count
            print(f"🚨 {issue_type}: {count}개 (중대 이슈)")
        elif issue_type in ['video_stock_violations']:
            total_critical_issues += count
            print(f"🚨 {issue_type}: {count}개 (규칙 위반)")
        else:
            total_quality_issues += count
            print(f"⚠️ {issue_type}: {count}개 (품질 개선 권장)")
        
        if count > 0 and count <= 3:
            for issue in issue_list[:3]:
                if issue_type == 'video_stock_violations':
                    print(f"  - {issue['stock']} ({issue['count']}회 중복) in '{issue['video_title'][:50]}...'")
                elif issue_type == 'quote_quality':
                    print(f"  - {issue['stock']}: '{issue['quote']}'")
                elif issue_type == 'reasoning_quality':
                    print(f"  - {issue['stock']}: {len(issue['reasoning'])}자 '{issue['reasoning'][:30]}...'")
    
    print(f"\n📊 요약:")
    print(f"중대 이슈: {total_critical_issues}개 (프롬프트로 해결 필수)")
    print(f"품질 이슈: {total_quality_issues}개 (추가 개선 권장)")
    
    # 프롬프트 개선 가능성 판단
    if total_critical_issues == 0:
        print("\n✅ 결론: 모든 중대 이슈가 해결됨. 프롬프트 개선 루프 종료 가능.")
    elif total_critical_issues <= 5:
        print(f"\n⚠️ 결론: {total_critical_issues}개 중대 이슈 남음. 추가 개선 시도 권장.")
    else:
        print(f"\n🚨 결론: {total_critical_issues}개 중대 이슈. 프롬프트 대폭 개선 필요.")
    
    # 상세 결과 저장
    with open("final_quality_report.json", "w", encoding="utf-8") as f:
        json.dump({
            'total_signals': len(signals),
            'critical_issues': total_critical_issues,
            'quality_issues': total_quality_issues,
            'issues': issues,
            'improvement_recommendation': 'STOP' if total_critical_issues == 0 else 'CONTINUE'
        }, f, ensure_ascii=False, indent=2)
    
    print("최종 품질 리포트가 final_quality_report.json에 저장되었습니다.")

except Exception as e:
    print(f"오류 발생: {e}")