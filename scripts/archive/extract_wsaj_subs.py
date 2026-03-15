#!/usr/bin/env python3
"""
월가아재(wsaj) 기업해부학 시리즈 자막 추출 스크립트
"""

import subprocess
import time
import sys
from pathlib import Path

# 나머지 12개 영상 ID와 제목 (이미 처리된 3개 제외)
video_list = [
    ("OWkw56VyeUM", "엔비디아 고점 논란, 가치평가 대가가 판 이유"),
    ("liP35sqr9aU", "엔비디아 실적 서프라이즈"),
    ("7x3HE_uXttI", "AI 수혜주 파헤치기"),
    ("tUv4-8BihrM", "AI 관련주, 골드만삭스 리포트"),
    ("l9suWlP7U68", "테슬라 = AI 대장주?"),
    ("_Ex0vR_1Ekg", "테슬라 목표가"),
    ("0pS0CTDgVmU", "Amazon 3Q 2023 어닝콜"),
    ("B17xc8zl3Z4", "Meta 3Q 2023 어닝콜"),
    ("sade4GuojTg", "IPO Arm 투자 체크포인트"),
    ("EbfuT0zGGjU", "IPO 공모주 투자 3가지 포인트"),
    ("57NbdmLvy6I", "노보 노디스크 & 일라이 릴리"),
    ("dPIjOdREB80", "찰스 슈왑 (1부)"),
    ("PzpU0H8iqQs", "찰스 슈왑 (2부)")
]

def extract_subtitle(video_id, title, delay=3):
    """단일 영상 자막 추출"""
    print(f"\n[EXTRACT] Processing: {title} ({video_id})")
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    cmd = [
        "python", "-m", "yt_dlp",
        "--write-auto-subs", 
        "--skip-download",
        "--sub-langs", "ko,ko-orig,kr,kr-orig",
        "--sub-format", "vtt",
        "--output", "subs/wsaj_%(id)s_%(title)s.%(ext)s",
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
        if result.returncode == 0:
            print(f"[SUCCESS] {title}")
        else:
            print(f"[ERROR] {title}")
            print(f"Error details: {result.stderr}")
        
        # 레이트 리밋 준수
        if delay > 0:
            print(f"[WAIT] Sleeping {delay} seconds...")
            time.sleep(delay)
            
    except Exception as e:
        print(f"[EXCEPTION] {title} - {str(e)}")

def main():
    """메인 실행 함수"""
    print("WSAJ Corporate Analysis Series Subtitle Extraction Started")
    print(f"Target videos: {len(video_list)}")
    
    for i, (video_id, title) in enumerate(video_list, 1):
        print(f"\nProgress: {i}/{len(video_list)}")
        
        # 20개마다 5분 휴식 (요구사항에 따라)
        if i > 0 and i % 20 == 0:
            print(f"\n20 videos processed! Taking 5 minute break...")
            time.sleep(300)  # 5분
        
        extract_subtitle(video_id, title, delay=3)
    
    print(f"\nAll subtitle extraction completed!")

if __name__ == "__main__":
    main()