#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

from sesang101_analyze import Sesang101Analyzer
import os
import glob

print('=== 시그널 분석 테스트 ===')
analyzer = Sesang101Analyzer()

# 첫 번째 처리할 영상
subtitle_files = glob.glob(os.path.join(analyzer.subs_dir, '*.json'))
subtitle_files = [f for f in subtitle_files if not f.endswith('_failed.txt')]
unprocessed_files = [f for f in subtitle_files if os.path.basename(f).replace('.json', '') not in analyzer.processed_video_ids]

test_file = unprocessed_files[0]
video_id = os.path.basename(test_file).replace('.json', '')

print(f'테스트 영상: {video_id}')

# 자막 추출
subtitle_text = analyzer.extract_subtitle_text(test_file)
print(f'자막 길이: {len(subtitle_text)}자')

# 영상 정보 구성
video_titles = analyzer.load_video_titles()
title = video_titles.get(video_id, '')
video_info = analyzer.get_video_info(video_id, title)

print(f'영상 제목: {title}')
print(f'영상 URL: {video_info["url"]}')

# 시그널 분석 시작
print('시그널 분석 시작...')

try:
    result = analyzer.analyzer.analyze_video_subtitle(
        channel_url=analyzer.channel_info['url'],
        video_data=video_info,
        subtitle=subtitle_text
    )
    
    if result:
        signals = result.get('signals', [])
        print(f'분석 완료: {len(signals)}개 시그널 발견')
        for i, signal in enumerate(signals[:3]):  # 처음 3개만 출력
            print(f'  시그널 {i+1}: {signal.get("stock", "?")} - {signal.get("signal", "?")}')
    else:
        print('분석 결과 없음')
        
except Exception as e:
    print(f'분석 실패: {e}')
    import traceback
    traceback.print_exc()