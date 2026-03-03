#!/usr/bin/env python3
"""
AI Detail 재생성 테스트 스크립트 (5개만)
"""

import json
import os
from pathlib import Path
import time
from anthropic import Anthropic

# 설정
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

WORK_DIR = Path("C:/Users/Mario/work/invest-sns")
DATA_DIR = WORK_DIR / "data"
ANALYST_REPORTS_FILE = DATA_DIR / "analyst_reports.json"

# 새로운 ai_detail 프롬프트
AI_DETAIL_PROMPT = """다음은 한국 증권회사에서 발행한 애널리스트 리포트입니다. 
PDF 내용을 바탕으로 투자자를 위한 상세 분석을 5개 섹션으로 정리해주세요.

**출력 형식 (반드시 ## 마크다운 헤더 사용):**

## 투자포인트
핵심 투자 판단과 근거, 왜 이 종목인지 (4~5줄)

## 실적전망  
매출/영업이익/순이익 전망 수치 포함 (1~3줄)

## 밸류에이션
PER/PBR/목표가 근거 (1~2줄)

## 리스크
주요 위험 요인 (1~2줄)

## 결론
최종 투자의견 + 향후 전망 요약 (2~3줄)

**규칙:**
- 5개 섹션 고정, 순서 고정
- PDF에 해당 내용 없으면 "정보 없음"
- 전체 한글 400~600자
- 정확한 수치와 근거 기반으로 작성

**입력 데이터:**
- 제목: {title}  
- 증권사: {firm}
- 종목: {ticker} ({stock_name})
- 목표가: {target_price}
- 투자의견: {opinion}
- 발행일: {published_at}
- 기존 AI 요약: {existing_detail}

위 정보를 바탕으로 새로운 형식의 상세 분석을 작성해주세요."""

def get_stock_name(ticker: str) -> str:
    """종목 코드에서 종목명 가져오기"""
    ticker_names = {
        '240810': '원익QnC', '284620': '카이', '298040': '효성중공업', 
        '352820': '하이브', '403870': 'HPSP', '090430': '아모레퍼시픽',
        '000660': 'SK하이닉스', '079160': 'CJ CGV', '005380': '현대자동차',
        '005930': '삼성전자', '036930': '주성엔지니어링', '042700': '한미반도체', 
        '006400': '삼성SDI', '000720': '현대건설', '005940': 'NH투자증권',
        '016360': '삼성증권', '039490': '키움증권', '051910': 'LG화학',
        '036570': '엔씨소프트', '071050': '한국금융지주'
    }
    return ticker_names.get(ticker, ticker)

def main():
    """테스트 함수"""
    print("AI Detail 재생성 테스트 (5개)")
    
    # 데이터 로드
    with open(ANALYST_REPORTS_FILE, 'r', encoding='utf-8') as f:
        reports_data = json.load(f)
    
    # 첫 번째 종목의 첫 5개 리포트 처리
    test_results = []
    count = 0
    
    for ticker, reports in reports_data.items():
        for i, report in enumerate(reports):
            if count >= 5:
                break
            if not report.get('ai_detail'):
                continue
                
            print(f"\n[{count+1}/5] 처리중: {ticker} - {report.get('title', '')[:30]}...")
            
            # 목표가 포맷팅
            target_price_str = f"{report.get('target_price', 0):,}원" if report.get('target_price') else "미제시"
            
            prompt = AI_DETAIL_PROMPT.format(
                title=report.get('title', ''),
                firm=report.get('firm', ''),
                ticker=ticker,
                stock_name=get_stock_name(ticker),
                target_price=target_price_str,
                opinion=report.get('opinion', ''),
                published_at=report.get('published_at', ''),
                existing_detail=report.get('ai_detail', '')[:500] + "..." if len(report.get('ai_detail', '')) > 500 else report.get('ai_detail', '')
            )
            
            try:
                message = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                new_ai_detail = message.content[0].text
                
                test_results.append({
                    "ticker": ticker,
                    "index": i,
                    "title": report.get('title', ''),
                    "original": report.get('ai_detail', ''),
                    "regenerated": new_ai_detail
                })
                
                print(f"성공! 길이: {len(new_ai_detail)}자")
                print("재생성 결과:")
                print(new_ai_detail)
                print("-" * 50)
                
                count += 1
                
            except Exception as e:
                print(f"실패: {e}")
            
            time.sleep(2)  # Rate limit 방지
        
        if count >= 5:
            break
    
    # 테스트 결과 저장
    test_output = DATA_DIR / "ai_detail_test_results.json"
    with open(test_output, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n테스트 완료! 결과 저장: {test_output}")

if __name__ == "__main__":
    main()