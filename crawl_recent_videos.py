#!/usr/bin/env python3
"""
작업 3: 최근 영상 크롤링 (2025-10~2026-02)
- yt-dlp로 세상학개론 채널 최근 영상 목록 가져오기
- 기존 98개와 비교해서 빠진 영상 확인
- 빠진 영상 자막 다운로드
- fast_analyzer.py로 분석 후 Supabase INSERT
"""
import os
import json
import subprocess
import glob
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv('.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
SESANG_CHANNEL_ID = "d68f8efd-64c8-4c07-9d34-e98c2954f4e1"

# 세상학개론 YouTube 채널 URL
SESANG_YOUTUBE_URL = "https://www.youtube.com/@sesangschool"
SESANG_YOUTUBE_CHANNEL_ID = "UCQ0n3PkX9z1qJJbPi6YfAFw"  # 실제 채널 ID

SUPABASE_HEADERS = {
    'apikey': SERVICE_ROLE_KEY,
    'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
    'Content-Type': 'application/json'
}

def get_existing_videos():
    """기존에 있는 세상학개론 영상 ID 조회"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_videos"
    params = {
        'channel_id': f'eq.{SESANG_CHANNEL_ID}',
        'select': 'video_id,title,published_at'
    }
    
    response = requests.get(url, headers=SUPABASE_HEADERS, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting existing videos: {response.status_code}")
        return []

def get_channel_videos_with_ytdlp():
    """yt-dlp로 채널의 최근 영상 목록 가져오기"""
    print("📺 Fetching recent videos from Sesang101 channel...")
    
    # 2025년 10월부터 2026년 2월까지의 영상만 가져오기
    cmd = [
        'python', '-m', 'yt_dlp',
        '--flat-playlist',
        '--print', '%(id)s|%(title)s|%(upload_date)s|%(duration)s',
        '--dateafter', '20251001',  # 2025-10-01 이후
        '--datebefore', '20260301',  # 2026-03-01 이전
        SESANG_YOUTUBE_URL
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f"yt-dlp error: {result.stderr}")
            return []
        
        videos = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    video_id = parts[0]
                    title = parts[1]
                    upload_date = parts[2]
                    duration = parts[3] if len(parts) > 3 else None
                    
                    # 날짜 파싱
                    try:
                        published_at = datetime.strptime(upload_date, '%Y%m%d')
                    except:
                        published_at = None
                    
                    videos.append({
                        'video_id': video_id,
                        'title': title,
                        'published_at': published_at,
                        'duration': duration
                    })
        
        return videos
        
    except Exception as e:
        print(f"Error running yt-dlp: {e}")
        return []

def download_subtitle(video_id):
    """특정 영상의 자막 다운로드"""
    print(f"  📝 Downloading subtitle for {video_id}...")
    
    cmd = [
        'python', '-m', 'yt_dlp',
        '--write-auto-sub',
        '--sub-lang', 'ko',
        '--skip-download',
        '-o', f'../subs/sesang101/{video_id}.%(ext)s',
        f'https://www.youtube.com/watch?v={video_id}'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        # .vtt 파일을 .json으로 변환
        vtt_files = glob.glob(f'../subs/sesang101/{video_id}*.vtt')
        if vtt_files:
            vtt_file = vtt_files[0]
            json_file = f'../subs/sesang101/{video_id}.json'
            
            # VTT to JSON 변환 (간단한 방법)
            with open(vtt_file, 'r', encoding='utf-8') as f:
                vtt_content = f.read()
            
            # VTT 파싱하여 JSON으로 변환
            subtitle_entries = parse_vtt_to_json(vtt_content)
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(subtitle_entries, f, ensure_ascii=False, indent=1)
            
            # VTT 파일 삭제
            os.remove(vtt_file)
            
            print(f"    ✓ Subtitle saved: {json_file}")
            return True
        else:
            print(f"    ✗ No subtitle file found")
            return False
            
    except Exception as e:
        print(f"    Error downloading subtitle: {e}")
        return False

def parse_vtt_to_json(vtt_content):
    """VTT 내용을 JSON 형태로 파싱"""
    entries = []
    lines = vtt_content.split('\n')
    
    current_text = ""
    current_start = 0
    
    for line in lines:
        line = line.strip()
        
        # 타임스탬프 라인 (예: "00:00:01.000 --> 00:00:03.500")
        if ' --> ' in line:
            timestamps = line.split(' --> ')
            if len(timestamps) == 2:
                start_time = parse_timestamp(timestamps[0])
                if start_time is not None:
                    current_start = start_time
        
        # 텍스트 라인 (타임스탬프도 숫자도 아닌 것)
        elif line and not line.startswith('WEBVTT') and not line.startswith('NOTE') and not line.isdigit():
            # HTML 태그 제거
            clean_text = line.replace('<c>', '').replace('</c>', '').strip()
            if clean_text and clean_text not in ['&nbsp;', '']:
                current_text = clean_text
                
                # 엔트리 추가
                entries.append({
                    'text': current_text,
                    'start': current_start,
                    'duration': 3.0  # 기본값
                })
    
    return entries

def parse_timestamp(timestamp_str):
    """VTT 타임스탬프를 초로 변환"""
    try:
        # "00:00:01.000" 형태
        parts = timestamp_str.split(':')
        if len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds_parts = parts[2].split('.')
            seconds = int(seconds_parts[0])
            milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
            
            total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
            return total_seconds
    except:
        pass
    return None

def run_fast_analyzer(video_ids):
    """fast_analyzer.py로 새로운 영상들 분석"""
    if not video_ids:
        return
    
    print(f"🤖 Analyzing {len(video_ids)} new videos with fast_analyzer.py...")
    
    # fast_analyzer.py 실행
    cmd = [
        'python', 'scripts/fast_analyzer.py',
        '--video-ids', ','.join(video_ids),
        '--speaker-id', 'b9496a5f-06fa-47eb-bc2d-47060b095534',
        '--channel-id', 'd68f8efd-64c8-4c07-9d34-e98c2954f4e1'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ Fast analysis completed")
            print(result.stdout)
        else:
            print(f"❌ Fast analysis failed: {result.stderr}")
            
    except Exception as e:
        print(f"Error running fast_analyzer.py: {e}")

def main():
    print("🎬 Starting recent video crawling for Sesang101...")
    
    # 1. 기존 영상 목록 조회
    existing_videos = get_existing_videos()
    existing_video_ids = set(video['video_id'] for video in existing_videos)
    
    print(f"📊 Found {len(existing_videos)} existing videos in database")
    
    # 2. yt-dlp로 최근 영상 목록 가져오기  
    recent_videos = get_channel_videos_with_ytdlp()
    
    if not recent_videos:
        print("❌ No recent videos found")
        return
    
    print(f"📺 Found {len(recent_videos)} recent videos from channel")
    
    # 3. 빠진 영상 찾기
    missing_videos = []
    for video in recent_videos:
        if video['video_id'] not in existing_video_ids:
            missing_videos.append(video)
    
    print(f"🆕 Found {len(missing_videos)} missing videos:")
    for video in missing_videos:
        date_str = video['published_at'].strftime('%Y-%m-%d') if video['published_at'] else 'Unknown'
        print(f"  {video['video_id']}: {video['title']} ({date_str})")
    
    if not missing_videos:
        print("✅ No missing videos found!")
        return
    
    # 4. 빠진 영상들의 자막 다운로드
    print(f"\n📝 Downloading subtitles for {len(missing_videos)} videos...")
    downloaded_video_ids = []
    
    for video in missing_videos:
        video_id = video['video_id']
        if download_subtitle(video_id):
            downloaded_video_ids.append(video_id)
    
    print(f"✅ Downloaded {len(downloaded_video_ids)} subtitles")
    
    # 5. fast_analyzer.py로 분석
    if downloaded_video_ids:
        run_fast_analyzer(downloaded_video_ids)
    
    # 결과 저장
    result = {
        'existing_videos': len(existing_videos),
        'recent_videos': len(recent_videos),
        'missing_videos': len(missing_videos),
        'downloaded_subtitles': len(downloaded_video_ids),
        'missing_video_list': [
            {
                'video_id': video['video_id'],
                'title': video['title'],
                'published_at': video['published_at'].strftime('%Y-%m-%d') if video['published_at'] else None
            }
            for video in missing_videos
        ],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open('recent_video_crawl_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 Crawling completed!")
    print(f"  Results saved to recent_video_crawl_result.json")

if __name__ == "__main__":
    main()