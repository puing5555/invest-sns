#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
영상 자막 full text DB 업데이트 + 타임스탬프 전수 교정 스크립트 (requests 버전)
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

def test_supabase_connection():
    """Supabase 연결 테스트"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/influencer_videos?select=video_id&limit=1"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            print("[OK] Supabase 연결 성공. 테이블 접근 확인.")
            return True
        else:
            print(f"[ERROR] Supabase 연결 실패: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Supabase 연결 실패: {e}")
        return False

def get_all_video_ids():
    """influencer_videos 테이블에서 모든 video_id 조회"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/influencer_videos?select=video_id"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            video_ids = [row['video_id'] for row in data if row.get('video_id')]
            print(f"[OK] video_id {len(video_ids)}개 조회 완료")
            return video_ids
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
            # yt-dlp 명령어 실행
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
                else:
                    print(f"   stderr: {result.stderr[:200]}")
                
        except subprocess.TimeoutExpired:
            print(f"[WARN] {video_id}: 타임아웃 (시도 {attempt+1}/{max_retries})")
        except Exception as e:
            print(f"[WARN] {video_id}: 예외 발생 (시도 {attempt+1}/{max_retries}): {e}")
        
        if attempt < max_retries - 1:
            time.sleep(random.uniform(2, 5))  # 재시도 전 랜덤 딜레이
    
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
        
        # VTT 파싱
        lines = content.split('\n')
        timestamped_text = []
        
        i = 0
        while i < len(lines):
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
        
        if response.status_code == 204:  # Supabase PATCH는 204를 반환
            print(f"[OK] {video_id}: DB 업데이트 성공")
            return True
        else:
            print(f"[ERROR] {video_id}: DB 업데이트 실패 - {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] {video_id}: DB 업데이트 실패: {e}")
        return False

def get_signals_for_timestamp_correction():
    """타임스탬프 교정용 시그널 조회"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/signals?select=id,video_id,key_quote,timestamp"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] 타임스탬프 교정 대상 시그널 {len(data)}개 조회")
            return data
        else:
            print(f"[ERROR] 시그널 조회 실패: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"[ERROR] 시그널 조회 실패: {e}")
        return []

def get_video_subtitle(video_id):
    """특정 영상의 자막 조회"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/influencer_videos?select=subtitle_text&video_id=eq.{video_id}"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if data and data[0].get('subtitle_text'):
                return data[0]['subtitle_text']
        return None
    except Exception as e:
        print(f"[ERROR] {video_id} 자막 조회 실패: {e}")
        return None

def extract_timestamp_from_subtitle(key_quote, subtitle_text):
    """자막에서 key_quote 찾아서 타임스탬프 추출"""
    if not subtitle_text or not key_quote:
        return None
    
    # key_quote를 자막에서 검색
    lines = subtitle_text.split('\n')
    for line in lines:
        if key_quote in line:
            # [M:SS] 패턴 찾기
            timestamp_match = re.search(r'\[(\d+):(\d{2})\]', line)
            if timestamp_match:
                minutes = int(timestamp_match.group(1))
                seconds = int(timestamp_match.group(2))
                return minutes * 60 + seconds
    
    return None

def update_signal_timestamp(signal_id, new_timestamp):
    """시그널의 타임스탬프 업데이트"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/signals?id=eq.{signal_id}"
        data = {"timestamp": new_timestamp}
        
        response = requests.patch(url, headers=HEADERS, json=data)
        
        if response.status_code == 204:
            return True
        else:
            print(f"[ERROR] 시그널 {signal_id} 타임스탬프 업데이트 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] 시그널 {signal_id} 타임스탬프 업데이트 실패: {e}")
        return False

def correct_timestamps():
    """타임스탬프 전수 교정"""
    print("\n[TASK] 타임스탬프 전수 교정 시작")
    
    signals = get_signals_for_timestamp_correction()
    if not signals:
        print("[ERROR] 교정할 시그널이 없습니다.")
        return 0
    
    correction_count = 0
    
    for signal in signals:
        signal_id = signal['id']
        video_id = signal['video_id']
        key_quote = signal['key_quote']
        current_timestamp = signal['timestamp']
        
        # 영상 자막 조회
        subtitle_text = get_video_subtitle(video_id)
        if not subtitle_text:
            continue
        
        # 자막에서 타임스탬프 추출
        new_timestamp_seconds = extract_timestamp_from_subtitle(key_quote, subtitle_text)
        if new_timestamp_seconds is None:
            continue
        
        # 30초 이상 차이나는지 확인
        if current_timestamp is not None:
            diff = abs(new_timestamp_seconds - current_timestamp)
            if diff >= 30:
                # 타임스탬프 업데이트
                if update_signal_timestamp(signal_id, new_timestamp_seconds):
                    print(f"[OK] 시그널 {signal_id}: {current_timestamp}s -> {new_timestamp_seconds}s (차이: {diff}s)")
                    correction_count += 1
    
    print(f"\n[RESULT] 타임스탬프 교정 완료: {correction_count}건")
    return correction_count

def main():
    """메인 함수"""
    print("=== 자막 업데이트 + 타임스탬프 교정 작업 시작 ===")
    
    # Supabase 연결 테스트
    if not test_supabase_connection():
        return
    
    # 작업 1: 자막 재수집
    print("\n[TASK] 작업 1: 자막 재수집 시작")
    
    # video_id 목록 조회
    video_ids = get_all_video_ids()
    if not video_ids:
        print("[ERROR] video_id가 없습니다.")
        return
    
    # 통계 변수
    total = len(video_ids)
    success_download = 0
    success_update = 0
    failed_videos = []
    
    print(f"[INFO] 총 {total}개 영상 처리 시작")
    
    for idx, video_id in enumerate(video_ids, 1):
        print(f"\n[{idx}/{total}] 처리 중: {video_id}")
        
        # 1. 자막 다운로드
        if download_subtitle(video_id):
            success_download += 1
            
            # 2. VTT -> 텍스트 변환
            subtitle_text = convert_vtt_to_timestamped_text(video_id)
            if subtitle_text:
                # 3. DB 업데이트
                if update_subtitle_in_db(video_id, subtitle_text):
                    success_update += 1
                else:
                    failed_videos.append(f"{video_id} (DB 업데이트 실패)")
            else:
                failed_videos.append(f"{video_id} (자막 변환 실패)")
        else:
            failed_videos.append(f"{video_id} (다운로드 실패)")
        
        # 레이트리밋 준수
        if idx % 20 == 0:  # 20개마다 5분 휴식
            print("[INFO] 20개 처리 완료. 5분 휴식...")
            time.sleep(300)
        else:
            time.sleep(random.uniform(2, 3))  # 2-3초 랜덤 딜레이
    
    # 작업 1 결과 리포트
    print("\n" + "="*50)
    print("[REPORT] 자막 수집 결과 리포트")
    print("="*50)
    print(f"총 영상 수: {total}")
    print(f"다운로드 성공: {success_download}")
    print(f"DB 업데이트 성공: {success_update}")
    print(f"실패: {len(failed_videos)}")
    
    if failed_videos:
        print("\n[ERROR] 실패 목록:")
        for failed in failed_videos:
            print(f"  - {failed}")
    
    # 작업 2: 타임스탬프 전수 교정
    print("\n[TASK] 작업 2: 타임스탬프 전수 교정 시작")
    correction_count = correct_timestamps()
    
    # 최종 결과 리포트
    print("\n" + "="*50)
    print("[FINAL] 최종 결과 리포트")
    print("="*50)
    print(f"자막 수집 성공: {success_update}/{total}")
    print(f"타임스탬프 교정: {correction_count}건")
    print(f"완료 시간: {datetime.now()}")
    
    return {
        'total_videos': total,
        'subtitle_success': success_update,
        'subtitle_failed': len(failed_videos),
        'timestamp_corrections': correction_count,
        'failed_videos': failed_videos
    }

if __name__ == "__main__":
    result = main()