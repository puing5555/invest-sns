#!/usr/bin/env python3
"""
AI Detail 519건 단순 재생성 스크립트
순차 처리 방식 (안전하고 확실함)
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
PROGRESS_FILE = DATA_DIR / "ai_detail_progress.json"

# 기존 ai_detail 프롬프트 (백업)
"""
AI_DETAIL_PROMPT_V1 = 다음은 한국 증권회사에서 발행한 애널리스트 리포트입니다. 
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

위 정보를 바탕으로 새로운 형식의 상세 분석을 작성해주세요.
"""

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

def load_analyst_reports():
    """애널리스트 리포트 데이터 로드"""
    with open(ANALYST_REPORTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_progress(progress_data):
    """진행상황 저장"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

def load_progress():
    """진행상황 로드"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"completed": [], "failed": [], "current": 0, "total": 0}

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

def regenerate_single_report(ticker: str, report_index: int, report: dict) -> str:
    """단일 리포트 ai_detail 재생성"""
    if not report.get('ai_detail'):
        return None
        
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
        existing_detail=report.get('ai_detail', '')[:1000] + "..." if len(report.get('ai_detail', '')) > 1000 else report.get('ai_detail', '')
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
        
        return message.content[0].text
        
    except Exception as e:
        print(f"실패: {ticker}_{report_index} - {e}")
        return None

def main():
    """메인 처리 함수"""
    print("AI Detail 519건 재생성 시작")
    
    # 데이터 로드
    reports_data = load_analyst_reports()
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
    
    # 진행상황에서 현재 위치 가져오기
    current_index = progress.get('current', 0)
    completed = progress.get('completed', [])
    failed = progress.get('failed', [])
    
    # 처리 시작
    for idx in range(current_index, total_reports):
        ticker, report_index, report = all_reports[idx]
        report_id = f"{ticker}_{report_index}"
        
        if report_id in completed:
            print(f"건너뛰기 (완료됨): {report_id}")
            continue
            
        print(f"처리중 [{idx+1}/{total_reports}]: {report_id} - {report.get('title', '')[:30]}...")
        
        # 재생성
        new_ai_detail = regenerate_single_report(ticker, report_index, report)
        
        if new_ai_detail:
            # 원본 데이터에 업데이트
            reports_data[ticker][report_index]['ai_detail'] = new_ai_detail
            completed.append(report_id)
            print(f"성공: {report_id}")
        else:
            failed.append(report_id)
            print(f"실패: {report_id}")
        
        # 진행상황 저장 (10개마다)
        if (idx + 1) % 10 == 0:
            progress.update({
                'current': idx + 1,
                'completed': completed,
                'failed': failed
            })
            save_progress(progress)
            
            # 중간 백업 저장
            backup_file = DATA_DIR / f"analyst_reports_backup_{idx+1}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(reports_data, f, ensure_ascii=False, indent=2)
            
            print(f"진행상황 저장: {len(completed)}개 완료, {len(failed)}개 실패")
        
        # Rate limit 방지 (2초 대기)
        time.sleep(2)
    
    # 최종 결과 저장
    output_file = DATA_DIR / "analyst_reports_regenerated.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reports_data, f, ensure_ascii=False, indent=2)
    
    # 진행상황 완료 처리
    progress.update({
        'current': total_reports,
        'completed': completed,
        'failed': failed,
        'status': 'completed',
        'output_file': str(output_file)
    })
    save_progress(progress)
    
    print(f"\n재생성 완료!")
    print(f"총 처리: {total_reports}개")
    print(f"성공: {len(completed)}개")
    print(f"실패: {len(failed)}개")
    print(f"출력 파일: {output_file}")

if __name__ == "__main__":
    main()