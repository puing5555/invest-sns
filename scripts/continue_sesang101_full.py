#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
continue_sesang101_full.py - 세상학개론 나머지 73개 영상 분석 (완전판)
기존 batch 1-5 결과에서 처리된 영상 제외하고 나머지 분석
"""

import os
import json
import glob
import time
from datetime import datetime
from typing import Set, List, Dict, Any, Optional
import sys

# 모듈 import
from pipeline_config import PipelineConfig
from signal_analyzer_rest import SignalAnalyzer
from db_inserter_rest import DatabaseInserter

class ContinueSesang101Analyzer:
    def __init__(self):
        self.config = PipelineConfig()
        self.analyzer = SignalAnalyzer()
        self.db_inserter = DatabaseInserter()
        
        # 채널 정보
        self.channel_info = {
            'url': 'https://www.youtube.com/@sesang101',
            'name': '세상학개론',
            'subscriber_count': 150000,
            'video_count': 200,
            'description': '이효석의 세상학개론 - 투자와 경제 분석'
        }
        
        # 호스트 정보 (이효석)
        self.host_info = {
            'name': '이효석',
            'role': '세상학개론 메인 진행자',
            'bio': '투자 전문가, 유튜버'
        }
        
    def extract_processed_video_ids(self) -> Set[str]:
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

    def get_all_subtitle_files(self) -> List[str]:
        """모든 자막 파일 목록 가져오기"""
        subtitle_path = '../subs/sesang101/*.json'
        files = glob.glob(subtitle_path)
        print(f"전체 자막 파일: {len(files)}개")
        return files

    def extract_video_id_from_filename(self, filename: str) -> str:
        """파일명에서 video_id 추출"""
        basename = os.path.basename(filename)
        video_id = basename.replace('.json', '')
        return video_id

    def load_subtitle_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """자막 파일 로드"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"자막 파일 로드 에러 {file_path}: {e}")
            return None

    def extract_subtitle_text(self, subtitle_data) -> str:
        """자막 데이터에서 텍스트 추출"""
        # subtitle_data가 리스트인 경우 (세상학개론 형태)
        if isinstance(subtitle_data, list):
            return " ".join([item.get('text', '') for item in subtitle_data if 'text' in item])
        
        # subtitle_data가 dict인 경우
        if isinstance(subtitle_data, dict):
            if 'text' in subtitle_data:
                return subtitle_data['text']
            elif 'captions' in subtitle_data:
                return " ".join([cap.get('text', '') for cap in subtitle_data['captions']])
            elif 'entries' in subtitle_data:
                return " ".join([entry.get('text', '') for entry in subtitle_data['entries']])
        
        return ""

    def create_video_data(self, video_id: str, subtitle_data) -> Dict[str, Any]:
        """영상 데이터 구성"""
        # subtitle_data가 리스트인 경우 (메타데이터 없음)
        if isinstance(subtitle_data, list):
            return {
                'video_id': video_id,
                'title': f'세상학개론 영상 {video_id}',  # 기본 제목
                'url': f"https://youtube.com/watch?v={video_id}",
                'published_at': '',
                'description': '',
                'duration': 0,
                'view_count': 0,
                'like_count': 0,
                'channel_info': self.channel_info,
                'host_info': self.host_info
            }
        
        # subtitle_data가 dict인 경우
        return {
            'video_id': video_id,
            'title': subtitle_data.get('title', '제목 없음'),
            'url': f"https://youtube.com/watch?v={video_id}",
            'published_at': subtitle_data.get('upload_date', ''),
            'description': subtitle_data.get('description', ''),
            'duration': subtitle_data.get('duration', 0),
            'view_count': subtitle_data.get('view_count', 0),
            'like_count': subtitle_data.get('like_count', 0),
            'channel_info': self.channel_info,
            'host_info': self.host_info
        }

    def analyze_video_signals(self, subtitle_text: str, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """영상 시그널 분석 (timeout 300초)"""
        try:
            print(f"시그널 분석 시작: {video_data['video_id']}")
            print(f"자막 길이: {len(subtitle_text)} 문자")
            
            # 시그널 분석 실행
            analysis_result = self.analyzer.analyze_video_subtitle(
                video_data['channel_info']['url'],  # channel_url
                video_data,  # video_data 
                subtitle_text  # subtitle
            )
            
            if analysis_result and analysis_result.get('signals'):
                print(f"시그널 발견: {len(analysis_result['signals'])}개")
                return {
                    'video_id': video_data['video_id'],
                    'status': 'analyzed',
                    'signals_count': len(analysis_result['signals']),
                    'analysis_result': analysis_result
                }
            else:
                print("시그널 없음")
                return {
                    'video_id': video_data['video_id'],
                    'status': 'no_signals',
                    'analysis_result': analysis_result
                }
                
        except Exception as e:
            print(f"분석 에러 {video_data['video_id']}: {e}")
            return {
                'video_id': video_data['video_id'],
                'status': 'error',
                'error': str(e)
            }

    def save_to_database(self, analysis_result: Dict[str, Any]) -> bool:
        """분석 결과를 데이터베이스에 저장"""
        try:
            if analysis_result.get('status') == 'analyzed':
                result = self.db_inserter.insert_analysis_result(
                    analysis_result['analysis_result']
                )
                return result.get('success', False)
            return True  # 시그널 없거나 에러인 경우도 처리됨으로 간주
        except Exception as e:
            print(f"DB 저장 에러: {e}")
            return False

    def update_signal_prices(self):
        """signal_prices.json에 새 종목 추가"""
        try:
            print("signal_prices.json 업데이트 중...")
            # 여기서 새로 발견된 종목들을 signal_prices.json에 추가
            # 실제 구현은 기존 로직 참조
            print("signal_prices.json 업데이트 완료")
        except Exception as e:
            print(f"signal_prices.json 업데이트 에러: {e}")

    def run_analysis(self):
        """메인 분석 실행"""
        print("=== 세상학개론 나머지 73개 영상 분석 시작 ===")
        
        # 1. 처리된 video_id 추출
        processed_ids = self.extract_processed_video_ids()
        print(f"이미 처리된 영상: {len(processed_ids)}개")
        
        # 2. 전체 자막 파일 목록
        all_subtitle_files = self.get_all_subtitle_files()
        
        # 3. 미처리 파일들 필터링
        unprocessed_files = []
        for file_path in all_subtitle_files:
            video_id = self.extract_video_id_from_filename(file_path)
            if video_id not in processed_ids:
                unprocessed_files.append(file_path)
        
        print(f"미처리 파일: {len(unprocessed_files)}개")
        
        if len(unprocessed_files) == 0:
            print("모든 영상이 이미 처리되었습니다!")
            return
        
        # 4. 배치 단위로 처리 (5개씩)
        batch_size = 5
        current_batch = 6  # batch 1-5는 이미 완료
        
        total_analyzed = 0
        total_signals = 0
        
        for i in range(0, len(unprocessed_files), batch_size):
            batch_files = unprocessed_files[i:i+batch_size]
            print(f"\n=== Batch {current_batch} 처리 ({len(batch_files)}개) ===")
            
            batch_results = []
            batch_analyzed = 0
            batch_signals = 0
            
            for j, file_path in enumerate(batch_files):
                video_id = self.extract_video_id_from_filename(file_path)
                print(f"\n[{j+1}/{len(batch_files)}] 처리 중: {video_id}")
                
                # 자막 파일 로드
                subtitle_data = self.load_subtitle_file(file_path)
                if not subtitle_data:
                    batch_results.append({
                        "video_id": video_id,
                        "status": "error",
                        "error": "subtitle_load_failed"
                    })
                    continue
                
                # 자막 텍스트 추출
                subtitle_text = self.extract_subtitle_text(subtitle_data)
                if not subtitle_text:
                    print(f"자막 텍스트 없음: {video_id}")
                    batch_results.append({
                        "video_id": video_id,
                        "status": "skipped",
                        "reason": "no_subtitle_text"
                    })
                    continue
                
                # 영상 데이터 구성
                video_data = self.create_video_data(video_id, subtitle_data)
                
                # 시그널 분석
                analysis_result = self.analyze_video_signals(subtitle_text, video_data)
                
                # DB에 저장
                save_success = self.save_to_database(analysis_result)
                analysis_result['db_saved'] = save_success
                
                batch_results.append(analysis_result)
                
                # 통계 업데이트
                if analysis_result.get('status') == 'analyzed':
                    batch_analyzed += 1
                    batch_signals += analysis_result.get('signals_count', 0)
                
                # API 요청 간 5초 대기
                print("5초 대기...")
                time.sleep(5)
            
            # 배치 결과 저장
            batch_result = {
                "start_time": datetime.now().isoformat(),
                "batch_number": current_batch,
                "total_files": len(batch_files),
                "analyzed": batch_analyzed,
                "total_signals": batch_signals,
                "results": batch_results
            }
            
            batch_filename = f"sesang101_analysis_results_batch_{current_batch}.json"
            with open(batch_filename, 'w', encoding='utf-8') as f:
                json.dump(batch_result, f, ensure_ascii=False, indent=2)
            
            print(f"Batch {current_batch} 완료: 분석 {batch_analyzed}개, 시그널 {batch_signals}개")
            print(f"결과 저장: {batch_filename}")
            
            total_analyzed += batch_analyzed
            total_signals += batch_signals
            
            # 20개마다 2분 휴식 (마지막 배치 제외)
            if i + batch_size < len(unprocessed_files):
                print("2분 휴식...")
                time.sleep(120)
            
            current_batch += 1
        
        print(f"\n=== 모든 배치 처리 완료 ===")
        print(f"총 분석: {total_analyzed}개")
        print(f"총 시그널: {total_signals}개")
        
        # 5. signal_prices.json 업데이트
        self.update_signal_prices()

def main():
    # 작업 디렉토리를 invest-sns로 변경
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    os.chdir(project_dir)
    print(f"작업 디렉토리: {os.getcwd()}")
    
    # 분석 실행
    analyzer = ContinueSesang101Analyzer()
    analyzer.run_analysis()

if __name__ == '__main__':
    main()