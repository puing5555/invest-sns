#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
manual_test.py - 수동으로 선택한 투자 관련 영상들 테스트
"""

import os
import json
import sys
import time
from datetime import datetime

# 모듈 import
sys.path.append(os.path.dirname(__file__))
from pipeline_config import PipelineConfig
from signal_analyzer_rest import SignalAnalyzer

def test_investment_videos():
    print("=== 투자 관련 영상 수동 테스트 ===")
    
    # 설정
    config = PipelineConfig()
    analyzer = SignalAnalyzer()
    
    # 테스트할 영상들 (투자 관련)
    test_videos = [
        {
            'id': 'UVeJSmWGzRw',
            'title': '3 Reasons to Buy IREN',
            'expected': 'IREN 매수 시그널'
        },
        {
            'id': 'iLUIU1sU1Ug',
            'title': 'Airen has tripled in 3 months, Rocket Lab has doubled. Are you really not selling it for 10 times?',
            'expected': 'IREN/RKLB 관련 시그널'
        },
        {
            'id': '1xfjt7moZEg',
            'title': 'Stop Watching Bitcoin Halvings Anymore: How to Read Bitcoin Market Changes After Trump',
            'expected': 'Bitcoin 관련 시그널'
        },
        {
            'id': '0z8e_heKtKk',
            'title': 'Should we be concerned about Bitcoin crash after the Hungda bankruptcy and Tether collapse?',
            'expected': 'Bitcoin 관련 시그널'
        }
    ]
    
    results = []
    subs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'subs', 'sesang101')
    
    for i, video in enumerate(test_videos, 1):
        print(f"\n[{i}/{len(test_videos)}] 테스트: {video['id']}")
        print(f"제목: {video['title']}")
        print(f"기대: {video['expected']}")
        
        # 자막 파일 경로
        subtitle_file = os.path.join(subs_dir, f"{video['id']}.json")
        
        if not os.path.exists(subtitle_file):
            print(f"[SKIP] 자막 파일 없음: {subtitle_file}")
            continue
        
        try:
            # 자막 읽기
            with open(subtitle_file, 'r', encoding='utf-8') as f:
                segments = json.load(f)
            
            full_text = ""
            for segment in segments:
                if isinstance(segment, dict) and 'text' in segment:
                    full_text += segment['text'] + " "
            
            full_text = full_text.strip()
            print(f"자막 길이: {len(full_text)}자")
            print(f"미리보기: {full_text[:150]}...")
            
            # 영상 정보
            video_info = {
                'title': video['title'],
                'url': f'https://www.youtube.com/watch?v={video["id"]}',
                'duration': 'N/A',
                'upload_date': 'N/A'
            }
            
            # 분석
            print(f"[ANALYZE] 분석 시작...")
            start_time = time.time()
            
            result = analyzer.analyze_video_subtitle(
                channel_url='https://www.youtube.com/@sesang101',
                video_data=video_info,
                subtitle=full_text
            )
            
            end_time = time.time()
            print(f"분석 시간: {end_time - start_time:.2f}초")
            
            if result and 'signals' in result:
                signals = result['signals']
                print(f"시그널 수: {len(signals)}개")
                
                for j, signal in enumerate(signals, 1):
                    print(f"\n--- 시그널 {j} ---")
                    print(f"종목: {signal.get('stock', 'N/A')}")
                    print(f"시그널: {signal.get('signal_type', 'N/A')}")
                    print(f"핵심 발언: {signal.get('key_quote', 'N/A')}")
                    print(f"근거: {signal.get('reasoning', 'N/A')}")
                    print(f"타임스탬프: {signal.get('timestamp', 'N/A')}")
                    print(f"신뢰도: {signal.get('confidence', 'N/A')}")
                
                results.append({
                    'video_id': video['id'],
                    'title': video['title'],
                    'expected': video['expected'],
                    'signals_found': len(signals),
                    'signals': signals,
                    'analysis_time': end_time - start_time
                })
                
            else:
                print("시그널 없음")
                results.append({
                    'video_id': video['id'],
                    'title': video['title'],
                    'expected': video['expected'],
                    'signals_found': 0,
                    'signals': [],
                    'analysis_time': end_time - start_time
                })
            
            # 레이트리밋
            if i < len(test_videos):
                print("[WAIT] 5초 대기...")
                time.sleep(5)
                
        except Exception as e:
            print(f"[ERROR] 처리 실패: {e}")
            import traceback
            traceback.print_exc()
    
    # 결과 요약
    print(f"\n=== 테스트 결과 요약 ===")
    total_signals = sum(r['signals_found'] for r in results)
    successful_videos = len([r for r in results if r['signals_found'] > 0])
    
    print(f"테스트된 영상: {len(results)}개")
    print(f"시그널 발견 영상: {successful_videos}개")
    print(f"총 시그널 수: {total_signals}개")
    
    # 결과 저장
    result_file = os.path.join(os.path.dirname(__file__), '..', 'manual_test_results.json')
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_date': datetime.now().isoformat(),
            'results': results,
            'summary': {
                'total_videos': len(results),
                'successful_videos': successful_videos,
                'total_signals': total_signals
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"결과 저장: {result_file}")

if __name__ == "__main__":
    test_investment_videos()