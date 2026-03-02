#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_5_sesang101.py - 세상학개론 5개 파일 테스트
"""

import os
import json
import sys
import time
import glob
from datetime import datetime

# 모듈 import
sys.path.append(os.path.dirname(__file__))
from pipeline_config import PipelineConfig
from signal_analyzer_rest import SignalAnalyzer
from db_inserter_rest import DatabaseInserter

def test_five_videos():
    print("=== 세상학개론 5개 영상 테스트 ===")
    
    # 설정
    config = PipelineConfig()
    analyzer = SignalAnalyzer()
    db_inserter = DatabaseInserter()
    
    # 채널 정보
    channel_info = {
        'url': 'https://www.youtube.com/@sesang101',
        'name': '세상학개론',
        'subscriber_count': 150000,
        'video_count': 200,
        'description': '이효석의 세상학개론 - 투자와 경제 분석'
    }
    
    # 호스트 정보
    host_info = {
        'name': '이효석',
        'role': '세상학개론 메인 진행자',
        'bio': '투자 전문가, 유튜버'
    }
    
    # 자막 파일 목록 (5개만)
    subs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'subs', 'sesang101')
    subtitle_files = glob.glob(os.path.join(subs_dir, "*.json"))
    subtitle_files = [f for f in subtitle_files if not f.endswith('_failed.txt')]
    subtitle_files = subtitle_files[:5]  # 5개만
    
    results = []
    
    for i, subtitle_file in enumerate(subtitle_files, 1):
        video_id = os.path.basename(subtitle_file).replace('.json', '')
        print(f"\n[{i}/5] 처리 중: {video_id}")
        
        try:
            # 자막 텍스트 추출
            with open(subtitle_file, 'r', encoding='utf-8') as f:
                segments = json.load(f)
            
            full_text = ""
            for segment in segments:
                if isinstance(segment, dict) and 'text' in segment:
                    full_text += segment['text'] + " "
            
            full_text = full_text.strip()
            print(f"자막 길이: {len(full_text)}자")
            
            if len(full_text) < 100:
                print(f"[SKIP] 자막 너무 짧음")
                continue
            
            # 영상 정보
            video_info = {
                'title': f'세상학개론 영상 {video_id}',
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'duration': 'N/A',
                'upload_date': 'N/A'
            }
            
            # 시그널 분석
            print(f"[ANALYZE] 분석 중...")
            start_time = time.time()
            
            result = analyzer.analyze_video_subtitle(
                channel_url=channel_info['url'],
                video_data=video_info,
                subtitle=full_text
            )
            
            end_time = time.time()
            print(f"분석 시간: {end_time - start_time:.2f}초")
            
            if result:
                signals = result.get('signals', [])
                print(f"시그널 수: {len(signals)}개")
                
                if signals:
                    for j, signal in enumerate(signals, 1):
                        print(f"  시그널 {j}:")
                        print(f"    종목: {signal.get('stock', 'N/A')}")
                        print(f"    시그널: {signal.get('signal_type', 'N/A')}")
                        print(f"    신뢰도: {signal.get('confidence', 'N/A')}")
                        print(f"    타임스탬프: {signal.get('timestamp', 'N/A')}")
                
                results.append({
                    'video_id': video_id,
                    'subtitle_length': len(full_text),
                    'signals_found': len(signals),
                    'analysis_time': end_time - start_time,
                    'signals': signals
                })
            else:
                print("분석 결과 없음")
                results.append({
                    'video_id': video_id,
                    'subtitle_length': len(full_text),
                    'signals_found': 0,
                    'analysis_time': end_time - start_time,
                    'signals': []
                })
            
            # API 레이트리밋
            if i < len(subtitle_files):
                print("[WAIT] 5초 대기...")
                time.sleep(5)
            
        except Exception as e:
            print(f"[ERROR] 처리 실패: {e}")
            import traceback
            traceback.print_exc()
    
    # 결과 요약
    print(f"\n=== 테스트 완료 ===")
    total_signals = sum(r['signals_found'] for r in results)
    avg_time = sum(r['analysis_time'] for r in results) / len(results) if results else 0
    
    print(f"처리된 영상: {len(results)}개")
    print(f"총 시그널: {total_signals}개")
    print(f"평균 분석 시간: {avg_time:.2f}초")
    
    # 결과 저장
    result_file = os.path.join(os.path.dirname(__file__), '..', 'test_5_results.json')
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_date': datetime.now().isoformat(),
            'results': results,
            'summary': {
                'total_videos': len(results),
                'total_signals': total_signals,
                'avg_analysis_time': avg_time
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"결과 저장: {result_file}")

if __name__ == "__main__":
    test_five_videos()