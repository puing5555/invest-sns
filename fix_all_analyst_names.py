import json
import re
import requests
from io import BytesIO
import pdfplumber
import time
import os
from datetime import datetime

def extract_analyst_from_pdf(pdf_url, firm):
    """PDF에서 애널리스트 이름을 추출"""
    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        
        with BytesIO(response.content) as pdf_file:
            with pdfplumber.open(pdf_file) as pdf:
                # 첫 1-2페이지만 읽기
                text = ""
                for i, page in enumerate(pdf.pages[:2]):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                # 패턴별로 애널리스트 이름 추출 시도
                analyst_patterns = [
                    r'(?:애널리스트|연구원|선임연구위원|책임연구원|연구위원)\s*:?\s*([가-힣]{2,4})',
                    r'([가-힣]{2,4})\s*(?:애널리스트|연구원|선임연구위원|책임연구원|연구위원)',
                    r'작성자?\s*:?\s*([가-힣]{2,4})',
                    r'리서치센터\s*([가-힣]{2,4})',
                    r'Research\s*([가-힣]{2,4})',
                ]
                
                # 패턴별로 시도
                for pattern in analyst_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        candidate = matches[0]
                        if re.match(r'^[가-힣]{2,4}$', candidate):
                            return candidate
                
                # 패턴으로 찾지 못했다면 모든 한글 이름 추출 후 첫 번째 선택
                all_korean_names = re.findall(r'[가-힣]{2,4}', text)
                if all_korean_names:
                    return all_korean_names[0]
                
        return None
        
    except Exception as e:
        print(f"PDF 처리 오류: {e}")
        return None

def is_valid_korean_name(name):
    """한글 2-4글자 이름인지 확인"""
    if not name or name == "-" or name == "null" or name == "None":
        return False
    return bool(re.match(r'^[가-힣]{2,4}$', name))

def main():
    # 원본 JSON 파일 로드
    with open('data/analyst_reports.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"분석 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 수정이 필요한 리포트들 수집
    reports_to_fix = []
    total_reports = 0
    
    for ticker, reports in data.items():
        for i, report in enumerate(reports):
            total_reports += 1
            analyst = report.get('analyst', '')
            
            if not is_valid_korean_name(analyst):
                reports_to_fix.append({
                    'ticker': ticker,
                    'report_index': i,
                    'current_analyst': analyst,
                    'firm': report.get('firm', ''),
                    'pdf_url': report.get('pdf_url', ''),
                    'title': report.get('title', '')
                })
    
    print(f"총 {total_reports}개 리포트 중 {len(reports_to_fix)}개 수정 필요")
    
    # 수정 진행
    corrections = []
    failed_fixes = []
    
    for i, report_info in enumerate(reports_to_fix):
        print(f"\n[{i+1}/{len(reports_to_fix)}] {report_info['ticker']} - {report_info['firm']}")
        print(f"현재: '{report_info['current_analyst']}'")
        
        if not report_info['pdf_url']:
            print("[SKIP] PDF URL 없음")
            failed_fixes.append({**report_info, 'reason': 'No PDF URL'})
            continue
        
        # PDF에서 애널리스트 이름 추출
        extracted_name = extract_analyst_from_pdf(report_info['pdf_url'], report_info['firm'])
        
        if extracted_name and extracted_name != report_info['current_analyst']:
            # JSON 데이터에서 실제 수정
            data[report_info['ticker']][report_info['report_index']]['analyst'] = extracted_name
            
            corrections.append({
                'ticker': report_info['ticker'],
                'firm': report_info['firm'],
                'old_name': report_info['current_analyst'],
                'new_name': extracted_name,
                'pdf_url': report_info['pdf_url']
            })
            
            print(f"[SUCCESS] '{report_info['current_analyst']}' -> '{extracted_name}'")
        else:
            print(f"[FAIL] 추출 실패")
            failed_fixes.append({**report_info, 'reason': 'Extraction failed'})
        
        # API 제한을 위해 잠시 대기 (처음 50개만 처리)
        if i >= 49:  # 처음 50개만
            print(f"\n처음 50개 처리 완료. 전체를 처리하려면 limit을 제거하세요.")
            break
        time.sleep(1)
    
    # 수정된 JSON 파일 저장
    with open('data/analyst_reports_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 수정 리포트 생성
    fix_report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_reports': total_reports,
        'reports_needing_fix': len(reports_to_fix),
        'successful_corrections': len(corrections),
        'failed_fixes': len(failed_fixes),
        'success_rate': len(corrections) / len(reports_to_fix) * 100 if reports_to_fix else 0,
        'corrections': corrections,
        'failed_fixes': failed_fixes
    }
    
    with open('analyst_fix_report.json', 'w', encoding='utf-8') as f:
        json.dump(fix_report, f, ensure_ascii=False, indent=2)
    
    # 결과 출력
    print(f"\n{'='*50}")
    print(f"수정 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"총 리포트: {total_reports}")
    print(f"수정 필요: {len(reports_to_fix)}")
    print(f"성공 수정: {len(corrections)}")
    print(f"실패: {len(failed_fixes)}")
    print(f"성공률: {fix_report['success_rate']:.1f}%")
    
    print(f"\n수정 예시:")
    for correction in corrections[:10]:
        print(f"- {correction['ticker']} ({correction['firm']}): '{correction['old_name']}' -> '{correction['new_name']}'")
    
    print(f"\n파일 저장:")
    print(f"- 수정된 JSON: data/analyst_reports_fixed.json")
    print(f"- 수정 리포트: analyst_fix_report.json")

if __name__ == "__main__":
    main()