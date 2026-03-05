#!/usr/bin/env python3
"""
새 프롬프트 테스트 스크립트
삼성전자(005930) 리포트 1건으로 테스트
"""

import json
import os
from pathlib import Path
from anthropic import Anthropic

# 설정
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

WORK_DIR = Path("C:/Users/Mario/work/invest-sns")
DATA_DIR = WORK_DIR / "data"
ANALYST_REPORTS_FILE = DATA_DIR / "analyst_reports.json"

# 새로운 ai_detail 프롬프트 v2 - 숫자 중심 포맷
AI_DETAIL_PROMPT = """다음은 한국 증권회사에서 발행한 애널리스트 리포트입니다. 
PDF 내용을 바탕으로 투자자를 위한 상세 분석을 5개 섹션으로 정리해주세요.

**출력 형식 (반드시 ## 마크다운 헤더 사용):**

## 투자포인트
이 종목을 왜 사야 하는지 투자 아이디어 중심으로 작성. 산업 변화, 경쟁 우위, 성장 동력 등 핵심 논리만. 실적 숫자는 넣지 말고 3~4줄로 간결하게.

## 실적전망  
문장 나열 금지. 숫자 테이블 형식으로만 작성.
예시: 매출 208조(+376% YoY) / 영업이익률 40%(+27%p) / 목표가 30만원
깔끔하게 숫자만 보이도록.

## 밸류에이션
문장 나열 금지. 숫자만 작성.
예시: PER 12.3x / PBR 1.8x / 목표 PER 15x → 목표가 30만원

## 리스크
핵심 리스크 2~3개를 간결하게.

## 결론
최종 결론 2~3줄. "사야 하는지 말아야 하는지" 명확하게 제시.

**규칙:**
- 5개 섹션 고정, 순서 고정
- PDF에 해당 내용 없으면 "정보 없음"
- 전체 한글 300~500자
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

def test_new_prompt():
    """새 프롬프트 테스트"""
    print("새 프롬프트 테스트 시작...")
    
    # 데이터 로드
    with open(ANALYST_REPORTS_FILE, 'r', encoding='utf-8') as f:
        reports_data = json.load(f)
    
    # 삼성전자 데이터 찾기
    samsung_reports = reports_data.get('005930', [])
    if not samsung_reports:
        print("삼성전자 리포트를 찾을 수 없습니다.")
        return
    
    # 첫 번째 리포트 선택
    test_report = samsung_reports[0]
    print(f"테스트 리포트: {test_report.get('title', '')} - {test_report.get('firm', '')}")
    
    # 기존 AI 요약 출력
    print("\n=== 기존 AI 요약 (v1) ===")
    print(test_report.get('ai_detail', ''))
    
    # 목표가 포맷팅
    target_price_str = f"{test_report.get('target_price', 0):,}원" if test_report.get('target_price') else "미제시"
    
    # 새 프롬프트로 생성
    prompt = AI_DETAIL_PROMPT.format(
        title=test_report.get('title', ''),
        firm=test_report.get('firm', ''),
        ticker='005930',
        stock_name=get_stock_name('005930'),
        target_price=target_price_str,
        opinion=test_report.get('opinion', ''),
        published_at=test_report.get('published_at', ''),
        existing_detail=test_report.get('ai_detail', '')[:1000] + "..." if len(test_report.get('ai_detail', '')) > 1000 else test_report.get('ai_detail', '')
    )
    
    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        new_ai_detail = message.content[0].text
        
        print("\n=== 새 AI 요약 (v2) ===")
        print(new_ai_detail)
        
        return new_ai_detail
        
    except Exception as e:
        print(f"API 호출 실패: {e}")
        return None

if __name__ == "__main__":
    test_new_prompt()