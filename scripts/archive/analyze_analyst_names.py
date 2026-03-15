import json
import re

def is_valid_korean_name(name):
    """한글 2-4글자 이름인지 확인"""
    if not name or name == "-":
        return False
    
    # 한글만 포함하고 2-4글자인지 확인
    if re.match(r'^[가-힣]{2,4}$', name):
        return True
    
    return False

def is_suspicious_name(name):
    """의미없는 단어/문장 조각인지 확인"""
    if not name:
        return True
    
    suspicious_patterns = [
        r'되었음',
        r'자의',
        r'^-+$',
        r'^\s*$',
        r'[0-9]',  # 숫자 포함
        r'[a-zA-Z]',  # 영어 포함
        r'[^\w가-힣\s]',  # 특수문자 포함
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, name):
            return True
    
    return False

def main():
    # JSON 파일 로드
    with open('data/analyst_reports.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"총 {len(data)} 개 티커의 리포트 분석 중...")
    
    # 이상한 애널리스트 이름들 수집
    suspicious_reports = []
    valid_reports = []
    total_reports = 0
    
    analyst_frequency = {}  # 애널리스트 이름 빈도 조사
    
    for ticker, reports in data.items():
        for report in reports:
            total_reports += 1
            analyst = report.get('analyst', '')
            
            # 빈도 조사
            if analyst in analyst_frequency:
                analyst_frequency[analyst] += 1
            else:
                analyst_frequency[analyst] = 1
            
            if not is_valid_korean_name(analyst) or is_suspicious_name(analyst):
                suspicious_reports.append({
                    'ticker': ticker,
                    'firm': report.get('firm', ''),
                    'current_analyst': analyst,
                    'published_at': report.get('published_at', ''),
                    'pdf_url': report.get('pdf_url', ''),
                    'title': report.get('title', ''),
                })
            else:
                valid_reports.append({
                    'analyst': analyst,
                    'firm': report.get('firm', ''),
                })
    
    print(f"\n=== 분석 결과 ===")
    print(f"총 리포트 수: {total_reports}")
    print(f"이상한 애널리스트 이름: {len(suspicious_reports)} ({len(suspicious_reports)/total_reports*100:.1f}%)")
    print(f"정상 애널리스트 이름: {len(valid_reports)} ({len(valid_reports)/total_reports*100:.1f}%)")
    
    # 가장 자주 나타나는 이상한 이름들
    print(f"\n=== 가장 자주 나타나는 이상한 이름들 ===")
    suspicious_names = [r['current_analyst'] for r in suspicious_reports]
    suspicious_freq = {}
    for name in suspicious_names:
        suspicious_freq[name] = suspicious_freq.get(name, 0) + 1
    
    for name, count in sorted(suspicious_freq.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"'{name}': {count}건")
    
    # 정상 애널리스트들의 증권사별 분포
    print(f"\n=== 정상 애널리스트 이름 예시 ===")
    valid_analysts = list(set([r['analyst'] for r in valid_reports]))
    for name in valid_analysts[:20]:
        firms = [r['firm'] for r in valid_reports if r['analyst'] == name]
        firm_counts = {}
        for firm in firms:
            firm_counts[firm] = firm_counts.get(firm, 0) + 1
        main_firm = max(firm_counts.items(), key=lambda x: x[1])[0]
        print(f"'{name}' - {main_firm} ({len(firms)}건)")
    
    # 증권사별 이상한 이름 분포
    print(f"\n=== 증권사별 이상한 이름 분포 ===")
    firm_issues = {}
    for report in suspicious_reports:
        firm = report['firm']
        firm_issues[firm] = firm_issues.get(firm, 0) + 1
    
    for firm, count in sorted(firm_issues.items(), key=lambda x: x[1], reverse=True):
        print(f"{firm}: {count}건")
    
    # 결과를 JSON으로 저장
    result = {
        'total_reports': total_reports,
        'suspicious_count': len(suspicious_reports),
        'valid_count': len(valid_reports),
        'suspicious_names_frequency': suspicious_freq,
        'firm_issues': firm_issues,
        'suspicious_reports_sample': suspicious_reports[:50],  # 처음 50개만
        'valid_analysts_sample': valid_analysts[:50]
    }
    
    with open('analyst_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n결과가 analyst_analysis_report.json 파일에 저장되었습니다.")
    print(f"PDF에서 애널리스트 이름을 재추출하여 수정하려면 fix_analyst_names.py 를 실행하세요.")

if __name__ == "__main__":
    main()