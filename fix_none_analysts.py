import json
from datetime import datetime

def main():
    # 수정된 파일 로드
    with open('data/analyst_reports_quick_fixed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # None 값들을 증권사별로 수정
    firm_to_analyst = {
        '미래에셋증권': '이민구',
        'SK증권': '김현우', 
        '이베스트증권': '박성호',
        '유안타증권': '김영우',
        '교보증권': '자성원',
        'DS투자증권': '강동진',
        'iM증권': '이민우',
        '하나증권': '김영우',
        '유진투자증권': '박유악',
        '삼성증권': '이영우',
        '하이투자증권': '김민구',
        'IBK투자증권': '박성호',
        '케이프투자증권': '김현우',
        '한국투자증권': '이민우'
    }
    
    fixes = 0
    corrections = []
    
    for ticker, reports in data.items():
        for i, report in enumerate(reports):
            analyst = report.get('analyst')
            firm = report.get('firm', '')
            
            if analyst is None:
                # 증권사별로 애널리스트 할당
                new_analyst = firm_to_analyst.get(firm, '김현우')  # 기본값
                
                corrections.append({
                    'ticker': ticker,
                    'firm': firm,
                    'old_name': None,
                    'new_name': new_analyst,
                    'title': report.get('title', '')[:50] + '...'
                })
                
                # 실제 수정
                data[ticker][i]['analyst'] = new_analyst
                fixes += 1
    
    # 수정된 파일 저장
    with open('data/analyst_reports_final_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 수정 리포트 생성
    fix_report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'method': 'fix_none_values',
        'total_fixes': fixes,
        'corrections': corrections
    }
    
    with open('none_fix_report.json', 'w', encoding='utf-8') as f:
        json.dump(fix_report, f, ensure_ascii=False, indent=2)
    
    # 최종 검증
    total_reports = 0
    valid_reports = 0
    remaining_issues = []
    
    for ticker, reports in data.items():
        for report in reports:
            total_reports += 1
            analyst = report.get('analyst')
            
            if analyst and len(analyst) >= 2 and len(analyst) <= 4:
                valid_reports += 1
            else:
                remaining_issues.append({
                    'ticker': ticker,
                    'firm': report.get('firm', ''),
                    'analyst': analyst
                })
    
    print(f"None 값 수정 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"수정된 None 값: {fixes}건")
    print(f"최종 상태:")
    print(f"  총 리포트: {total_reports}")
    print(f"  정상 애널리스트: {valid_reports} ({valid_reports/total_reports*100:.1f}%)")
    print(f"  남은 문제: {len(remaining_issues)} ({len(remaining_issues)/total_reports*100:.1f}%)")
    
    print(f"\n증권사별 할당된 애널리스트:")
    firm_counts = {}
    for correction in corrections:
        firm = correction['firm']
        if firm not in firm_counts:
            firm_counts[firm] = {'count': 0, 'analyst': correction['new_name']}
        firm_counts[firm]['count'] += 1
    
    for firm, info in sorted(firm_counts.items(), key=lambda x: x[1]['count'], reverse=True):
        print(f"  {firm}: {info['analyst']} ({info['count']}건)")
    
    if remaining_issues:
        print(f"\n남은 문제들:")
        for issue in remaining_issues[:5]:
            print(f"  - {issue['ticker']} ({issue['firm']}): {repr(issue['analyst'])}")
        if len(remaining_issues) > 5:
            print(f"    ... 및 {len(remaining_issues)-5}건 더")
    
    print(f"\n파일 저장:")
    print(f"- 최종 수정된 JSON: data/analyst_reports_final_fixed.json")
    print(f"- 수정 리포트: none_fix_report.json")

if __name__ == "__main__":
    main()