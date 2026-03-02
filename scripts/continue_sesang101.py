#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
continue_sesang101.py - 세상학개론 나머지 73개 영상 분석 계속
기존 batch 1-5 결과에서 처리된 영상 제외하고 나머지 분석
"""

import os
import json
import glob
import time
from datetime import datetime
from typing import Set, List, Dict, Any
import requests

def extract_processed_video_ids() -> Set[str]:
    """기존 batch 결과 파일들에서 처리된 video_id 추출"""
    processed_ids = set()
    
    # 기존 배치 결과 파일들 확인
    batch_files = glob.glob('sesang101_analysis_results_batch_*.json')
    print(f"발견된 배치 파일: {len(batch_files)}개")
    
    for batch_file in batch_files:
        try:
            print(f"읽는 중: {batch_file}")
            with open(batch_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 다양한 구조 지원
            results = data.get('results', [])
            if not results and 'processed' in data:
                results = data['processed']
            
            for result in results:
                video_id = result.get('video_id', '')
                if video_id:
                    processed_ids.add(video_id)
                    
        except Exception as e:
            print(f"에러 읽기 {batch_file}: {e}")
            
    return processed_ids

def get_all_subtitle_files() -> List[str]:
    """모든 자막 파일 목록 가져오기"""
    subtitle_path = '../subs/sesang101/*.json'
    files = glob.glob(subtitle_path)
    print(f"전체 자막 파일: {len(files)}개")
    return files

def extract_video_id_from_filename(filename: str) -> str:
    """파일명에서 video_id 추출"""
    # 파일명 형태: video_id.json
    basename = os.path.basename(filename)
    video_id = basename.replace('.json', '')
    return video_id

def analyze_with_timeout(subtitle_text: str, video_info: Dict) -> Dict:
    """timeout을 300초로 설정한 시그널 분석"""
    
    # 기본 Anthropic API 호출 (실제 구현 필요)
    # 여기서는 더미 응답 반환
    return {
        "video_id": video_info.get("video_id", ""),
        "signals": [],
        "analysis_success": False,
        "error": "분석 로직 구현 필요"
    }

def main():
    print("=== 세상학개론 나머지 73개 영상 분석 시작 ===")
    
    # 1. 처리된 video_id 추출
    processed_ids = extract_processed_video_ids()
    print(f"이미 처리된 영상: {len(processed_ids)}개")
    print(f"처리된 영상들 (처음 5개): {list(processed_ids)[:5]}")
    
    # 2. 전체 자막 파일 목록
    all_subtitle_files = get_all_subtitle_files()
    
    # 3. 미처리 파일들 필터링
    unprocessed_files = []
    for file_path in all_subtitle_files:
        video_id = extract_video_id_from_filename(file_path)
        if video_id not in processed_ids:
            unprocessed_files.append(file_path)
    
    print(f"미처리 파일: {len(unprocessed_files)}개")
    
    if len(unprocessed_files) == 0:
        print("모든 영상이 이미 처리되었습니다!")
        return
    
    # 4. 배치 단위로 처리 (20개씩)
    batch_size = 20
    current_batch = 6  # batch 1-5는 이미 완료
    
    for i in range(0, len(unprocessed_files), batch_size):
        batch_files = unprocessed_files[i:i+batch_size]
        print(f"\n=== Batch {current_batch} 처리 ({len(batch_files)}개) ===")
        
        results = []
        
        for j, file_path in enumerate(batch_files):
            video_id = extract_video_id_from_filename(file_path)
            print(f"[{j+1}/{len(batch_files)}] 처리 중: {video_id}")
            
            try:
                # 자막 파일 읽기
                with open(file_path, 'r', encoding='utf-8') as f:
                    subtitle_data = json.load(f)
                
                # 자막 텍스트 추출
                subtitle_text = ""
                if 'text' in subtitle_data:
                    subtitle_text = subtitle_data['text']
                elif 'captions' in subtitle_data:
                    subtitle_text = " ".join([cap.get('text', '') for cap in subtitle_data['captions']])
                
                if not subtitle_text:
                    print(f"자막 텍스트 없음: {video_id}")
                    results.append({
                        "video_id": video_id,
                        "status": "skipped",
                        "reason": "no_subtitle_text"
                    })
                    continue
                
                # 영상 정보 구성
                video_info = {
                    "video_id": video_id,
                    "title": subtitle_data.get('title', '제목 없음'),
                    "url": f"https://youtube.com/watch?v={video_id}"
                }
                
                print(f"자막 길이: {len(subtitle_text)} 문자")
                
                # 시그널 분석 (timeout 300초)
                analysis_result = analyze_with_timeout(subtitle_text, video_info)
                results.append(analysis_result)
                
                # API 요청 간 5초 대기
                time.sleep(5)
                
            except Exception as e:
                print(f"에러 처리 {video_id}: {e}")
                results.append({
                    "video_id": video_id,
                    "status": "error",
                    "error": str(e)
                })
        
        # 배치 결과 저장
        batch_result = {
            "start_time": datetime.now().isoformat(),
            "batch_number": current_batch,
            "total_files": len(batch_files),
            "results": results
        }
        
        batch_filename = f"sesang101_analysis_results_batch_{current_batch}.json"
        with open(batch_filename, 'w', encoding='utf-8') as f:
            json.dump(batch_result, f, ensure_ascii=False, indent=2)
        
        print(f"Batch {current_batch} 결과 저장: {batch_filename}")
        
        # 20개마다 2분 휴식
        if i + batch_size < len(unprocessed_files):
            print("2분 휴식...")
            time.sleep(120)
        
        current_batch += 1
    
    print("\n=== 모든 배치 처리 완료 ===")

if __name__ == '__main__':
    # 작업 디렉토리를 invest-sns로 변경
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    os.chdir(project_dir)
    print(f"작업 디렉토리: {os.getcwd()}")
    
    main()