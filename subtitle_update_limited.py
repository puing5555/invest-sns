#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
제한된 영상 자막 업데이트 스크립트 (처음 5개만)
"""

import os
import json
import time
import random
import subprocess
import re
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# .env.local 로드
load_dotenv('.env.local')

# Supabase 설정
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("[ERROR] Supabase 환경변수가 없습니다.")
    exit(1)

# Supabase REST API 헤더
HEADERS = {
    'apikey': SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json'
}

def get_limited_video_ids(limit=5):
    """제한된 수의 video_id 조회"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/influencer_videos?select=video_id,subtitle_text&limit={limit}"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            video_info = []
            for row in data:
                if row.get('video_id'):
                    subtitle_len = len(row.get('subtitle_text', '')) if row.get('subtitle_text') else 0
                    video_info.append({
                        'video_id': row['video_id'],
                        'current_subtitle_length': subtitle_len
                    })
            print(f"[OK] {len(video_info)}개 영상 정보 조회 완료")
            return video_info
        else:
            print(f"[ERROR] video_id 조회 실패: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"[ERROR] video_id 조회 실패: {e}")
        return []

def download_subtitle(video_id, max_retries=3):
    """yt-dlp로 자막 다운로드"""
    subs_dir = Path("subs")
    subs_dir.mkdir(exist_ok=True)
    
    url = f"https://youtube.com/watch?v={video_id}"
    
    for attempt in range(max_retries):
        try:
            cmd = [
                "python", "-m", "yt_dlp",
                "--write-auto-sub",
                "--sub-lang", "ko",
                "--skip-download",
                "-o", f"subs/{video_id}",
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"[OK] {video_id}: 자막 다운로드 성공")
                return True
            else:
                print(f"[WARN] {video_id}: 자막 다운로드 실패 (시도 {attempt+1}/{max_retries})")
                if "429" in result.stderr:
                    print("   429 Too Many Requests 감지 - 60초 대기")
                    time.sleep(60)
                
        except subprocess.TimeoutExpired:
            print(f"[WARN] {video_id}: 타임아웃 (시도 {attempt+1}/{max_retries})")
        except Exception as e:
            print(f"[WARN] {video_id}: 예외 발생 (시도 {attempt+1}/{max_retries}): {e}")
        
        if attempt < max_retries - 1:
            time.sleep(random.uniform(2, 5))
    
    print(f"[ERROR] {video_id}: 최대 재시도 후 실패")
    return False

def convert_vtt_to_timestamped_text(video_id):
    """VTT 파일을 [M:SS] 형식 텍스트로 변환"""
    vtt_file = Path(f"subs/{video_id}.ko.vtt")
    
    if not vtt_file.exists():
        print(f"[ERROR] {video_id}: VTT 파일이 없습니다.")
        return None
    
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
        
        result = '\n'.join(timestamped_text)
        print(f"[OK] {video_id}: 자막 변환 완료 ({len(result)}자)")
        return result
        
    except Exception as e:
        print(f"[ERROR] {video_id}: 자막 변환 실패: {e}")
        return None

def update_subtitle_in_db(video_id, subtitle_text):
    """DB에 자막 업데이트"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/influencer_videos?video_id=eq.{video_id}"
        data = {"subtitle_text": subtitle_text}
        
        response = requests.patch(url, headers=HEADERS, json=data)
        
        if response.status_code == 204:
            print(f"[OK] {video_id}: DB 업데이트 성공")
            return True
        else:
            print(f"[ERROR] {video_id}: DB 업데이트 실패 - {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] {video_id}: DB 업데이트 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("=== 제한된 자막 업데이트 테스트 (처음 5개) ===")
    
    # 제한된 video_id 목록 조회
    video_infos = get_limited_video_ids(5)
    if not video_infos:
        print("[ERROR] video_id가 없습니다.")
        return
    
    # 현재 자막 상태 분석
    print("\n=== 현재 자막 상태 분석 ===")
    for info in video_infos:
        video_id = info['video_id']
        length = info['current_subtitle_length']
        status = "자막없음" if length == 0 else f"{length}자"
        if length == 5000:
            status += " (5000자 잘림 추정)"
        print(f"{video_id}: {status}")
    
    # 통계 변수
    total = len(video_infos)
    success_download = 0
    success_update = 0
    failed_videos = []
    
    print(f"\n[INFO] 총 {total}개 영상 처리 시작")
    
    for idx, info in enumerate(video_infos, 1):
        video_id = info['video_id']
        current_length = info['current_subtitle_length']
        
        print(f"\n[{idx}/{total}] 처리 중: {video_id} (현재 {current_length}자)")
        
        # 1. 자막 다운로드
        if download_subtitle(video_id):
            success_download += 1
            
            # 2. VTT -> 텍스트 변환
            subtitle_text = convert_vtt_to_timestamped_text(video_id)
            if subtitle_text:
                new_length = len(subtitle_text)
                print(f"[INFO] {video_id}: 새 자막 {new_length}자 (기존 {current_length}자)")
                
                # 길이 증가가 있거나 자막이 없었던 경우만 업데이트
                if new_length > current_length or current_length == 0:
                    if update_subtitle_in_db(video_id, subtitle_text):
                        success_update += 1
                        print(f"[UPDATE] {video_id}: {current_length}자 -> {new_length}자 (+{new_length - current_length}자)")
                    else:
                        failed_videos.append(f"{video_id} (DB 업데이트 실패)")
                else:
                    print(f"[SKIP] {video_id}: 기존 자막이 더 길어서 스킵")
                    success_update += 1  # 스킵도 성공으로 처리
            else:
                failed_videos.append(f"{video_id} (자막 변환 실패)")
        else:
            failed_videos.append(f"{video_id} (다운로드 실패)")
        
        # 레이트리밋 준수 (짧은 테스트이므로 2-3초만)
        if idx < total:
            time.sleep(random.uniform(2, 3))
    
    # 결과 리포트
    print("\n" + "="*50)
    print("[REPORT] 제한된 자막 수집 결과 리포트")
    print("="*50)
    print(f"총 영상 수: {total}")
    print(f"다운로드 성공: {success_download}")
    print(f"DB 처리 성공: {success_update}")
    print(f"실패: {len(failed_videos)}")
    
    if failed_videos:
        print("\n[ERROR] 실패 목록:")
        for failed in failed_videos:
            print(f"  - {failed}")
    
    print(f"\n완료 시간: {datetime.now()}")
    
    return {
        'total_videos': total,
        'subtitle_success': success_update,
        'subtitle_failed': len(failed_videos),
        'failed_videos': failed_videos
    }

if __name__ == "__main__":
    result = main()