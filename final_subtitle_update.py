#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 자막 업데이트 스크립트 - 단순화된 버전
"""

import os
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

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

HEADERS = {
    'apikey': SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json'
}

# 처리 통계
stats = {
    'total': 0,
    'success_download': 0,
    'success_update': 0,
    'failed': 0,
    'skipped': 0,
    'start_time': datetime.now()
}

def log(message):
    """로그 출력"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_update_candidates():
    """업데이트 후보 조회"""
    log("업데이트 후보 조회 중...")
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/influencer_videos?select=video_id,subtitle_text"
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code != 200:
            log(f"ERROR: DB 조회 실패 {response.status_code}")
            return []
        
        data = response.json()
        candidates = []
        
        for row in data:
            video_id = row['video_id']
            subtitle = row.get('subtitle_text', '')
            
            if not subtitle or len(subtitle) == 5000:
                candidates.append({
                    'video_id': video_id,
                    'current_length': len(subtitle) if subtitle else 0,
                    'reason': 'empty' if not subtitle else 'truncated'
                })
        
        log(f"업데이트 후보 {len(candidates)}개 발견")
        return candidates
        
    except Exception as e:
        log(f"ERROR: 후보 조회 실패 - {e}")
        return []

def download_and_convert(video_id):
    """자막 다운로드 및 변환"""
    subs_dir = Path("subs")
    subs_dir.mkdir(exist_ok=True)
    
    # 다운로드
    try:
        url = f"https://youtube.com/watch?v={video_id}"
        cmd = [
            "python", "-m", "yt_dlp",
            "--write-auto-sub", "--sub-lang", "ko", "--skip-download",
            "-o", f"subs/{video_id}", url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            log(f"WARN: {video_id} 다운로드 실패")
            return None
            
        log(f"OK: {video_id} 다운로드 성공")
        
    except Exception as e:
        log(f"ERROR: {video_id} 다운로드 예외 - {e}")
        return None
    
    # VTT 변환
    vtt_file = Path(f"subs/{video_id}.ko.vtt")
    if not vtt_file.exists():
        log(f"ERROR: {video_id} VTT 파일 없음")
        return None
    
    try:
        with open(vtt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        result_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if '-->' in line:
                match = re.match(r'(\d{2}):(\d{2}):(\d{2})\.\d+', line)
                if match:
                    h, m, s = map(int, match.groups())
                    total_min = h * 60 + m
                    timestamp = f"[{total_min}:{s:02d}]"
                    
                    i += 1
                    text_parts = []
                    while i < len(lines) and lines[i].strip() and '-->' not in lines[i]:
                        text = lines[i].strip()
                        text = re.sub(r'<[^>]+>', '', text)
                        if text:
                            text_parts.append(text)
                        i += 1
                    
                    if text_parts:
                        result_lines.append(f"{timestamp} {' '.join(text_parts)}")
            else:
                i += 1
        
        final_text = '\n'.join(result_lines)
        log(f"OK: {video_id} 변환 완료 ({len(final_text)}자)")
        return final_text
        
    except Exception as e:
        log(f"ERROR: {video_id} 변환 실패 - {e}")
        return None

def update_database(video_id, subtitle_text):
    """DB 업데이트"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/influencer_videos?video_id=eq.{video_id}"
        data = {"subtitle_text": subtitle_text}
        
        response = requests.patch(url, headers=HEADERS, json=data, timeout=30)
        
        if response.status_code == 204:
            log(f"OK: {video_id} DB 업데이트 성공")
            return True
        else:
            log(f"ERROR: {video_id} DB 업데이트 실패 {response.status_code}")
            return False
            
    except Exception as e:
        log(f"ERROR: {video_id} DB 업데이트 예외 - {e}")
        return False

def process_one_video(candidate):
    """한 개 영상 처리"""
    video_id = candidate['video_id']
    current_length = candidate['current_length']
    
    log(f"처리 시작: {video_id} (현재 {current_length}자)")
    
    # 다운로드 및 변환
    new_subtitle = download_and_convert(video_id)
    if not new_subtitle:
        stats['failed'] += 1
        return False
    
    stats['success_download'] += 1
    new_length = len(new_subtitle)
    
    # 길이 확인
    if new_length <= current_length:
        log(f"SKIP: {video_id} 새 자막이 더 짧음 ({new_length} vs {current_length})")
        stats['skipped'] += 1
        return True
    
    # DB 업데이트
    if update_database(video_id, new_subtitle):
        increase = new_length - current_length
        log(f"UPDATE: {video_id} 완료 ({current_length} -> {new_length}, +{increase}자)")
        stats['success_update'] += 1
        return True
    else:
        stats['failed'] += 1
        return False

def main():
    """메인 함수"""
    log("=== 자막 업데이트 작업 시작 ===")
    
    # 후보 조회
    candidates = get_update_candidates()
    if not candidates:
        log("업데이트할 영상이 없습니다.")
        return
    
    stats['total'] = len(candidates)
    
    # 배치 크기 설정 (테스트용)
    BATCH_SIZE = 15  # 일단 15개만
    process_candidates = candidates[:BATCH_SIZE]
    
    log(f"총 {stats['total']}개 중 {len(process_candidates)}개 처리 시작")
    
    # 순차 처리
    for idx, candidate in enumerate(process_candidates, 1):
        log(f"--- [{idx}/{len(process_candidates)}] ---")
        
        success = process_one_video(candidate)
        
        # 진행상황 리포트
        if idx % 5 == 0 or idx == len(process_candidates):
            elapsed = datetime.now() - stats['start_time']
            log(f"진행률: {idx}/{len(process_candidates)} ({idx/len(process_candidates)*100:.1f}%)")
            log(f"성공: {stats['success_update']}, 실패: {stats['failed']}, 스킵: {stats['skipped']}")
            log(f"경과시간: {elapsed}")
        
        # 레이트리밋 (마지막 제외)
        if idx < len(process_candidates):
            if idx % 20 == 0:  # 20개마다 5분 휴식
                log("20개 처리 완료 - 5분 휴식")
                time.sleep(300)
            else:
                delay = random.uniform(2.0, 3.0)
                time.sleep(delay)
    
    # 최종 리포트
    elapsed = datetime.now() - stats['start_time']
    log("=== 최종 결과 ===")
    log(f"처리 대상: {len(process_candidates)}")
    log(f"다운로드 성공: {stats['success_download']}")
    log(f"DB 업데이트 성공: {stats['success_update']}")
    log(f"실패: {stats['failed']}")
    log(f"스킵: {stats['skipped']}")
    log(f"총 소요시간: {elapsed}")
    
    if len(candidates) > BATCH_SIZE:
        log(f"남은 작업: {len(candidates) - BATCH_SIZE}개")

if __name__ == "__main__":
    main()