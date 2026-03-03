#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VTT 파일 변환 테스트
"""

import re
from pathlib import Path

video_id = "Ke7gQMbIFLI"
vtt_file = Path(f"subs/{video_id}.ko.vtt")

print(f"VTT 파일 변환 테스트: {vtt_file}")

if not vtt_file.exists():
    print("[ERROR] VTT 파일이 없습니다.")
    exit(1)

try:
    with open(vtt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"원본 파일 크기: {len(content)} 문자")
    
    # VTT 파싱
    lines = content.split('\n')
    timestamped_text = []
    
    i = 0
    processed_count = 0
    while i < len(lines) and processed_count < 10:  # 처음 10개만 테스트
        line = lines[i].strip()
        
        # 타임스탬프 라인 찾기 (00:01:30.000 --> 00:01:35.000 형식)
        if '-->' in line:
            timestamp_match = re.match(r'(\d{2}):(\d{2}):(\d{2})\.\d+', line)
            if timestamp_match:
                hours, minutes, seconds = map(int, timestamp_match.groups())
                total_minutes = hours * 60 + minutes
                timestamp = f"[{total_minutes}:{seconds:02d}]"
                
                # 다음 라인들에서 텍스트 수집
                i += 1
                text_lines = []
                while i < len(lines) and lines[i].strip() and '-->' not in lines[i]:
                    text = lines[i].strip()
                    # VTT 태그 제거
                    text = re.sub(r'<[^>]+>', '', text)
                    if text:
                        text_lines.append(text)
                    i += 1
                
                if text_lines:
                    full_text = ' '.join(text_lines)
                    result_line = f"{timestamp} {full_text}"
                    timestamped_text.append(result_line)
                    print(f"변환됨: {result_line}")
                    processed_count += 1
        else:
            i += 1
    
    final_result = '\n'.join(timestamped_text)
    print(f"\n=== 변환 결과 (처음 10개) ===")
    print(final_result)
    print(f"\n변환된 총 길이: {len(final_result)} 문자")
    
    # 전체 변환 수행
    print("\n=== 전체 변환 수행 ===")
    lines = content.split('\n')
    all_timestamped_text = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if '-->' in line:
            timestamp_match = re.match(r'(\d{2}):(\d{2}):(\d{2})\.\d+', line)
            if timestamp_match:
                hours, minutes, seconds = map(int, timestamp_match.groups())
                total_minutes = hours * 60 + minutes
                timestamp = f"[{total_minutes}:{seconds:02d}]"
                
                i += 1
                text_lines = []
                while i < len(lines) and lines[i].strip() and '-->' not in lines[i]:
                    text = lines[i].strip()
                    text = re.sub(r'<[^>]+>', '', text)
                    if text:
                        text_lines.append(text)
                    i += 1
                
                if text_lines:
                    full_text = ' '.join(text_lines)
                    all_timestamped_text.append(f"{timestamp} {full_text}")
        else:
            i += 1
    
    full_result = '\n'.join(all_timestamped_text)
    print(f"전체 변환 완료: {len(all_timestamped_text)}개 라인, {len(full_result)} 문자")
    
    # 샘플 저장
    with open(f"subs/{video_id}_converted.txt", 'w', encoding='utf-8') as f:
        f.write(full_result)
    print(f"변환 결과 저장: subs/{video_id}_converted.txt")

except Exception as e:
    print(f"[ERROR] 변환 실패: {e}")

print("변환 테스트 완료")