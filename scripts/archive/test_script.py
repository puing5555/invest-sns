#!/usr/bin/env python3
"""
AI Detail 테스트 스크립트
"""

import json
import os
from pathlib import Path
import time
from anthropic import Anthropic

print("스크립트 시작!")

# 설정
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
print(f"API 키 존재: {ANTHROPIC_API_KEY is not None}")

if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")

client = Anthropic(api_key=ANTHROPIC_API_KEY)
print("Anthropic 클라이언트 생성 완료")

WORK_DIR = Path("C:/Users/Mario/work/invest-sns")
DATA_DIR = WORK_DIR / "data"
ANALYST_REPORTS_FILE = DATA_DIR / "analyst_reports.json"
PROGRESS_FILE = DATA_DIR / "ai_detail_progress.json"

print(f"작업 디렉토리: {WORK_DIR}")
print(f"데이터 디렉토리: {DATA_DIR}")
print(f"리포트 파일: {ANALYST_REPORTS_FILE}")
print(f"진행 파일: {PROGRESS_FILE}")

# 파일 존재 확인
print(f"리포트 파일 존재: {ANALYST_REPORTS_FILE.exists()}")
print(f"진행 파일 존재: {PROGRESS_FILE.exists()}")

if ANALYST_REPORTS_FILE.exists():
    with open(ANALYST_REPORTS_FILE, 'r', encoding='utf-8') as f:
        reports_data = json.load(f)
    
    print(f"총 종목 수: {len(reports_data)}")
    
    total_reports = 0
    for ticker, reports in reports_data.items():
        for report in reports:
            if report.get('ai_detail'):
                total_reports += 1
    
    print(f"ai_detail이 있는 총 리포트 수: {total_reports}")

print("테스트 완료!")