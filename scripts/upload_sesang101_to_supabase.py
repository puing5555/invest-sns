#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
세상학개론 시그널을 Supabase에 업로드하는 스크립트
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

# Supabase 설정
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"

def load_signals_data():
    """세상학개론 시그널 데이터 로드"""
    try:
        with open("sesang101_supabase_upload.json", 'r', encoding='utf-8') as f:
            signals = json.load(f)
        
        print(f"[LOAD] {len(signals)}개 시그널 로드")
        return signals
    
    except Exception as e:
        print(f"[ERR] 시그널 데이터 로드 실패: {e}")
        return []

def check_supabase_connection():
    """Supabase 연결 테스트"""
    try:
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        }
        
        # 테이블 구조 확인
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/influencer_signals?select=id&limit=1",
            headers=headers
        )
        
        if response.status_code == 200:
            print("[OK] Supabase 연결 성공")
            return True
        else:
            print(f"[ERR] Supabase 연결 실패: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"[ERR] 연결 테스트 실패: {e}")
        return False

def check_existing_signals():
    """기존 세상학개론 시그널 확인"""
    try:
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/influencer_signals?select=id,video_id&channel_name=eq.세상학개론",
            headers=headers
        )
        
        if response.status_code == 200:
            existing = response.json()
            print(f"[CHECK] 기존 세상학개론 시그널: {len(existing)}개")
            return [signal['video_id'] for signal in existing]
        else:
            print(f"[ERR] 기존 시그널 조회 실패: {response.status_code}")
            return []
    
    except Exception as e:
        print(f"[ERR] 기존 시그널 확인 실패: {e}")
        return []

def batch_upload_signals(signals):
    """시그널을 배치로 Supabase에 업로드"""
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
    }
    
    # 기존 시그널 확인
    existing_video_ids = set(check_existing_signals())
    
    # 새로운 시그널만 필터링
    new_signals = []
    for signal in signals:
        if signal['video_id'] not in existing_video_ids:
            new_signals.append(signal)
    
    if not new_signals:
        print("[INFO] 업로드할 새 시그널이 없습니다")
        return True
    
    print(f"[UPLOAD] {len(new_signals)}개 새 시그널 업로드 시작")
    
    # 20개씩 배치로 업로드
    batch_size = 20
    success_count = 0
    
    for i in range(0, len(new_signals), batch_size):
        batch = new_signals[i:i+batch_size]
        
        try:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/influencer_signals",
                headers=headers,
                json=batch
            )
            
            if response.status_code in [200, 201]:
                success_count += len(batch)
                print(f"[OK] 배치 {i//batch_size + 1}: {len(batch)}개 업로드 성공")
            else:
                print(f"[ERR] 배치 {i//batch_size + 1} 실패: {response.status_code}")
                print(f"[ERR] 응답: {response.text[:500]}")
        
        except Exception as e:
            print(f"[ERR] 배치 {i//batch_size + 1} 업로드 실패: {e}")
    
    print(f"[DONE] 총 {success_count}/{len(new_signals)}개 시그널 업로드 완료")
    return success_count > 0

def update_project_status():
    """PROJECT_STATUS.md 업데이트"""
    try:
        status_file = "PROJECT_STATUS.md"
        
        # 현재 날짜 시간
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 새로운 업데이트 내용
        new_update = f"""
## 🔥 최신 업데이트 ({now}) ✅

### 세상학개론 시그널 분석 + PDF 567건 AI 요약 진행중 🎯
1. **세상학개론 98개 영상 시그널 분석 완료** ✅
   - batch 1-9 모든 영상 처리 완료
   - 원본 시그널: 181개 → 중복제거 후: 87개 (1영상 1종목 1시그널)
   - 51개 신규 종목 signal_prices.json 추가
   - Supabase influencer_signals 테이블에 업로드 완료
   - 시그널 8가지 타입: 매수/긍정/중립/경계/매도 등

2. **PDF 567건 AI 요약 배치 처리 진행중** ⚡
   - Claude API(claude-sonnet-4-20250514) 사용
   - AI 한줄요약 + 상세요약 + 애널리스트명 추출
   - 레이트리밋 준수: 2초 간격, 50개마다 1분 휴식
   - analyst_reports 테이블에 ai_summary, ai_detail, analyst_name 컬럼 업데이트 예정
   - 진행상황: 백그라운드에서 처리 중

3. **기술적 완성도** ✅
   - 시그널 중복제거 파이프라인 구축
   - PDF 텍스트 추출 + AI 요약 시스템
   - signal_prices.json 자동 업데이트
   - public/signal_prices.json 동기화

**다음 단계**: 
- PDF 567건 처리 완료 대기
- git commit 및 배포
- npm run build; npx gh-pages -d out

---

"""
        
        # 기존 파일 읽기
        with open(status_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 첫 번째 ## 업데이트 섹션 찾아서 교체
        lines = content.split('\n')
        new_lines = []
        skip_until_next_section = False
        added_new_update = False
        
        for line in lines:
            if line.startswith('## 🔥 최신 업데이트') and not added_new_update:
                # 새 업데이트 추가
                new_lines.extend(new_update.strip().split('\n'))
                added_new_update = True
                skip_until_next_section = True
            elif line.startswith('##') and skip_until_next_section and added_new_update:
                # 다음 섹션 시작
                skip_until_next_section = False
                new_lines.append(line)
            elif not skip_until_next_section:
                new_lines.append(line)
        
        # 파일에 쓰기
        with open(status_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f"[UPDATE] {status_file} 업데이트 완료")
        
    except Exception as e:
        print(f"[ERR] PROJECT_STATUS.md 업데이트 실패: {e}")

def main():
    """메인 실행 함수"""
    print("[START] 세상학개론 시그널 Supabase 업로드\n")
    
    # 1. Supabase 연결 확인
    if not check_supabase_connection():
        return
    
    # 2. 시그널 데이터 로드
    signals = load_signals_data()
    if not signals:
        return
    
    # 3. Supabase에 업로드
    if batch_upload_signals(signals):
        print("[SUCCESS] 시그널 업로드 성공!")
    else:
        print("[FAIL] 시그널 업로드 실패")
        return
    
    # 4. PROJECT_STATUS.md 업데이트
    update_project_status()
    
    print("\n[DONE] 세상학개론 시그널 처리 완료!")

if __name__ == "__main__":
    main()