#!/usr/bin/env python3
"""
AI Detail 519건 전체 재생성 스크립트 (최종 버전)
"""

import json
import os
from pathlib import Path
import time
from anthropic import Anthropic

print("AI Detail 519건 재생성 시작")

# 설정
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=ANTHROPIC_API_KEY)

WORK_DIR = Path("C:/Users/Mario/work/invest-sns")
DATA_DIR = WORK_DIR / "data"
ANALYST_REPORTS_FILE = DATA_DIR / "analyst_reports.json"
PROGRESS_FILE = DATA_DIR / "ai_detail_progress.json"

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

def save_progress(progress_data):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"completed": [], "failed": [], "current": 0, "total": 0}

def get_stock_name(ticker: str) -> str:
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

# 데이터 로드
with open(ANALYST_REPORTS_FILE, 'r', encoding='utf-8') as f:
    reports_data = json.load(f)

progress = load_progress()

# 전체 리포트 목록 생성
all_reports = []
for ticker, reports in reports_data.items():
    for i, report in enumerate(reports):
        if report.get('ai_detail'):
            all_reports.append((ticker, i, report))

total_reports = len(all_reports)
progress['total'] = total_reports

print(f"총 {total_reports}개 리포트 처리 예정")

# 진행상황
current_index = progress.get('current', 0)
completed = progress.get('completed', [])
failed = progress.get('failed', [])

print(f"현재 진행: {current_index}/{total_reports}")
print("처리 시작")

# 처리 시작
for idx in range(current_index, total_reports):
    ticker, report_index, report = all_reports[idx]
    report_id = f"{ticker}_{report_index}"
    
    if report_id in completed:
        print(f"SKIP: {report_id}")
        continue
        
    print(f"[{idx+1}/{total_reports}] {report_id}")
    
    # 프롬프트 생성
    target_price_str = f"{report.get('target_price', 0):,}원" if report.get('target_price') else "미제시"
    
    prompt = AI_DETAIL_PROMPT.format(
        title=report.get('title', ''),
        firm=report.get('firm', ''),
        ticker=ticker,
        stock_name=get_stock_name(ticker),
        target_price=target_price_str,
        opinion=report.get('opinion', ''),
        published_at=report.get('published_at', ''),
        existing_detail=report.get('ai_detail', '')[:1000] + "..." if len(report.get('ai_detail', '')) > 1000 else report.get('ai_detail', '')
    )
    
    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        new_ai_detail = message.content[0].text
        reports_data[ticker][report_index]['ai_detail'] = new_ai_detail
        completed.append(report_id)
        print(f"OK: {report_id}")
        
    except Exception as e:
        failed.append(report_id)
        print(f"FAIL: {report_id} - {str(e)}")
    
    # 진행상황 저장 (10개마다)
    if (idx + 1) % 10 == 0:
        progress.update({
            'current': idx + 1,
            'completed': completed,
            'failed': failed
        })
        save_progress(progress)
        
        backup_file = DATA_DIR / f"analyst_reports_backup_{idx+1}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(reports_data, f, ensure_ascii=False, indent=2)
        
        print(f"SAVE: {len(completed)}개 완료, {len(failed)}개 실패")
    
    # 50건마다 보고
    if (idx + 1) % 50 == 0:
        progress_percent = (idx+1)/total_reports*100
        remaining_minutes = (total_reports - idx - 1) * 2 / 60
        print(f"=== 50건 단위 보고 ===")
        print(f"진행: {idx+1}/{total_reports} ({progress_percent:.1f}%)")
        print(f"완료: {len(completed)}건")
        print(f"실패: {len(failed)}건") 
        print(f"예상 완료: 약 {remaining_minutes:.0f}분 후")
        print("===================")
    
    time.sleep(2)

# 최종 저장
output_file = DATA_DIR / "analyst_reports_regenerated.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(reports_data, f, ensure_ascii=False, indent=2)

progress.update({
    'current': total_reports,
    'completed': completed,
    'failed': failed,
    'status': 'completed',
    'output_file': str(output_file)
})
save_progress(progress)

print("=== 최종 결과 ===")
print(f"총 처리: {total_reports}개")
print(f"성공: {len(completed)}개")
print(f"실패: {len(failed)}개")
print("================")