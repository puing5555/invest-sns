#!/usr/bin/env python3
"""
AI Detail 519�??�순 ?�생???�크립트
?�차 처리 방식 (?�전?�고 ?�실??
"""

import json
import os
from pathlib import Path
import time
from anthropic import Anthropic

# ?�정
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY ?�경변?��? ?�정?��? ?�았?�니??")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

WORK_DIR = Path("C:/Users/Mario/work/invest-sns")
DATA_DIR = WORK_DIR / "data"
ANALYST_REPORTS_FILE = DATA_DIR / "analyst_reports.json"
PROGRESS_FILE = DATA_DIR / "ai_detail_progress.json"

# 기존 ai_detail ?�롬?�트 (백업)
"""
AI_DETAIL_PROMPT_V1 = ?�음?� ?�국 증권?�사?�서 발행???�널리스??리포?�입?�다. 
PDF ?�용??바탕?�로 ?�자?��? ?�한 ?�세 분석??5�??�션?�로 ?�리?�주?�요.

**출력 ?�식 (반드??## 마크?�운 ?�더 ?�용):**

## ?�자?�인??
?�심 ?�자 ?�단�?근거, ????종목?��? (4~5�?

## ?�적?�망  
매출/?�업?�익/?�이???�망 ?�치 ?�함 (1~3�?

## 밸류?�이??
PER/PBR/목표가 근거 (1~2�?

## 리스??
주요 ?�험 ?�인 (1~2�?

## 결론
최종 ?�자?�견 + ?�후 ?�망 ?�약 (2~3�?

**규칙:**
- 5�??�션 고정, ?�서 고정
- PDF???�당 ?�용 ?�으�?"?�보 ?�음"
- ?�체 ?��? 400~600??
- ?�확???�치?� 근거 기반?�로 ?�성

**?�력 ?�이??**
- ?�목: {title}  
- 증권?? {firm}
- 종목: {ticker} ({stock_name})
- 목표가: {target_price}
- ?�자?�견: {opinion}
- 발행?? {published_at}
- 기존 AI ?�약: {existing_detail}

???�보�?바탕?�로 ?�로???�식???�세 분석???�성?�주?�요.
"""

# ?�로??ai_detail ?�롬?�트 v2 - ?�자 중심 ?�맷
AI_DETAIL_PROMPT = """?�음?� ?�국 증권?�사?�서 발행???�널리스??리포?�입?�다. 
PDF ?�용??바탕?�로 ?�자?��? ?�한 ?�세 분석??5�??�션?�로 ?�리?�주?�요.

**출력 ?�식 (반드??## 마크?�운 ?�더 ?�용):**

## ?�자?�인??
??종목?????�야 ?�는지 ?�자 ?�이?�어 중심?�로 ?�성. ?�업 변?? 경쟁 ?�위, ?�장 ?�력 ???�심 ?�리�? ?�적 ?�자???��? 말고 3~4줄로 간결?�게.

## ?�적?�망  
문장 ?�열 금�?. ?�자 ?�이�??�식?�로�??�성.
?�시: 매출 208�?+376% YoY) / ?�업?�익�?40%(+27%p) / 목표가 30만원
깔끔?�게 ?�자�?보이?�록.

## 밸류?�이??
문장 ?�열 금�?. ?�자�??�성.
?�시: PER 12.3x / PBR 1.8x / 목표 PER 15x ??목표가 30만원

## 리스??
?�심 리스??2~3개�? 간결?�게.

## 결론
최종 결론 2~3�? "?�야 ?�는지 말아???�는지" 명확?�게 ?�시.

**규칙:**
- 5�??�션 고정, ?�서 고정
- PDF???�당 ?�용 ?�으�?"?�보 ?�음"
- ?�체 ?��? 300~500??
- ?�확???�치?� 근거 기반?�로 ?�성

**?�력 ?�이??**
- ?�목: {title}  
- 증권?? {firm}
- 종목: {ticker} ({stock_name})
- 목표가: {target_price}
- ?�자?�견: {opinion}
- 발행?? {published_at}
- 기존 AI ?�약: {existing_detail}

???�보�?바탕?�로 ?�로???�식???�세 분석???�성?�주?�요."""

def load_analyst_reports():
    """?�널리스??리포???�이??로드"""
    with open(ANALYST_REPORTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_progress(progress_data):
    """진행?�황 ?�??""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

def load_progress():
    """진행?�황 로드"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"completed": [], "failed": [], "current": 0, "total": 0}

def get_stock_name(ticker: str) -> str:
    """종목 코드?�서 종목�?가?�오�?""
    ticker_names = {
        '240810': '?�익QnC', '284620': '카이', '298040': '?�성중공??, 
        '352820': '?�이�?, '403870': 'HPSP', '090430': '?�모?�퍼?�픽',
        '000660': 'SK?�이?�스', '079160': 'CJ CGV', '005380': '?��??�동�?,
        '005930': '?�성?�자', '036930': '주성?��??�어�?, '042700': '?��?반도�?, 
        '006400': '?�성SDI', '000720': '?��?건설', '005940': 'NH?�자증권',
        '016360': '?�성증권', '039490': '?��?증권', '051910': 'LG?�학',
        '036570': '?�씨?�프??, '071050': '?�국금융지�?
    }
    return ticker_names.get(ticker, ticker)

def regenerate_single_report(ticker: str, report_index: int, report: dict) -> str:
    """?�일 리포??ai_detail ?�생??""
    if not report.get('ai_detail'):
        return None
        
    # 목표가 ?�맷??
    target_price_str = f"{report.get('target_price', 0):,}?? if report.get('target_price') else "미제??
    
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
            model="claude-sonnet-4-6"  # pipeline_config ����,
            max_tokens=1000,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return message.content[0].text
        
    except Exception as e:
        print(f"?�패: {ticker}_{report_index} - {e}")
        return None

def main():
    """메인 처리 ?�수"""
    print("AI Detail 519�??�생???�작")
    
    # ?�이??로드
    reports_data = load_analyst_reports()
    progress = load_progress()
    
    # ?�체 리포??목록 ?�성
    all_reports = []
    for ticker, reports in reports_data.items():
        for i, report in enumerate(reports):
            if report.get('ai_detail'):
                all_reports.append((ticker, i, report))
    
    total_reports = len(all_reports)
    progress['total'] = total_reports
    print(f"�?{total_reports}�?리포??처리 ?�정")
    
    # 진행?�황?�서 ?�재 ?�치 가?�오�?
    current_index = progress.get('current', 0)
    completed = progress.get('completed', [])
    failed = progress.get('failed', [])
    
    # 처리 ?�작
    for idx in range(current_index, total_reports):
        ticker, report_index, report = all_reports[idx]
        report_id = f"{ticker}_{report_index}"
        
        if report_id in completed:
            print(f"건너?�기 (?�료??: {report_id}")
            continue
            
        print(f"처리�?[{idx+1}/{total_reports}]: {report_id} - {report.get('title', '')[:30]}...")
        
        # ?�생??
        new_ai_detail = regenerate_single_report(ticker, report_index, report)
        
        if new_ai_detail:
            # ?�본 ?�이?�에 ?�데?�트
            reports_data[ticker][report_index]['ai_detail'] = new_ai_detail
            completed.append(report_id)
            print(f"?�공: {report_id}")
        else:
            failed.append(report_id)
            print(f"?�패: {report_id}")
        
        # 진행?�황 ?�??(10개마??
        if (idx + 1) % 10 == 0:
            progress.update({
                'current': idx + 1,
                'completed': completed,
                'failed': failed
            })
            save_progress(progress)
            
            # 중간 백업 ?�??
            backup_file = DATA_DIR / f"analyst_reports_backup_{idx+1}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(reports_data, f, ensure_ascii=False, indent=2)
            
            print(f"진행?�황 ?�?? {len(completed)}�??�료, {len(failed)}�??�패")
        
        # Rate limit 방�? (2�??��?
        time.sleep(2)
    
    # 최종 결과 ?�??
    output_file = DATA_DIR / "analyst_reports_regenerated.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reports_data, f, ensure_ascii=False, indent=2)
    
    # 진행?�황 ?�료 처리
    progress.update({
        'current': total_reports,
        'completed': completed,
        'failed': failed,
        'status': 'completed',
        'output_file': str(output_file)
    })
    save_progress(progress)
    
    print(f"\n?�생???�료!")
    print(f"�?처리: {total_reports}�?)
    print(f"?�공: {len(completed)}�?)
    print(f"?�패: {len(failed)}�?)
    print(f"출력 ?�일: {output_file}")

if __name__ == "__main__":
    main()