import json
import re

def main():
    # 수정된 파일을 로드
    with open('data/analyst_reports_quick_fixed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 여전히 이상한 애널리스트 이름들 찾기
    remaining_issues = {}
    total_reports = 0
    valid_reports = 0
    
    for ticker, reports in data.items():
        for report in reports:
            total_reports += 1
            analyst = report.get('analyst')
            
            # None, null, 빈 값 등을 체크
            is_valid = True
            issue_type = None
            
            if analyst is None:
                is_valid = False
                issue_type = 'None_type'
            elif analyst == 'null':
                is_valid = False
                issue_type = 'null_string'
            elif analyst == '':
                is_valid = False
                issue_type = 'empty_string'
            elif not isinstance(analyst, str):
                is_valid = False
                issue_type = f'wrong_type_{type(analyst).__name__}'
            elif not re.match(r'^[가-힣]{2,4}$', analyst):
                is_valid = False
                issue_type = 'invalid_pattern'
            
            if not is_valid:
                if issue_type not in remaining_issues:
                    remaining_issues[issue_type] = []
                remaining_issues[issue_type].append({
                    'ticker': ticker,
                    'firm': report.get('firm', ''),
                    'analyst': analyst,
                    'title': report.get('title', '')[:30] + '...'
                })
            else:
                valid_reports += 1
    
    print(f"=== 수정 후 상태 확인 ===")
    print(f"총 리포트: {total_reports}")
    print(f"정상 애널리스트: {valid_reports} ({valid_reports/total_reports*100:.1f}%)")
    print(f"여전히 문제: {total_reports-valid_reports} ({(total_reports-valid_reports)/total_reports*100:.1f}%)")
    
    print(f"\n=== 남은 문제들 ===")
    for issue_type, cases in remaining_issues.items():
        print(f"{issue_type}: {len(cases)}건")
        for case in cases[:5]:  # 처음 5개만 출력
            print(f"  - {case['ticker']} ({case['firm']}): {repr(case['analyst'])}")
        if len(cases) > 5:
            print(f"    ... 및 {len(cases)-5}건 더")
    
    # 결과 저장
    with open('remaining_issues_report.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_reports': total_reports,
            'valid_reports': valid_reports,
            'remaining_issues': remaining_issues
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n상세 결과가 remaining_issues_report.json에 저장되었습니다.")

if __name__ == "__main__":
    main()