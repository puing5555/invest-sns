#!/usr/bin/env python3
"""
영상 자막 full text DB 업데이트 + 타임스탬프 전수 교정 스크립트
"""

import os
import json
import time
import random
import subprocess
import re
from datetime import datetime
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# .env.local 로드
load_dotenv('.env.local')

# Supabase 클라이언트 초기화
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Supabase 환경변수가 없습니다.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def test_supabase_connection():
    """Supabase 연결 테스트"""
    try:
        # influencer_videos 테이블 간단 조회
        response = supabase.table('influencer_videos').select('video_id').limit(1).execute()
        print(f"✅ Supabase 연결 성공. 테이블 접근 확인.")
        return True
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        return False

def get_all_video_ids():
    """influencer_videos 테이블에서 모든 video_id 조회"""
    try:
        response = supabase.table('influencer_videos').select('video_id').execute()
        video_ids = [row['video_id'] for row in response.data if row['video_id']]
        print(f"✅ video_id {len(video_ids)}개 조회 완료")
        return video_ids
    except Exception as e:
        print(f"❌ video_id 조회 실패: {e}")
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
                print(f"✅ {video_id}: 자막 다운로드 성공")
                return True
            else:
                print(f"⚠️  {video_id}: 자막 다운로드 실패 (시도 {attempt+1}/{max_retries})")
                print(f"   stderr: {result.stderr[:200]}")
                
        except subprocess.TimeoutExpired:
            print(f"⚠️  {video_id}: 타임아웃 (시도 {attempt+1}/{max_retries})")
        except Exception as e:
            print(f"⚠️  {video_id}: 예외 발생 (시도 {attempt+1}/{max_retries}): {e}")
        
        if attempt < max_retries - 1:
            time.sleep(random.uniform(2, 5))  # 재시도 전 랜덤 딜레이
    
    print(f"❌ {video_id}: 최대 재시도 후 실패")
    return False

def convert_vtt_to_timestamped_text(video_id):
    """VTT 파일을 [M:SS] 형식 텍스트로 변환"""
    vtt_file = Path(f"subs/{video_id}.ko.vtt")
    
    if not vtt_file.exists():
        print(f"❌ {video_id}: VTT 파일이 없습니다.")
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
        print(f"✅ {video_id}: 자막 변환 완료 ({len(result)}자)")
        return result
        
    except Exception as e:
        print(f"❌ {video_id}: 자막 변환 실패: {e}")
        return None

def update_subtitle_in_db(video_id, subtitle_text):
    """DB에 자막 업데이트"""
    try:
        response = supabase.table('influencer_videos').update({
            'subtitle_text': subtitle_text
        }).eq('video_id', video_id).execute()
        
        if response.data:
            print(f"✅ {video_id}: DB 업데이트 성공")
            return True
        else:
            print(f"❌ {video_id}: DB 업데이트 실패 - 데이터 없음")
            return False
            
    except Exception as e:
        print(f"❌ {video_id}: DB 업데이트 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("🚀 자막 업데이트 작업 시작")
    
    # Supabase 연결 테스트
    if not test_supabase_connection():
        return
    
    # video_id 목록 조회
    video_ids = get_all_video_ids()
    if not video_ids:
        print("❌ video_id가 없습니다.")
        return
    
    # 통계 변수
    total = len(video_ids)
    success_download = 0
    success_update = 0
    failed_videos = []
    
    print(f"📊 총 {total}개 영상 처리 시작")
    
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
            print("😴 20개 처리 완료. 5분 휴식...")
            time.sleep(300)
        else:
            time.sleep(random.uniform(2, 3))  # 2-3초 랜덤 딜레이
    
    # 결과 리포트
    print("\n" + "="*50)
    print("📊 자막 수집 결과 리포트")
    print("="*50)
    print(f"총 영상 수: {total}")
    print(f"다운로드 성공: {success_download}")
    print(f"DB 업데이트 성공: {success_update}")
    print(f"실패: {len(failed_videos)}")
    
    if failed_videos:
        print("\n❌ 실패 목록:")
        for failed in failed_videos:
            print(f"  - {failed}")
    
    print(f"\n✅ 자막 수집 작업 완료: {datetime.now()}")

if __name__ == "__main__":
    main()