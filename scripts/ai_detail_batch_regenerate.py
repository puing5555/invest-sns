#!/usr/bin/env python3
"""
AI Detail 519건 Batch API 재생성 스크립트
Anthropic Message Batches API 사용
"""

import json
import os
from pathlib import Path
import time
from anthropic import Anthropic
import asyncio
from typing import List, Dict, Any

# 설정
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

WORK_DIR = Path("C:/Users/Mario/work/invest-sns")
DATA_DIR = WORK_DIR / "data"
ANALYST_REPORTS_FILE = DATA_DIR / "analyst_reports.json"
PROGRESS_FILE = DATA_DIR / "ai_detail_progress.json"

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

def load_analyst_reports() -> Dict[str, List[Dict]]:
    """애널리스트 리포트 데이터 로드"""
    with open(ANALYST_REPORTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_progress(progress_data: Dict):
    """진행상황 저장"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

def load_progress() -> Dict:
    """진행상황 로드"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"completed": [], "failed": [], "batch_id": None, "status": "not_started"}

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

def create_batch_requests() -> List[Dict]:
    """배치 요청 생성"""
    reports_data = load_analyst_reports()
    requests = []
    
    for ticker, reports in reports_data.items():
        for i, report in enumerate(reports):
            if not report.get('ai_detail'):
                continue
                
            request_id = f"{ticker}_{i}"
            
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
            
            requests.append({
                "custom_id": request_id,
                "method": "POST",
                "url": "/v1/messages",
                "body": {
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            })
    
    return requests

def submit_batch_job() -> str:
    """배치 작업 제출"""
    requests = create_batch_requests()
    print(f"배치 요청 생성 완료: {len(requests)}개")
    
    # 배치 작업 생성 (직접 requests 전달)
    print("배치 작업 생성 중...")
    message_batch = client.beta.message_batches.create(
        requests=requests
    )
    
    batch_id = message_batch.id
    print(f"배치 작업 생성 완료: {batch_id}")
    
    # 진행상황 저장
    progress_data = load_progress()
    progress_data.update({
        "batch_id": batch_id,
        "status": "processing",
        "submitted_at": time.time(),
        "total_requests": len(requests)
    })
    save_progress(progress_data)
    
    return batch_id

def check_batch_status(batch_id: str) -> Dict:
    """배치 작업 상태 확인"""
    try:
        message_batch = client.beta.message_batches.retrieve(batch_id)
        return {
            "id": message_batch.id,
            "status": message_batch.processing_status,
            "request_counts": message_batch.request_counts.__dict__ if message_batch.request_counts else {}
        }
    except Exception as e:
        print(f"배치 상태 확인 실패: {e}")
        return {"status": "error", "error": str(e)}

def download_and_apply_results(batch_id: str) -> None:
    """배치 결과 다운로드 및 적용"""
    try:
        message_batch = client.beta.message_batches.retrieve(batch_id)
        
        if message_batch.processing_status != "ended":
            print(f"배치 작업이 아직 완료되지 않음: {message_batch.processing_status}")
            return
            
        if not message_batch.output_file_id:
            print("출력 파일이 없습니다.")
            return
            
        # 결과 파일 다운로드
        print("결과 파일 다운로드 중...")
        file_response = client.files.content(message_batch.output_file_id)
        
        # 결과 파싱
        results = {}
        for line in file_response.text.strip().split('\n'):
            if line:
                result = json.loads(line)
                custom_id = result.get("custom_id")
                if result.get("response", {}).get("body", {}).get("content"):
                    content = result["response"]["body"]["content"][0]["text"]
                    results[custom_id] = content
                else:
                    print(f"실패한 요청: {custom_id}")
        
        print(f"성공한 결과: {len(results)}개")
        
        # 원본 데이터에 결과 적용
        reports_data = load_analyst_reports()
        updated_count = 0
        
        for ticker, reports in reports_data.items():
            for i, report in enumerate(reports):
                request_id = f"{ticker}_{i}"
                if request_id in results:
                    report['ai_detail'] = results[request_id]
                    updated_count += 1
        
        # 업데이트된 데이터 저장
        output_file = DATA_DIR / "analyst_reports_updated.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(reports_data, f, ensure_ascii=False, indent=2)
        
        print(f"업데이트 완료: {updated_count}개 리포트")
        print(f"저장 위치: {output_file}")
        
        # 진행상황 업데이트
        progress_data = load_progress()
        progress_data.update({
            "status": "completed",
            "completed_at": time.time(),
            "updated_count": updated_count,
            "output_file": str(output_file)
        })
        save_progress(progress_data)
        
    except Exception as e:
        print(f"결과 처리 실패: {e}")

def main():
    """메인 함수"""
    progress = load_progress()
    
    if len(os.sys.argv) < 2:
        print("사용법: python ai_detail_batch_regenerate.py [submit|status|download]")
        return
    
    command = os.sys.argv[1]
    
    if command == "submit":
        batch_id = submit_batch_job()
        print(f"배치 작업 제출 완료: {batch_id}")
        print("상태 확인: python ai_detail_batch_regenerate.py status")
        
    elif command == "status":
        batch_id = progress.get("batch_id")
        if not batch_id:
            print("진행 중인 배치 작업이 없습니다.")
            return
            
        status = check_batch_status(batch_id)
        print(f"배치 ID: {batch_id}")
        print(f"상태: {status.get('status')}")
        if "request_counts" in status:
            counts = status["request_counts"]
            print(f"요청 현황: {counts}")
            
    elif command == "download":
        batch_id = progress.get("batch_id")
        if not batch_id:
            print("진행 중인 배치 작업이 없습니다.")
            return
            
        download_and_apply_results(batch_id)
        
    else:
        print("알 수 없는 명령어:", command)
        print("사용 가능한 명령어: submit, status, download")

if __name__ == "__main__":
    main()