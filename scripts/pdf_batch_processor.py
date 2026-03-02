#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 배치 처리 스크립트 - 애널리스트 리포트 567건
- Supabase에서 PDF URL 조회
- 네이버 리서치에서 PDF 다운로드
- PDF 텍스트 추출 
- Claude API로 AI 요약 생성
- 애널리스트명 추출
- Supabase 업데이트
"""

import os
import sys
import json
import time
import requests
import pdfplumber
from pathlib import Path
import urllib.parse
from typing import Dict, List, Optional
import anthropic

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

# 설정
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
ANTHROPIC_API_KEY = "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"

PDF_DIR = Path("data/analyst_pdfs")
BATCH_SIZE = 20  # AI 요약 배치 크기
DOWNLOAD_DELAY = 2  # 다운로드 간격 (초)
BATCH_DELAY = 60  # 50개마다 휴식 시간 (초)

class PDFBatchProcessor:
    def __init__(self):
        self.claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # PDF 저장 디렉토리 생성
        PDF_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_analyst_reports(self) -> List[Dict]:
        """로컬 JSON 파일에서 애널리스트 리포트 조회"""
        json_file = Path("data/analyst_reports.json")
        
        if not json_file.exists():
            print(f"파일 없음: {json_file}")
            return []
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 모든 리포트를 평면화
        all_reports = []
        for ticker, reports in data.items():
            for report in reports:
                if report.get('pdf_url'):  # PDF URL이 있는 것만
                    report['id'] = f"{ticker}_{report['firm']}_{report['published_at']}"
                    all_reports.append(report)
        
        print(f"총 {len(all_reports)}개 리포트 발견")
        # 테스트용: 처음 5개만 처리
        return all_reports[:5]
    
    def download_pdf(self, pdf_url: str, filename: str) -> bool:
        """PDF 다운로드"""
        try:
            print(f"다운로드: {filename}")
            response = self.session.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            # PDF 파일 저장
            pdf_path = PDF_DIR / filename
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            print(f"저장 완료: {pdf_path}")
            return True
            
        except Exception as e:
            print(f"다운로드 실패 {filename}: {e}")
            return False
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Optional[str]:
        """PDF에서 텍스트 추출"""
        try:
            text_content = ""
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            
            # 텍스트 정리
            text_content = text_content.strip()
            if len(text_content) < 100:  # 너무 짧으면 실패로 간주
                return None
            
            return text_content
            
        except Exception as e:
            print(f"텍스트 추출 실패 {pdf_path}: {e}")
            return None
    
    def extract_analyst_name(self, text_content: str) -> Optional[str]:
        """PDF 텍스트에서 애널리스트명 추출"""
        lines = text_content.split('\n')[:20] + text_content.split('\n')[-20:]  # 앞뒤 20줄
        
        # 애널리스트명 패턴 찾기
        import re
        patterns = [
            r'(?:애널리스트|분석가|Analyst)[:：\s]*([가-힣]{2,4})',
            r'([가-힣]{2,4})[\s]*(?:애널리스트|분석가)',
            r'(?:담당|작성)[:：\s]*([가-힣]{2,4})',
            r'([가-힣]{2,4})[\s]*(?:선임연구원|연구원|책임연구원)'
        ]
        
        for line in lines:
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    name = match.group(1).strip()
                    if 2 <= len(name) <= 4:  # 한국 이름 길이 체크
                        return name
        
        return None
    
    def generate_ai_summary(self, text_content: str, firm: str, ticker: str) -> Dict[str, str]:
        """Claude API로 AI 요약 생성"""
        try:
            # 한줄요약 프롬프트
            summary_prompt = f"""
다음 애널리스트 리포트를 읽고 한줄요약을 작성해주세요.

증권사: {firm}
종목코드: {ticker}

리포트 내용:
{text_content[:4000]}

요구사항:
- 한줄로 핵심 내용만 요약
- "증권사명이 종목명에 투자의견, 목표가 제시" 형태가 아닌 실제 내용 기반 요약
- 구체적인 투자포인트나 전망 포함
- 50자 이내
"""

            summary_response = self.claude_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[{"role": "user", "content": summary_prompt}]
            )
            
            ai_summary = summary_response.content[0].text.strip()
            
            # 상세요약 프롬프트  
            detail_prompt = f"""
다음 애널리스트 리포트를 읽고 상세요약을 작성해주세요.

증권사: {firm}
종목코드: {ticker}

리포트 내용:
{text_content[:8000]}

요구사항:
- 다음 구조로 작성: 투자포인트 / 실적전망 / 밸류에이션 / 리스크 / 결론
- 스크롤 두 번 분량 (500자 이상)
- 템플릿 문장 절대 금지, 실제 내용 기반 작성
- 구체적인 수치와 근거 포함
"""

            detail_response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022", 
                max_tokens=1000,
                messages=[{"role": "user", "content": detail_prompt}]
            )
            
            ai_detail = detail_response.content[0].text.strip()
            
            return {
                "ai_summary": ai_summary,
                "ai_detail": ai_detail
            }
            
        except Exception as e:
            print(f"AI 요약 생성 실패: {e}")
            return {
                "ai_summary": "",
                "ai_detail": ""
            }
    
    def update_local_report(self, report_id: str, updates: Dict) -> bool:
        """로컬 JSON 파일 업데이트 (나중에 Supabase에 일괄 업데이트)"""
        try:
            # 업데이트 내용을 별도 파일에 저장
            update_file = Path("data/analyst_updates.json")
            
            # 기존 업데이트 파일 읽기
            if update_file.exists():
                with open(update_file, 'r', encoding='utf-8') as f:
                    all_updates = json.load(f)
            else:
                all_updates = {}
            
            # 업데이트 추가
            all_updates[report_id] = updates
            
            # 파일에 저장
            with open(update_file, 'w', encoding='utf-8') as f:
                json.dump(all_updates, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"로컬 업데이트 실패 {report_id}: {e}")
            return False
    
    def process_batch(self):
        """전체 배치 처리 실행"""
        print("PDF 배치 처리 시작")
        
        # 1. Supabase에서 리포트 조회
        reports = self.get_analyst_reports()
        
        if not reports:
            print("처리할 리포트가 없습니다")
            return
        
        processed_count = 0
        success_count = 0
        
        # 결과 저장용
        results = []
        
        for i, report in enumerate(reports, 1):
            print(f"\n[{i}/{len(reports)}] 처리 중...")
            print(f"종목: {report.get('ticker', 'Unknown')}")
            print(f"증권사: {report.get('firm', 'Unknown')}")
            
            # PDF 파일명 생성 
            pdf_filename = f"{report['id']}.pdf"
            pdf_path = PDF_DIR / pdf_filename
            
            # 2. PDF 다운로드
            if not pdf_path.exists():
                if not self.download_pdf(report['pdf_url'], pdf_filename):
                    continue
                
                # 레이트리밋 적용
                time.sleep(DOWNLOAD_DELAY)
                
                # 50개마다 휴식
                if processed_count % 50 == 0 and processed_count > 0:
                    print(f"{BATCH_DELAY}초 휴식...")
                    time.sleep(BATCH_DELAY)
            
            # 3. PDF 텍스트 추출
            text_content = self.extract_text_from_pdf(pdf_path)
            if not text_content:
                print("텍스트 추출 실패")
                continue
            
            # 4. 애널리스트명 추출
            analyst_name = self.extract_analyst_name(text_content)
            
            # 5. AI 요약 생성
            ai_results = self.generate_ai_summary(
                text_content, 
                report.get('firm', ''),
                report.get('ticker', '')
            )
            
            # 6. Supabase 업데이트 준비
            updates = {}
            if analyst_name:
                updates['analyst_name'] = analyst_name
            if ai_results['ai_summary']:
                updates['ai_summary'] = ai_results['ai_summary']
            if ai_results['ai_detail']:
                updates['ai_detail'] = ai_results['ai_detail']
            
            # 7. 로컬 업데이트
            if updates and self.update_local_report(report['id'], updates):
                success_count += 1
                print("처리 완료")
            else:
                print("업데이트 실패")
            
            # 결과 저장
            result = {
                'id': report['id'],
                'ticker': report.get('ticker'),
                'firm': report.get('firm'), 
                'analyst_name': analyst_name,
                'ai_summary': ai_results['ai_summary'],
                'success': len(updates) > 0
            }
            results.append(result)
            
            processed_count += 1
            
            # 진행률 출력
            if processed_count % 10 == 0:
                print(f"진행률: {processed_count}/{len(reports)} ({processed_count/len(reports)*100:.1f}%)")
        
        # 최종 결과 저장
        result_file = f"pdf_processing_results_{int(time.time())}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n배치 처리 완료!")
        print(f"총 처리: {processed_count}개")
        print(f"성공: {success_count}개") 
        print(f"결과 파일: {result_file}")

if __name__ == "__main__":
    processor = PDFBatchProcessor()
    processor.process_batch()