#!/usr/bin/env python3
"""
간단한 테스트: 1개 채널, 1개 영상만 처리
"""
import json
import os
import sys
import ssl
import time
import subprocess
import urllib.request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

# 환경 설정
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
SUBS_DIR = r"C:\Users\Mario\work\subs"
SSL_CTX = ssl.create_default_context()

def supabase_get(table, params=""):
    """Supabase GET 요청"""
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}" if params else f"{SUPABASE_URL}/rest/v1/{table}"
    req = urllib.request.Request(url, headers={
        "apikey": ANON_KEY,
        "Authorization": f"Bearer {ANON_KEY}",
        "Content-Type": "application/json",
    })
    try:
        resp = urllib.request.urlopen(req, context=SSL_CTX)
        return json.loads(resp.read().decode())
    except Exception as e:
        print(f"DB Error: {e}")
        return []

def get_existing_video_ids():
    """DB에서 기존 video_id 목록 가져오기"""
    print("기존 video_id 확인중...")
    data = supabase_get("influencer_videos", "select=video_id")
    existing_ids = set([item['video_id'] for item in data])
    print(f"기존 영상: {len(existing_ids)}개")
    return existing_ids

def get_one_video():
    """부읽남TV에서 첫번째 영상 1개만 가져오기"""
    print("부읽남TV 첫번째 영상 가져오는중...")
    
    cmd = [
        "python", "-m", "yt_dlp", "--flat-playlist",
        "--print", "%(id)s|%(title)s|%(upload_date)s",
        "https://www.youtube.com/@buiknam_tv/videos",
        "--playlist-items", "1"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode != 0:
            safe_error = str(result.stderr).encode('ascii', 'ignore').decode('ascii')
            print(f"Error: {safe_error}")
            return None
        
        if result.stdout and result.stdout.strip():
            line = result.stdout.strip().split('\n')[0]
            if '|' in line:
                parts = line.split('|')
                video_id = parts[0]
                title = parts[1] if len(parts) > 1 else "Unknown"
                upload_date = parts[2] if len(parts) > 2 else None
                safe_title = title.encode('ascii', 'ignore').decode('ascii')
                print(f"Found: {video_id} - {safe_title}")
                return {
                    'video_id': video_id,
                    'title': title,
                    'upload_date': upload_date
                }
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def extract_transcript(video_id):
    """YouTube 자막 추출"""
    print(f"자막 추출: {video_id}")
    
    transcript_file = os.path.join(SUBS_DIR, f"{video_id}_transcript.json")
    if os.path.exists(transcript_file):
        print(f"이미 존재: {transcript_file}")
        return True
    
    try:
        # 한국어 자막 시도
        api = YouTubeTranscriptApi()
        transcript_obj = api.fetch(video_id, languages=['ko', 'ko-KR'])
        transcript = transcript_obj.fetch()
        
        # JSON 형식으로 저장
        subtitle_data = {
            "video_id": video_id,
            "subtitles": [
                {
                    "start": item.get('start', 0.0),
                    "duration": item.get('duration', 0.0),
                    "text": item.get('text', '')
                }
                for item in transcript
            ]
        }
        
        os.makedirs(SUBS_DIR, exist_ok=True)
        
        with open(transcript_file, 'w', encoding='utf-8') as f:
            json.dump(subtitle_data, f, ensure_ascii=False, indent=2)
        
        print(f"저장완료: {len(subtitle_data['subtitles'])}개 구간")
        return True
        
    except TranscriptsDisabled:
        print(f"자막 비활성화: {video_id}")
    except NoTranscriptFound:
        print(f"한국어 자막 없음: {video_id}")
    except Exception as e:
        print(f"자막 추출 에러: {e}")
    
    return False

def main():
    print("=== 간단 테스트 시작 ===")
    
    # 1. 기존 video_id 확인
    existing_ids = get_existing_video_ids()
    
    # 2. 1개 영상 가져오기
    video = get_one_video()
    if not video:
        print("영상을 가져올 수 없습니다.")
        return
    
    # 3. 이미 DB에 있는지 확인
    if video['video_id'] in existing_ids:
        print(f"이미 DB에 있음: {video['video_id']}")
    else:
        print(f"새로운 영상: {video['video_id']}")
    
    # 4. 자막 추출 테스트
    success = extract_transcript(video['video_id'])
    
    if success:
        print("[OK] 자막 추출 성공")
        
        # 5. pipeline_v9.py 실행 테스트
        print("pipeline_v9.py 실행 테스트...")
        try:
            result = subprocess.run([
                "python", "pipeline_v9.py"
            ], capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=60)
            
            if result.returncode == 0:
                print("[OK] 파이프라인 실행 완료")
                print("출력:", result.stdout[:500])  # 처음 500자만
            else:
                print("[ERROR] 파이프라인 에러:")
                print("stderr:", result.stderr[:500])
        
        except subprocess.TimeoutExpired:
            print("파이프라인 타임아웃 (60초)")
        except Exception as e:
            print(f"파이프라인 실행 에러: {e}")
    else:
        print("[ERROR] 자막 추출 실패")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    main()