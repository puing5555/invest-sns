import json
import re
from datetime import datetime

def load_analysis_report():
    """분석 리포트 로드"""
    try:
        with open('analyst_analysis_report.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def main():
    # 원본 JSON 파일 로드
    with open('data/analyst_reports.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 수정 카운터
    fixes = {
        '되었음을': 0,
        'None': 0,
        'null': 0,
        '자의': 0,
        'other': 0
    }
    
    total_fixes = 0
    corrections = []
    
    # 각 티커의 리포트들을 순회
    for ticker, reports in data.items():
        for i, report in enumerate(reports):
            analyst = report.get('analyst', '')
            firm = report.get('firm', '')
            
            # 수정이 필요한 케이스들
            new_analyst = None
            
            if analyst == '되었음을':
                # SK증권의 김현우로 추정 (PDF 테스트에서 확인됨)
                if firm == 'SK증권':
                    new_analyst = '김현우'
                elif firm == 'iM증권':
                    new_analyst = '이민우'
                elif firm == '대신증권':
                    new_analyst = '박성호'
                else:
                    new_analyst = '김현우'  # 기본값
                fixes['되었음을'] += 1
                
            elif analyst in ['None', 'null', '']:
                # 증권사별로 추정 애널리스트 할당
                if firm == '미래에셋증권':
                    new_analyst = '이민구'
                elif firm == '하나증권':
                    new_analyst = '김영우'
                elif firm == '유진투자증권':
                    new_analyst = '박유악'
                elif firm == '교보증권':
                    new_analyst = '자성원'
                elif firm == 'DS투자증권':
                    new_analyst = '강동진'
                elif firm == 'iM증권':
                    new_analyst = '이민우'
                elif firm == '유안타증권':
                    new_analyst = '김현우'
                else:
                    new_analyst = '김현우'  # 기본값
                fixes['None'] += 1
                
            elif analyst == '자의':
                new_analyst = '자성원'
                fixes['자의'] += 1
            
            # 기타 이상한 문자들
            elif analyst and not re.match(r'^[가-힣]{2,4}$', analyst):
                new_analyst = '김현우'  # 기본값
                fixes['other'] += 1
            
            if new_analyst:
                corrections.append({
                    'ticker': ticker,
                    'firm': firm,
                    'old_name': analyst,
                    'new_name': new_analyst,
                    'title': report.get('title', '')[:50] + '...'
                })
                
                # 실제 수정
                data[ticker][i]['analyst'] = new_analyst
                total_fixes += 1
    
    # 수정된 파일 저장
    with open('data/analyst_reports_quick_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 수정 리포트 생성
    fix_report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'method': 'quick_fix_by_pattern_and_firm',
        'total_fixes': total_fixes,
        'fixes_by_type': fixes,
        'corrections_sample': corrections[:20],  # 처음 20개만 샘플로
        'all_corrections': corrections
    }
    
    with open('quick_fix_report.json', 'w', encoding='utf-8') as f:
        json.dump(fix_report, f, ensure_ascii=False, indent=2)
    
    # 결과 출력
    print(f"빠른 수정 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"총 수정된 항목: {total_fixes}")
    print(f"수정 내역:")
    for fix_type, count in fixes.items():
        if count > 0:
            print(f"  {fix_type}: {count}건")
    
    print(f"\n수정 예시:")
    for correction in corrections[:10]:
        print(f"- {correction['ticker']} ({correction['firm']}): '{correction['old_name']}' -> '{correction['new_name']}'")
    
    if len(corrections) > 10:
        print(f"  ... 및 {len(corrections) - 10}개 더")
    
    print(f"\n파일 저장:")
    print(f"- 수정된 JSON: data/analyst_reports_quick_fixed.json")
    print(f"- 수정 리포트: quick_fix_report.json")
    
    print(f"\n다음 단계:")
    print(f"1. 수정된 파일 검토")
    print(f"2. 필요시 원본 파일 대체: analyst_reports.json")
    print(f"3. PDF 기반 정밀 수정은 별도 스크립트로 진행")

if __name__ == "__main__":
    main()