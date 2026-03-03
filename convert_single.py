#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
단일 영상 변환 및 업데이트 스크립트
"""

import os
import re
import requests
from pathlib import Path
from dotenv import load_dotenv

# .env.local 로드
load_dotenv('.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

HEADERS = {
    'apikey': SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json'
}

video_id = "XveVkr3JHs4"

print(f"=== {video_id} 변환 및 업데이트 ===")

# 1. VTT 파일 변환
vtt_file = Path(f"subs/{video_id}.ko.vtt")
if not vtt_file.exists():
    print(f"ERROR: VTT 파일이 없습니다: {vtt_file}")
    exit(1)

print(f"VTT 파일 크기: {vtt_file.stat().st_size} bytes")

try:
    with open(vtt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    timestamped_text = []
    
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
                    timestamped_text.append(f"{timestamp} {full_text}")
        else:
            i += 1
    
    new_subtitle = '\n'.join(timestamped_text)
    print(f"변환 완료: {len(timestamped_text)}개 라인, {len(new_subtitle)}자")
    
    # 2. 현재 DB 자막과 비교
    print("\n=== DB 자막 비교 ===")
    try:
        url = f"{SUPABASE_URL}/rest/v1/influencer_videos?select=subtitle_text&video_id=eq.{video_id}"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if data and data[0].get('subtitle_text'):
                current_subtitle = data[0]['subtitle_text']
                current_length = len(current_subtitle)
                new_length = len(new_subtitle)
                
                print(f"현재 DB: {current_length}자")
                print(f"새 자막: {new_length}자")
                print(f"증가량: {new_length - current_length}자")
                
                if new_length > current_length:
                    print("업데이트가 필요합니다.")
                    
                    # 3. DB 업데이트
                    update_url = f"{SUPABASE_URL}/rest/v1/influencer_videos?video_id=eq.{video_id}"
                    update_data = {"subtitle_text": new_subtitle}
                    
                    update_response = requests.patch(update_url, headers=HEADERS, json=update_data)
                    
                    if update_response.status_code == 204:
                        print("DB 업데이트 성공!")
                        
                        # 확인
                        check_response = requests.get(url, headers=HEADERS)
                        if check_response.status_code == 200:
                            check_data = check_response.json()
                            updated_length = len(check_data[0]['subtitle_text'])
                            print(f"업데이트 확인: {updated_length}자")
                    else:
                        print(f"DB 업데이트 실패: {update_response.status_code}")
                else:
                    print("업데이트가 필요하지 않습니다.")
            else:
                print("현재 DB에 자막이 없습니다.")
    
    except Exception as e:
        print(f"DB 작업 중 오류: {e}")

except Exception as e:
    print(f"변환 중 오류: {e}")

print("작업 완료")