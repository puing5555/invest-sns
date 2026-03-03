#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
단일 영상 자막 다운로드 테스트
"""

import subprocess
import time
from pathlib import Path

# 테스트할 video_id (첫 번째 영상)
video_id = "Ke7gQMbIFLI"
print(f"테스트 영상: {video_id}")

# subs 디렉토리 생성
subs_dir = Path("subs")
subs_dir.mkdir(exist_ok=True)
print("subs 디렉토리 준비 완료")

# yt-dlp 명령어 실행
url = f"https://youtube.com/watch?v={video_id}"
cmd = [
    "python", "-m", "yt_dlp",
    "--write-auto-sub",
    "--sub-lang", "ko",
    "--skip-download",
    "-o", f"subs/{video_id}",
    url
]

print(f"실행할 명령어: {' '.join(cmd)}")
print("yt-dlp 실행 중...")

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    print(f"반환코드: {result.returncode}")
    print(f"stdout: {result.stdout}")
    print(f"stderr: {result.stderr}")
    
    # VTT 파일 확인
    vtt_file = Path(f"subs/{video_id}.ko.vtt")
    if vtt_file.exists():
        print(f"[OK] VTT 파일 생성 성공: {vtt_file}")
        print(f"파일 크기: {vtt_file.stat().st_size} bytes")
        
        # 파일 내용 일부 확인
        with open(vtt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"내용 길이: {len(content)} 문자")
            print("첫 500자:")
            print(content[:500])
    else:
        print(f"[ERROR] VTT 파일이 생성되지 않았습니다: {vtt_file}")
        
except subprocess.TimeoutExpired:
    print("[ERROR] 타임아웃 발생 (120초)")
except Exception as e:
    print(f"[ERROR] 예외 발생: {e}")

print("테스트 완료")