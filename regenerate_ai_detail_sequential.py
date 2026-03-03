#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
애널리스트 AI 상세분석(ai_detail) 519건 재생성 (순차 처리)
안정적인 순차 API 호출로 새로운 형식으로 재생성
"""

import json
import os
from datetime import datetime
from anthropic import Anthropic
import time
import traceback

# Anthropic API 클라이언트 초기화
client = Anthropic()

def load_analyst_data():
    """애널리스트 데이터 로드"""
    data_path = r'C:\Users\Mario\work\invest-sns\data\analyst_reports.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_prompt(report):
    """개별 보고서에 대한 프롬프트 생성"""
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

    # None 값 처리하여 프롬프트 생성
    return prompt_template.format(
        title=report.get('title', '') or '',
        firm=report.get('firm', '') or '',
        analyst=report.get('analyst', '') or '',
        opinion=report.get('opinion', '') or '',
        target_price=report.get('target_price', 0) or 0,
        summary=report.get('summary', '') or '',
        ai_detail=report.get('ai_detail', '') or ''
    )

def generate_ai_detail(report):
    """단일 보고서의 ai_detail 생성"""
    try:
        prompt = create_prompt(report)
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return response.content[0].text
        
    except Exception as e:
        print(f"AI 생성 실패: {e}")
        return None

def save_progress(progress_data):
    """진행상황 저장"""
    progress_path = r'C:\Users\Mario\work\invest-sns\data\ai_detail_progress.json'
    with open(progress_path, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)

def save_updated_data(updated_data):
    """업데이트된 데이터 저장"""
    output_path = r'C:\Users\Mario\work\invest-sns\data\analyst_reports.json'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
    
    print(f"업데이트된 데이터 저장 완료: {output_path}")

def main():
    """메인 실행 함수"""
    print("=== 애널리스트 AI 상세분석(ai_detail) 재생성 시작 (순차 처리) ===")
    start_time = datetime.now()
    print(f"시작 시간: {start_time}")
    
    # 1. 데이터 로드
    print("\n1. 기존 데이터 로딩...")
    original_data = load_analyst_data()
    total_reports = sum(len(reports) for reports in original_data.values())
    print(f"총 {len(original_data)}개 티커, {total_reports}건의 보고서 로드")
    
    # 2. 순차 처리
    print("\n2. AI 상세분석 재생성 시작...")
    updated_data = original_data.copy()
    
    success_count = 0
    error_count = 0
    processed_count = 0
    
    for ticker, reports in updated_data.items():
        print(f"\n처리 중: {ticker} ({len(reports)}건)")
        
        for i, report in enumerate(reports):
            processed_count += 1
            
            try:
                print(f"  {processed_count}/{total_reports} - {report.get('firm', '')} - {report.get('title', '')[:40]}...")
                
                # AI 상세분석 생성
                new_ai_detail = generate_ai_detail(report)
                
                if new_ai_detail:
                    updated_data[ticker][i]['ai_detail'] = new_ai_detail
                    success_count += 1
                    print(f"    [SUCCESS] 성공")
                else:
                    error_count += 1
                    print(f"    [FAIL] 실패")
                
                # 진행상황 저장 (매 10건마다)
                if processed_count % 10 == 0:
                    progress_data = {
                        'status': 'processing',
                        'processed': processed_count,
                        'total': total_reports,
                        'success': success_count,
                        'error': error_count,
                        'current_ticker': ticker,
                        'last_updated': datetime.now().isoformat(),
                        'estimated_time_remaining': None
                    }
                    
                    # 예상 완료 시간 계산
                    if processed_count > 0:
                        elapsed_time = (datetime.now() - start_time).total_seconds()
                        avg_time_per_item = elapsed_time / processed_count
                        remaining_items = total_reports - processed_count
                        estimated_remaining_seconds = remaining_items * avg_time_per_item
                        
                        estimated_completion = datetime.now() + \
                            datetime.timedelta(seconds=estimated_remaining_seconds)
                        progress_data['estimated_completion'] = estimated_completion.isoformat()
                    
                    save_progress(progress_data)
                    
                    # 중간 저장 (매 50건마다)
                    if processed_count % 50 == 0:
                        save_updated_data(updated_data)
                        print(f"    [SAVE] 중간 저장 완료 ({processed_count}/{total_reports})")
                
                # API 호출 제한 고려하여 잠시 대기
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n사용자에 의한 중단...")
                save_updated_data(updated_data)
                return
                
            except Exception as e:
                error_count += 1
                print(f"    [ERROR] 오류: {e}")
                # 오류 발생 시 더 긴 대기
                time.sleep(2)
    
    # 3. 최종 저장
    print("\n3. 최종 데이터 저장...")
    save_updated_data(updated_data)
    
    # 4. 최종 리포트
    end_time = datetime.now()
    elapsed_time = end_time - start_time
    
    print("\n=== 작업 완료 ===")
    print(f"시작 시간: {start_time}")
    print(f"완료 시간: {end_time}")
    print(f"소요 시간: {elapsed_time}")
    print(f"성공: {success_count}건")
    print(f"실패: {error_count}건")
    print(f"총 처리: {processed_count}건")
    
    if processed_count > 0:
        print(f"성공률: {success_count / processed_count * 100:.1f}%")
    
    # 최종 진행상황 저장
    final_progress = {
        'status': 'completed',
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'elapsed_time': str(elapsed_time),
        'processed': processed_count,
        'total': total_reports,
        'success': success_count,
        'error': error_count,
        'success_rate': success_count / processed_count * 100 if processed_count > 0 else 0,
        'completed_at': datetime.now().isoformat()
    }
    save_progress(final_progress)

if __name__ == "__main__":
    main()