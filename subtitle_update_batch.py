#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
배치 자막 업데이트 스크립트
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

HEADERS = {
    'apikey': SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json'
}

def get_update_needed_videos(limit=None):
    """업데이트가 필요한 영상 목록 조회"""
    print("=== 업데이트 필요 영상 조회 ===")
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/influencer_videos?select=video_id,subtitle_text"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code != 200:
            print(f"[ERROR] DB 조회 실패: {response.status_code}")
            return []
        
        data = response.json()
        need_update = []
        
        for row in data:
            video_id = row['video_id']
            subtitle = row.get('subtitle_text', '')
            
            # 자막이 없거나 5000자로 잘린 경우
            if not subtitle or len(subtitle) == 5000:
                reason = "자막없음" if not subtitle else "5000자잘림"
                need_update.append({
                    'video_id': video_id,
                    'reason': reason,
                    'current_length': len(subtitle) if subtitle else 0
                })
        
        if limit:
            need_update = need_update[:limit]
        
        print(f"[OK] 업데이트 필요 영상 {len(need_update)}개 확인")
        return need_update
        
    except Exception as e:
        print(f"[ERROR] 조회 실패: {e}")
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
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"[OK] {video_id}: 자막 다운로드 성공")
                return True
            else:
                print(f"[WARN] {video_id}: 자막 다운로드 실패 (시도 {attempt+1}/{max_retries})")
                if "429" in result.stderr:
                    print("   429 Too Many Requests 감지 - 60초 대기")
                    time.sleep(60)
                elif "Private video" in result.stderr or "unavailable" in result.stderr:
                    print("   영상이 비공개이거나 삭제됨")
                    return False
                
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

def process_videos(videos, start_from=0):
    """영상들을 순차 처리"""
    total = len(videos)
    success_download = 0
    success_update = 0
    failed_videos = []
    
    print(f"\n[INFO] {start_from+1}번째부터 총 {total}개 영상 처리 시작")
    
    for idx in range(start_from, total):
        video_info = videos[idx]
        video_id = video_info['video_id']
        current_length = video_info['current_length']
        reason = video_info['reason']
        
        print(f"\n[{idx+1}/{total}] 처리 중: {video_id} ({reason}, {current_length}자)")
        
        # 1. 자막 다운로드
        if download_subtitle(video_id):
            success_download += 1
            
            # 2. VTT -> 텍스트 변환
            subtitle_text = convert_vtt_to_timestamped_text(video_id)
            if subtitle_text:
                new_length = len(subtitle_text)
                
                # 3. DB 업데이트 (새 자막이 더 길거나 기존 자막이 없는 경우만)
                if new_length > current_length:
                    if update_subtitle_in_db(video_id, subtitle_text):
                        success_update += 1
                        increase = new_length - current_length
                        print(f"[UPDATE] {video_id}: {current_length}자 -> {new_length}자 (+{increase}자)")
                    else:
                        failed_videos.append(f"{video_id} (DB 업데이트 실패)")
                else:
                    print(f"[SKIP] {video_id}: 새 자막이 더 짧음 ({new_length}자 vs {current_length}자)")
                    success_update += 1  # 스킵도 성공으로 처리
            else:
                failed_videos.append(f"{video_id} (자막 변환 실패)")
        else:
            failed_videos.append(f"{video_id} (다운로드 실패)")
        
        # 레이트리밋 준수
        processed_count = idx - start_from + 1
        if processed_count % 20 == 0:
            print(f"[INFO] {processed_count}개 처리 완료. 5분 휴식...")
            time.sleep(300)  # 5분 휴식
        else:
            delay = random.uniform(2, 3)
            print(f"[INFO] {delay:.1f}초 대기...")
            time.sleep(delay)
    
    return success_download, success_update, failed_videos

def main():
    """메인 함수"""
    print("=== 배치 자막 업데이트 시작 ===")
    print(f"시작 시간: {datetime.now()}")
    
    # 처리할 영상 개수 설정 (테스트용으로 10개부터 시작)
    BATCH_SIZE = 10
    
    # 업데이트 필요 영상 조회
    videos = get_update_needed_videos()
    if not videos:
        print("[ERROR] 업데이트할 영상이 없습니다.")
        return
    
    print(f"[INFO] 총 {len(videos)}개 영상 중 {BATCH_SIZE}개부터 시작")
    
    # 첫 번째 배치 처리
    batch_videos = videos[:BATCH_SIZE]
    success_download, success_update, failed_videos = process_videos(batch_videos)
    
    # 결과 리포트
    print("\n" + "="*50)
    print(f"[REPORT] 배치 처리 결과 ({BATCH_SIZE}개)")
    print("="*50)
    print(f"처리 대상: {len(batch_videos)}개")
    print(f"다운로드 성공: {success_download}")
    print(f"DB 업데이트 성공: {success_update}")
    print(f"실패: {len(failed_videos)}")
    
    if failed_videos:
        print("\n[ERROR] 실패 목록:")
        for failed in failed_videos:
            print(f"  - {failed}")
    
    print(f"\n완료 시간: {datetime.now()}")
    
    if len(videos) > BATCH_SIZE:
        print(f"\n[INFO] 남은 작업: {len(videos) - BATCH_SIZE}개")
        print("전체 처리를 원하면 BATCH_SIZE를 늘리거나 start_from 파라미터를 조정하세요.")

if __name__ == "__main__":
    main()