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
    
    # 결과를 JSON 파일로 저장
    with open("current_signals.json", "w", encoding="utf-8") as f:
        json.dump(signals, f, ensure_ascii=False, indent=2)
    
    print("데이터가 current_signals.json에 저장되었습니다.")
    
    # 간단한 통계 출력
    signal_types = {}
    issues = []
    
    for i, signal in enumerate(signals):
        # 시그널 타입 통계
        signal_type = signal.get('signal', 'None')
        signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
        
        # 이슈 체크
        issues_for_this = []
        
        # key_quote 체크 (15자 이상)
        key_quote = signal.get('key_quote', '')
        if not key_quote or len(key_quote) < 15:
            issues_for_this.append(f"key_quote 너무 짧음: '{key_quote}'")
        
        # reasoning 체크 (20자 이상)
        reasoning = signal.get('reasoning', '')
        if not reasoning or len(reasoning) < 20:
            issues_for_this.append(f"reasoning 너무 짧음: '{reasoning}'")
        
        # signal 한글 체크
        if signal_type not in ['매수', '긍정', '중립', '경계', '매도']:
            issues_for_this.append(f"잘못된 시그널 타입: '{signal_type}'")
        
        # timestamp 체크
        timestamp = signal.get('timestamp', '')
        if not timestamp or timestamp == '0:00':
            issues_for_this.append(f"잘못된 타임스탬프: '{timestamp}'")
        
        # confidence 체크
        confidence = signal.get('confidence')
        if confidence is None:
            issues_for_this.append("confidence 누락")
        
        if issues_for_this:
            issues.append({
                'id': signal.get('id'),
                'stock': signal.get('stock'),
                'issues': issues_for_this
            })
    
    print("\n=== 시그널 타입 통계 ===")
    for signal_type, count in signal_types.items():
        print(f"{signal_type}: {count}개")
    
    print(f"\n=== 이슈 발견 ===")
    print(f"총 이슈가 있는 시그널: {len(issues)}개")
    
    if issues:
        print("\n첫 10개 이슈:")
        for issue in issues[:10]:
            print(f"ID {issue['id']} ({issue['stock']}):")
            for issue_detail in issue['issues']:
                print(f"  - {issue_detail}")
    
    # 이슈 정보도 저장
    with open("signal_issues.json", "w", encoding="utf-8") as f:
        json.dump({
            'total_signals': len(signals),
            'total_issues': len(issues),
            'signal_types': signal_types,
            'issues': issues
        }, f, ensure_ascii=False, indent=2)
    
except Exception as e:
    print(f"오류 발생: {e}")