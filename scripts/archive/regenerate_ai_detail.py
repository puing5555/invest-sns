#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
애널리스트 AI 상세분석(ai_detail) 519건 재생성
Anthropic Batch API를 사용하여 새로운 형식으로 재생성
"""

import json
import os
from datetime import datetime
from anthropic import Anthropic
import time
import uuid

# Anthropic API 클라이언트 초기화
client = Anthropic()

def load_analyst_data():
    """애널리스트 데이터 로드"""
    data_path = r'C:\Users\Mario\work\invest-sns\data\analyst_reports.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_batch_requests(data):
    """배치 요청 생성"""
    batch_requests = []
    
    # 새로운 형식의 프롬프트 템플릿
    prompt_template = """다음 애널리스트 보고서 정보를 바탕으로 ai_detail을 아래 형식으로 재생성해주세요.

보고서 정보:
- 제목: {title}
- 증권사: {firm}
- 애널리스트: {analyst}
- 투자의견: {opinion}
- 목표가: {target_price:,}원
- 기존 요약: {summary}
- 기존 상세분석: {ai_detail}

출력 형식 (마크다운):
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

규칙:
- 5개 섹션 고정, 순서 고정
- 해당 내용이 없으면 "정보 없음"
- 전체 한글 400~600자
- 기존 정보를 최대한 활용하되 새로운 형식에 맞게 재구성"""

    request_id = 0
    
    for ticker, reports in data.items():
        for report in reports:
            request_id += 1
            
            # None 값 처리하여 프롬프트 생성
            prompt = prompt_template.format(
                title=report.get('title', '') or '',
                firm=report.get('firm', '') or '',
                analyst=report.get('analyst', '') or '',
                opinion=report.get('opinion', '') or '',
                target_price=report.get('target_price', 0) or 0,
                summary=report.get('summary', '') or '',
                ai_detail=report.get('ai_detail', '') or ''
            )
            
            # 배치 요청 생성
            batch_request = {
                "custom_id": f"request_{request_id}_{ticker}_{hash(report.get('title', ''))}",
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
            }
            
            batch_requests.append(batch_request)
            
            # 메타데이터 저장 (나중에 결과 매칭용)
            batch_request['_meta'] = {
                'ticker': ticker,
                'report_index': reports.index(report),
                'title': report.get('title', ''),
                'firm': report.get('firm', '')
            }
    
    return batch_requests

def save_progress(progress_data):
    """진행상황 저장"""
    progress_path = r'C:\Users\Mario\work\invest-sns\data\ai_detail_progress.json'
    with open(progress_path, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

def create_batch_file(batch_requests):
    """배치 파일 생성"""
    batch_file_path = r'C:\Users\Mario\work\invest-sns\data\ai_detail_batch_requests.jsonl'
    
    with open(batch_file_path, 'w', encoding='utf-8') as f:
        for request in batch_requests:
            # 메타데이터 제거 후 저장
            clean_request = {k: v for k, v in request.items() if k != '_meta'}
            f.write(json.dumps(clean_request, ensure_ascii=False) + '\n')
    
    return batch_file_path

def submit_batch(batch_file_path):
    """배치 작업 제출"""
    print("배치 작업을 Anthropic에 제출 중...")
    
    try:
        # 배치 파일 업로드
        with open(batch_file_path, 'rb') as f:
            batch = client.beta.message_batches.create(
                requests_file=f
            )
        
        print(f"배치 ID: {batch.id}")
        print(f"상태: {batch.processing_status}")
        
        return batch
        
    except Exception as e:
        print(f"배치 제출 실패: {e}")
        return None

def monitor_batch(batch_id, batch_requests):
    """배치 진행상황 모니터링"""
    print(f"배치 {batch_id} 진행상황 모니터링 시작...")
    
    while True:
        try:
            batch = client.beta.message_batches.retrieve(batch_id)
            
            progress_data = {
                'batch_id': batch_id,
                'status': batch.processing_status,
                'created_at': str(batch.created_at),
                'expires_at': str(batch.expires_at),
                'request_counts': {
                    'total': batch.request_counts.total,
                    'completed': batch.request_counts.completed,
                    'errored': batch.request_counts.errored,
                    'processing': batch.request_counts.processing
                },
                'last_updated': datetime.now().isoformat(),
                'total_requests': len(batch_requests)
            }
            
            save_progress(progress_data)
            
            print(f"상태: {batch.processing_status}")
            print(f"진행률: {batch.request_counts.completed}/{batch.request_counts.total}")
            
            if batch.processing_status == 'ended':
                print("배치 처리 완료!")
                return batch
            elif batch.processing_status == 'failed':
                print("배치 처리 실패!")
                return batch
            
            # 30초 대기 후 다시 확인
            time.sleep(30)
            
        except Exception as e:
            print(f"배치 상태 확인 실패: {e}")
            time.sleep(60)

def process_batch_results(batch_id, batch_requests, original_data):
    """배치 결과 처리"""
    print("배치 결과를 다운로드하고 처리 중...")
    
    try:
        # 결과 다운로드
        results = client.beta.message_batches.results(batch_id)
        
        # 결과를 딕셔너리로 변환 (custom_id를 키로)
        result_dict = {}
        for result in results:
            result_dict[result.custom_id] = result
        
        # 원본 데이터에 새로운 ai_detail 적용
        updated_data = original_data.copy()
        success_count = 0
        error_count = 0
        
        for request in batch_requests:
            custom_id = request['custom_id']
            meta = request['_meta']
            
            if custom_id in result_dict:
                result = result_dict[custom_id]
                
                if result.result.type == 'succeeded':
                    # 성공한 경우 새로운 ai_detail 적용
                    new_ai_detail = result.result.message.content[0].text
                    
                    ticker = meta['ticker']
                    report_index = meta['report_index']
                    
                    updated_data[ticker][report_index]['ai_detail'] = new_ai_detail
                    success_count += 1
                    
                    print(f"✅ {meta['firm']} - {meta['title'][:30]}...")
                    
                else:
                    # 실패한 경우
                    error_count += 1
                    print(f"❌ 실패: {meta['firm']} - {meta['title'][:30]}...")
            else:
                error_count += 1
                print(f"❌ 결과 없음: {meta['firm']} - {meta['title'][:30]}...")
        
        return updated_data, success_count, error_count
        
    except Exception as e:
        print(f"결과 처리 실패: {e}")
        return original_data, 0, len(batch_requests)

def save_updated_data(updated_data):
    """업데이트된 데이터 저장"""
    output_path = r'C:\Users\Mario\work\invest-sns\data\analyst_reports.json'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
    
    print(f"업데이트된 데이터 저장 완료: {output_path}")

def main():
    """메인 실행 함수"""
    print("=== 애널리스트 AI 상세분석(ai_detail) 재생성 시작 ===")
    print(f"시작 시간: {datetime.now()}")
    
    # 1. 데이터 로드
    print("\n1. 기존 데이터 로딩...")
    original_data = load_analyst_data()
    total_reports = sum(len(reports) for reports in original_data.values())
    print(f"총 {len(original_data)}개 티커, {total_reports}건의 보고서 로드")
    
    # 2. 배치 요청 생성
    print("\n2. 배치 요청 생성...")
    batch_requests = create_batch_requests(original_data)
    print(f"{len(batch_requests)}개의 배치 요청 생성")
    
    # 3. 배치 파일 생성
    print("\n3. 배치 파일 생성...")
    batch_file_path = create_batch_file(batch_requests)
    print(f"배치 파일 생성: {batch_file_path}")
    
    # 4. 배치 제출
    print("\n4. Anthropic Batch API에 제출...")
    batch = submit_batch(batch_file_path)
    
    if not batch:
        print("배치 제출 실패. 종료합니다.")
        return
    
    # 5. 배치 진행상황 모니터링
    print("\n5. 배치 진행상황 모니터링...")
    completed_batch = monitor_batch(batch.id, batch_requests)
    
    if not completed_batch or completed_batch.processing_status != 'ended':
        print("배치 처리가 정상적으로 완료되지 않았습니다.")
        return
    
    # 6. 결과 처리
    print("\n6. 배치 결과 처리...")
    updated_data, success_count, error_count = process_batch_results(
        batch.id, batch_requests, original_data
    )
    
    # 7. 결과 저장
    print("\n7. 업데이트된 데이터 저장...")
    save_updated_data(updated_data)
    
    # 8. 최종 리포트
    print("\n=== 작업 완료 ===")
    print(f"완료 시간: {datetime.now()}")
    print(f"성공: {success_count}건")
    print(f"실패: {error_count}건")
    print(f"총 처리: {success_count + error_count}건")
    print(f"성공률: {success_count / (success_count + error_count) * 100:.1f}%")
    
    # 진행상황 파일 최종 업데이트
    final_progress = {
        'batch_id': batch.id,
        'status': 'completed',
        'completed_at': datetime.now().isoformat(),
        'results': {
            'success': success_count,
            'error': error_count,
            'total': success_count + error_count,
            'success_rate': success_count / (success_count + error_count) * 100
        }
    }
    save_progress(final_progress)

if __name__ == "__main__":
    main()