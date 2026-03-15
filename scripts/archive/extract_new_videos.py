#!/usr/bin/env python3
"""
추가 영상 자막 추출 및 V9.1 분석 파이프라인
목표: 시그널 100개+ 달성 (현재 78개 → 22개+ 추가)
"""
import json
import os
import sys
import ssl
import time
import random
import subprocess
import urllib.request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

# 환경 설정
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
SUBS_DIR = r"C:\Users\Mario\work\subs"
SSL_CTX = ssl.create_default_context()

# 채널 정보 (작동하는 채널들만)
CHANNELS = [
    {"name": "부읽남TV", "handle": "@buiknam_tv", "current_count": 7},
    {"name": "삼프로TV", "handle": "@3protv", "current_count": 20},
    # 추후 정확한 핸들 확인 후 추가:
    # {"name": "이효석아카데미", "handle": "?", "current_count": 9},
    # {"name": "달란트투자", "handle": "?", "current_count": 4},
    # {"name": "슈카월드", "handle": "?", "current_count": 17},
    # {"name": "코린이아빠", "handle": "?", "current_count": 11}
]

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
        print(f"  DB Error: {e}")
        return []

def get_existing_video_ids():
    """DB에서 기존 video_id 목록 가져오기"""
    print("[DB] DB에서 기존 video_id 목록 확인 중...")
    data = supabase_get("influencer_videos", "select=video_id")
    existing_ids = set([item['video_id'] for item in data])
    print(f"  기존 영상: {len(existing_ids)}개")
    return existing_ids

def get_channel_videos(channel_handle, max_videos=15):
    """채널의 최신 영상 목록 가져오기 (yt-dlp 사용)"""
    print(f"[VIDEO] {channel_handle} 채널 영상 목록 가져오는 중...")
    
    try:
        # yt-dlp로 영상 목록 가져오기
        cmd = [
            "python", "-m", "yt_dlp", "--flat-playlist",
            "--print", "%(id)s|%(title)s|%(upload_date)s",
            f"https://www.youtube.com/{channel_handle}/videos",
            "--playlist-items", f"1-{max_videos}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode != 0:
            print(f"  [ERROR] yt-dlp 에러: {result.stderr}")
            return []
        
        videos = []
        if result.stdout and result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        video_id = parts[0]
                        title = parts[1]
                        upload_date = parts[2] if len(parts) > 2 else None
                        videos.append({
                            'video_id': video_id,
                            'title': title,
                            'upload_date': upload_date
                        })
        
        print(f"  찾은 영상: {len(videos)}개")
        return videos
        
    except Exception as e:
        print(f"  [ERROR] 에러: {e}")
        return []

def extract_transcript(video_id):
    """YouTube 자막 추출"""
    print(f"[TRANSCRIPT] {video_id} 자막 추출 중...")
    
    # 이미 있는지 확인
    transcript_file = os.path.join(SUBS_DIR, f"{video_id}_transcript.json")
    if os.path.exists(transcript_file):
        print(f"  [SKIP] 자막 파일 이미 존재: {transcript_file}")
        return True
    
    try:
        # 한국어 자막 우선 시도
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'ko-KR'])
        
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
        
        # subs 디렉토리 생성
        os.makedirs(SUBS_DIR, exist_ok=True)
        
        # 파일 저장
        with open(transcript_file, 'w', encoding='utf-8') as f:
            json.dump(subtitle_data, f, ensure_ascii=False, indent=2)
        
        print(f"  [OK] 자막 저장됨: {len(subtitle_data['subtitles'])}개 구간")
        return True
        
    except TranscriptsDisabled:
        print(f"  [ERROR] 자막이 비활성화됨: {video_id}")
    except NoTranscriptFound:
        print(f"  [ERROR] 한국어 자막이 없음: {video_id}")
    except Exception as e:
        print(f"  [ERROR] 자막 추출 에러: {e}")
    
    return False

def rate_limit_delay():
    """레이트 리밋 딜레이"""
    delay = random.uniform(2.0, 3.5)  # 2-3.5초 랜덤 딜레이
    print(f"  [WAIT] {delay:.1f}초 대기...")
    time.sleep(delay)

def main():
    print("[START] 추가 영상 자막 추출 + V9.1 분석 파이프라인 시작")
    print("[GOAL] 목표: 시그널 100개+ 달성 (현재 78개 -> 22개+ 추가)")
    print("=" * 60)
    
    # 1단계: 기존 video_id 확인
    existing_ids = get_existing_video_ids()
    
    new_videos_found = []
    transcripts_extracted = 0
    
    # 2단계: 각 채널별 최신 영상 가져오기
    for channel in CHANNELS:
        print(f"\n[CHANNEL] {channel['name']} ({channel['handle']}) 처리 중...")
        
        # 영상 목록 가져오기
        videos = get_channel_videos(channel['handle'])
        
        # 새 영상 필터링
        new_videos = []
        for video in videos:
            if video['video_id'] not in existing_ids:
                new_videos.append(video)
        
        print(f"  새로운 영상: {len(new_videos)}개")
        
        if new_videos:
            # 자막 추출
            for i, video in enumerate(new_videos):
                safe_title = video['title'][:50].encode('ascii', 'ignore').decode('ascii')
                print(f"\n  [{i+1}/{len(new_videos)}] {safe_title}...")
                
                # 자막 추출
                if extract_transcript(video['video_id']):
                    video['channel_name'] = channel['name']
                    video['channel_handle'] = channel['handle']
                    new_videos_found.append(video)
                    transcripts_extracted += 1
                    
                    # 20개마다 5분 휴식
                    if transcripts_extracted > 0 and transcripts_extracted % 20 == 0:
                        print(f"  [BREAK] 20개 처리 완료, 5분 휴식...")
                        time.sleep(300)  # 5분
                
                # 레이트 리밋
                rate_limit_delay()
    
    # 결과 요약
    print(f"\n[SUMMARY] 1차 결과 요약:")
    print(f"  총 찾은 새 영상: {len(new_videos_found)}개")
    print(f"  자막 추출 성공: {transcripts_extracted}개")
    
    if new_videos_found:
        print(f"\n[BREAKDOWN] 채널별 breakdown:")
        channel_counts = {}
        for video in new_videos_found:
            channel = video['channel_name']
            channel_counts[channel] = channel_counts.get(channel, 0) + 1
        
        for channel, count in channel_counts.items():
            print(f"  - {channel}: {count}개")
        
        # V9.1 파이프라인 실행
        print(f"\n[PIPELINE] V9.1 파이프라인으로 분석 시작...")
        try:
            result = subprocess.run([
                "python", "pipeline_v9.py"
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                print("  [OK] 파이프라인 실행 완료")
                print("  [OUTPUT] 출력:")
                print(result.stdout)
            else:
                print("  [ERROR] 파이프라인 에러:")
                print(result.stderr)
        
        except Exception as e:
            print(f"  [ERROR] 파이프라인 실행 중 에러: {e}")
    
    else:
        print("  [INFO] 새로운 영상이 없습니다.")
    
    print(f"\n[COMPLETE] 작업 완료!")

if __name__ == "__main__":
    main()