import json
import re
import requests
from io import BytesIO
import pdfplumber
import time

def extract_analyst_from_pdf(pdf_url, firm):
    """PDF에서 애널리스트 이름을 추출"""
    try:
        print(f"PDF 다운로드: {pdf_url}")
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
                
                print(f"추출된 텍스트 길이: {len(text)}")
                
                # 한글 이름 패턴으로 추출
                analyst_patterns = [
                    r'(?:애널리스트|연구원|선임연구위원|책임연구원|연구위원)\s*:?\s*([가-힣]{2,4})',
                    r'([가-힣]{2,4})\s*(?:애널리스트|연구원|선임연구위원|책임연구원|연구위원)',
                    r'작성자?\s*:?\s*([가-힣]{2,4})',
                    r'리서치센터\s*([가-힣]{2,4})',
                    r'Research\s*([가-힣]{2,4})',
                ]
                
                # 패턴별로 시도
                for i, pattern in enumerate(analyst_patterns):
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        print(f"패턴 {i+1}에서 발견: {matches}")
                        candidate = matches[0]
                        if re.match(r'^[가-힣]{2,4}$', candidate):
                            return candidate
                
                # 패턴으로 찾지 못했다면 모든 한글 이름 추출
                all_korean_names = re.findall(r'[가-힣]{2,4}', text)
                print(f"모든 한글 이름들: {all_korean_names[:20]}...")
                
                # 자주 나타나는 이름 중에서 선택
                if all_korean_names:
                    # 첫 페이지에 나오는 이름을 우선
                    return all_korean_names[0]
                
        return None
        
    except Exception as e:
        print(f"PDF 처리 오류: {e}")
        return None

def main():
    # 분석 리포트 로드
    with open('analyst_analysis_report.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    sample_reports = data['suspicious_reports_sample'][:5]  # 처음 5개만 테스트
    
    corrections = []
    
    for i, report in enumerate(sample_reports):
        print(f"\n=== [{i+1}/{len(sample_reports)}] ===")
        print(f"티커: {report['ticker']}")
        print(f"증권사: {report['firm']}")
        print(f"현재 애널리스트: '{report['current_analyst']}'")
        print(f"제목: {report['title'][:50]}...")
        
        if report['pdf_url']:
            corrected_name = extract_analyst_from_pdf(report['pdf_url'], report['firm'])
            
            if corrected_name and corrected_name != report['current_analyst']:
                corrections.append({
                    'ticker': report['ticker'],
                    'firm': report['firm'],
                    'old_name': report['current_analyst'],
                    'new_name': corrected_name,
                    'pdf_url': report['pdf_url']
                })
                print(f"[SUCCESS] '{report['current_analyst']}' -> '{corrected_name}'")
            else:
                print(f"[FAIL] 추출 실패 또는 동일한 이름")
        else:
            print(f"[SKIP] PDF URL이 없음")
        
        # API 제한을 위해 잠시 대기
        time.sleep(2)
    
    print(f"\n=== 테스트 결과 ===")
    print(f"성공적으로 수정된 항목: {len(corrections)}")
    
    for correction in corrections:
        print(f"- {correction['ticker']} ({correction['firm']}): '{correction['old_name']}' -> '{correction['new_name']}'")
    
    # corrections를 JSON으로 저장
    with open('pdf_extraction_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'test_count': len(sample_reports),
            'success_count': len(corrections),
            'corrections': corrections
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n테스트 결과가 pdf_extraction_test_results.json 파일에 저장되었습니다.")

if __name__ == "__main__":
    main()