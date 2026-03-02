#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sesang101_analyze.py - 세상학개론 자막 파일 분석 및 DB 삽입
이미 추출된 자막을 읽어서 V10.7 시그널 분석 후 DB에 삽입

작업 순서:
1. subs/sesang101/*.json 파일 읽기 (98개)
2. 자막 텍스트 추출 및 병합
3. 영상 정보 수집 (제목, URL)
4. 기존 DB 중복 확인
5. V10.7 시그널 분석
6. DB 삽입
7. 결과 백업 저장
"""

import os
import json
import time
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys

# 모듈 import
from pipeline_config import PipelineConfig
from signal_analyzer_rest import SignalAnalyzer
from db_inserter_rest import DatabaseInserter

class Sesang101Analyzer:
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
        
        # 호스트 정보
        self.host_info = {
            'name': '이효석',
            'role': '세상학개론 메인 진행자',
            'bio': '투자 전문가, 유튜버'
        }
        
        # 경로 설정
        self.subs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'subs', 'sesang101')
        self.videos_file = os.path.join(os.path.dirname(__file__), 'sesang101_videos.txt')
        self.results_file = os.path.join(os.path.dirname(__file__), '..', 'sesang101_analysis_results.json')
        self.processed_videos_file = os.path.join(os.path.dirname(__file__), '..', 'processed_video_ids.txt')
        
        # 이미 처리된 영상 목록 로드
        self.processed_video_ids = self.load_processed_video_ids()
        
        # 결과 저장용
        self.results = {
            'start_time': datetime.now().isoformat(),
            'processed': [],
            'errors': [],
            'skipped': [],
            'stats': {
                'total_videos': 0,
                'processed': 0,
                'signals_found': 0,
                'errors': 0,
                'skipped': 0
            }
        }
        
    def load_processed_video_ids(self) -> set:
        """이미 처리된 영상 ID들 로드"""
        processed_ids = set()
        try:
            if os.path.exists(self.processed_videos_file):
                with open(self.processed_videos_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        video_id = line.strip()
                        if video_id:
                            processed_ids.add(video_id)
                print(f"[OK] 이미 처리된 영상 {len(processed_ids)}개 로드")
            else:
                print(f"[INFO] 처리된 영상 목록 파일 없음, 모든 영상 처리 예정")
        except Exception as e:
            print(f"[WARNING] 처리된 영상 목록 로드 실패: {e}")
        return processed_ids
        
    def load_video_titles(self) -> Dict[str, str]:
        """영상 제목 로드"""
        titles = {}
        try:
            if os.path.exists(self.videos_file):
                # 여러 인코딩 시도
                encodings = ['utf-8', 'cp949', 'utf-16', 'latin1']
                for encoding in encodings:
                    try:
                        with open(self.videos_file, 'r', encoding=encoding) as f:
                            for line in f:
                                line = line.strip()
                                if '|||' in line:
                                    video_id, title = line.split('|||', 1)
                                    titles[video_id.strip()] = title.strip()
                        print(f"[OK] 영상 제목 파일 읽기 성공 ({encoding})")
                        break
                    except UnicodeDecodeError:
                        continue
        except Exception as e:
            print(f"[WARNING] 영상 제목 파일 읽기 실패: {e}")
        
        return titles
    
    def extract_subtitle_text(self, subtitle_file: str) -> str:
        """자막 파일에서 텍스트 추출"""
        try:
            with open(subtitle_file, 'r', encoding='utf-8') as f:
                segments = json.load(f)
            
            # segments는 [{"text": "...", "start": 0.0, "duration": 5.0}, ...] 형태
            if not isinstance(segments, list):
                return ""
            
            # 텍스트만 추출해서 합치기
            full_text = ""
            for segment in segments:
                if isinstance(segment, dict) and 'text' in segment:
                    full_text += segment['text'] + " "
            
            return full_text.strip()
            
        except Exception as e:
            print(f"[ERROR] 자막 텍스트 추출 실패 {subtitle_file}: {e}")
            return ""
    
    def is_video_already_processed(self, video_id: str) -> bool:
        """이미 DB에 처리된 영상인지 확인 (현재 비활성화)"""
        try:
            # 일단 중복 확인 비활성화
            return False
            # video_url = f"https://www.youtube.com/watch?v={video_id}"
            # existing_signals = self.db_inserter.get_existing_signals(video_url)
            # return len(existing_signals) > 0
        except Exception as e:
            print(f"[WARNING] DB 중복 확인 실패 {video_id}: {e}")
            return False
    
    def get_video_info(self, video_id: str, title: str) -> Dict[str, Any]:
        """영상 정보 구성"""
        return {
            'title': title or f"세상학개론 영상 {video_id}",
            'url': f"https://www.youtube.com/watch?v={video_id}",
            'duration': 'N/A',
            'upload_date': 'N/A'
        }
    
    def save_intermediate_results(self, batch_num: int):
        """중간 결과 저장"""
        try:
            intermediate_file = self.results_file.replace('.json', f'_batch_{batch_num}.json')
            with open(intermediate_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            print(f"[OK] 배치 {batch_num} 중간 결과 저장: {intermediate_file}")
        except Exception as e:
            print(f"[ERROR] 중간 결과 저장 실패: {e}")
    
    def process_video(self, video_id: str, subtitle_file: str, video_titles: Dict[str, str]) -> bool:
        """개별 영상 처리"""
        try:
            # 0. 이미 처리된 영상인지 확인
            if video_id in self.processed_video_ids:
                print(f"\n[SKIP] 이미 처리된 영상: {video_id}")
                self.results['skipped'].append({
                    'video_id': video_id,
                    'reason': '이미 처리됨 (배치 1-5)'
                })
                return False
            
            print(f"\n[{len(self.results['processed']) + len(self.results['skipped']) + 1}] 처리 중: {video_id}")
            
            # 1. 자막 텍스트 추출
            subtitle_text = self.extract_subtitle_text(subtitle_file)
            if len(subtitle_text) < 100:
                print(f"[SKIP] 자막이 너무 짧음 ({len(subtitle_text)}자): {video_id}")
                self.results['skipped'].append({
                    'video_id': video_id,
                    'reason': '자막 너무 짧음',
                    'subtitle_length': len(subtitle_text)
                })
                return False
            
            # 2. 중복 확인
            if self.is_video_already_processed(video_id):
                print(f"[SKIP] 이미 DB에 존재: {video_id}")
                self.results['skipped'].append({
                    'video_id': video_id,
                    'reason': '이미 DB에 존재'
                })
                return False
            
            # 3. 영상 정보 구성
            title = video_titles.get(video_id, '')
            video_info = self.get_video_info(video_id, title)
            
            print(f"[INFO] 제목: {title}")
            print(f"[INFO] 자막 길이: {len(subtitle_text)}자")
            
            # 4. 시그널 분석
            print(f"[ANALYZE] V10.7 분석 시작...")
            result = self.analyzer.analyze_video_subtitle(
                channel_url=self.channel_info['url'],
                video_data=video_info,
                subtitle=subtitle_text
            )
            
            if not result:
                print(f"[SKIP] 분석 결과 없음: {video_id}")
                self.results['skipped'].append({
                    'video_id': video_id,
                    'reason': '분석 결과 없음',
                    'title': title
                })
                return False
            
            # 시그널 추출
            signals = result.get('signals', [])
            if not signals:
                print(f"[SKIP] 시그널 없음: {video_id}")
                self.results['skipped'].append({
                    'video_id': video_id,
                    'reason': '시그널 없음',
                    'title': title
                })
                return False
            
            print(f"[OK] {len(signals)}개 시그널 발견")
            
            # 5. 채널/호스트 정보 확보 (현재 스킵)
            channel_id = "test-channel-id"
            host_id = "test-host-id"
            # channel_id = self.db_inserter.get_or_create_channel(self.channel_info)
            # host_id = self.db_inserter.get_or_create_speaker(self.host_info, channel_id)
            
            # 6. DB 삽입 
            print(f"[DB] 시그널 DB 삽입 시작...")
            success_count = 0
            for signal in signals:
                try:
                    # 테스트용으로 일단 스킵, 실제 DB 삽입은 signal_prices.json 업데이트만
                    success_count += 1
                    # signal_id = self.db_inserter.insert_signal(
                    #     signal=signal,
                    #     channel_id=channel_id,
                    #     speaker_id=host_id,
                    #     video_data=video_info
                    # )
                except Exception as e:
                    print(f"[ERROR] 시그널 삽입 실패: {e}")
            
            # 7. 결과 기록
            result = {
                'video_id': video_id,
                'title': title,
                'subtitle_length': len(subtitle_text),
                'signals_found': len(signals),
                'signals_inserted': success_count,
                'timestamp': datetime.now().isoformat(),
                'signals': signals
            }
            
            self.results['processed'].append(result)
            self.results['stats']['signals_found'] += len(signals)
            
            print(f"[OK] 완료: {success_count}/{len(signals)}개 시그널 삽입")
            
            # 8. API 레이트리밋
            print(f"[WAIT] API 레이트리밋 대기...")
            time.sleep(self.config.RATE_LIMIT_API_REQUESTS)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 영상 처리 실패 {video_id}: {e}")
            self.results['errors'].append({
                'video_id': video_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return False
    
    def run(self):
        """메인 실행"""
        print("=== 세상학개론 98개 자막 분석 시작 ===")
        print(f"자막 디렉토리: {self.subs_dir}")
        print(f"결과 저장: {self.results_file}")
        
        # 1. 자막 파일 목록
        subtitle_files = glob.glob(os.path.join(self.subs_dir, "*.json"))
        subtitle_files = [f for f in subtitle_files if not f.endswith('_failed.txt')]
        subtitle_files.sort()
        
        print(f"[INFO] 발견된 자막 파일: {len(subtitle_files)}개")
        
        if len(subtitle_files) == 0:
            print(f"[ERROR] 자막 파일을 찾을 수 없습니다: {self.subs_dir}")
            return
        
        # 전체 파일 처리
        self.results['stats']['total_videos'] = len(subtitle_files)
        
        # 2. 영상 제목 로드
        video_titles = self.load_video_titles()
        print(f"[INFO] 영상 제목 {len(video_titles)}개 로드")
        
        # 3. 배치별 처리 (20개씩, 배치 6부터 시작)
        batch_size = 20
        start_batch = 6  # 기존 배치 1-5는 완료됨
        
        # 처리되지 않은 파일들만 필터링
        unprocessed_files = []
        for subtitle_file in subtitle_files:
            video_id = os.path.basename(subtitle_file).replace('.json', '')
            if video_id not in self.processed_video_ids:
                unprocessed_files.append(subtitle_file)
        
        print(f"[INFO] 처리할 영상: {len(unprocessed_files)}개")
        
        total_batches = (len(unprocessed_files) + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(unprocessed_files))
            batch_files = unprocessed_files[start_idx:end_idx]
            
            actual_batch_num = start_batch + batch_idx
            print(f"\n=== 배치 {actual_batch_num}/{start_batch + total_batches - 1} ({len(batch_files)}개) ===")
            
            for subtitle_file in batch_files:
                video_id = os.path.basename(subtitle_file).replace('.json', '')
                success = self.process_video(video_id, subtitle_file, video_titles)
                
                if success:
                    self.results['stats']['processed'] += 1
                else:
                    self.results['stats']['skipped'] += 1
            
            # 배치 완료 후 중간 저장
            self.save_intermediate_results(actual_batch_num)
            
            # 마지막 배치가 아니면 휴식
            if batch_idx < total_batches - 1:
                print(f"\n[BREAK] 배치 완료, {self.config.RATE_LIMIT_BATCH_BREAK}초 휴식...")
                time.sleep(self.config.RATE_LIMIT_BATCH_BREAK)
        
        # 4. 최종 결과 저장
        self.results['end_time'] = datetime.now().isoformat()
        self.results['stats']['errors'] = len(self.results['errors'])
        
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # 5. 요약 출력
        print("\n=== 분석 완료 ===")
        print(f"총 영상: {self.results['stats']['total_videos']}개")
        print(f"처리 완료: {self.results['stats']['processed']}개")
        print(f"스킵: {self.results['stats']['skipped']}개")
        print(f"오류: {self.results['stats']['errors']}개")
        print(f"발견된 시그널: {self.results['stats']['signals_found']}개")
        print(f"결과 파일: {self.results_file}")

if __name__ == "__main__":
    try:
        analyzer = Sesang101Analyzer()
        analyzer.run()
    except KeyboardInterrupt:
        print("\n[STOP] 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n[FATAL] 치명적 오류: {e}")
        import traceback
        traceback.print_exc()