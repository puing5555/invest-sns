#!/usr/bin/env python3
import json
import os
from pathlib import Path
from anthropic import Anthropic

# 환경설정
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=ANTHROPIC_API_KEY)

# 파일 경로
DATA_DIR = Path("C:/Users/Mario/work/invest-sns/data")
ANALYST_REPORTS_FILE = DATA_DIR / "analyst_reports.json"

# 프롬프트
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

# 데이터 로드
with open(ANALYST_REPORTS_FILE, 'r', encoding='utf-8') as f:
    reports_data = json.load(f)

# 첫 번째 리포트 가져오기
ticker = list(reports_data.keys())[0]
first_report = reports_data[ticker][0]

print(f"테스트 종목: {ticker}")
print(f"제목: {first_report.get('title', '')}")

# 프롬프트 생성
prompt = AI_DETAIL_PROMPT.format(
    title=first_report.get('title', ''),
    firm=first_report.get('firm', ''),
    ticker=ticker,
    stock_name=ticker,
    target_price=f"{first_report.get('target_price', 0):,}원" if first_report.get('target_price') else "미제시",
    opinion=first_report.get('opinion', ''),
    published_at=first_report.get('published_at', ''),
    existing_detail=first_report.get('ai_detail', '')[:500]
)

print("API 호출 중...")

# Claude API 호출
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
    
    result = message.content[0].text
    print("성공!")
    print("결과:")
    print("-" * 50)
    print(result)
    
except Exception as e:
    print(f"실패: {e}")