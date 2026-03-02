#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
세상학개론 시그널을 Supabase에 업로드하는 스크립트 (수정버전)
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

# 세상학개론 ID
SESANG101_CHANNEL_ID = "d68f8efd-64c8-4c07-9d34-e98c2954f4e1"
SESANG101_SPEAKER_ID = "b9496a5f-06fa-47eb-bc2d-47060b095534"

def load_signals_data():
    """세상학개론 시그널 데이터 로드"""
    try:
        with open("sesang101_final_signals.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        signals = data.get('signals', [])
        print(f"[LOAD] {len(signals)}개 시그널 로드")
        return signals
    
    except Exception as e:
        print(f"[ERR] 시그널 데이터 로드 실패: {e}")
        return []

def create_video_records_if_needed(signals):
    """영상 레코드가 없으면 생성"""
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    # 고유한 video_id 목록 추출
    video_ids = list(set(signal['video_id'] for signal in signals if signal.get('video_id')))
    
    print(f"[VIDEO] {len(video_ids)}개 고유 영상 처리")
    
    created_count = 0
    
    for video_id in video_ids:
        try:
            # 기존 영상 확인
            check_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/influencer_videos?video_id=eq.{video_id}",
                headers={k: v for k, v in headers.items() if k != 'Prefer'}
            )
            
            if check_response.status_code == 200:
                existing = check_response.json()
                if existing:
                    continue  # 이미 존재함
            
            # 영상 제목 찾기
            video_title = next(
                (signal['video_title'] for signal in signals if signal['video_id'] == video_id),
                f"세상학개론 영상 {video_id}"
            )
            
            # 영상 레코드 생성
            video_data = {
                "video_id": video_id,
                "channel_id": SESANG101_CHANNEL_ID,
                "title": video_title,
                "published_at": "2026-03-02T00:00:00Z",
                "pipeline_version": "V9",
                "signal_count": len([s for s in signals if s['video_id'] == video_id]),
                "has_subtitle": True,
                "subtitle_language": "ko"
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/influencer_videos",
                headers=headers,
                json=video_data
            )
            
            if response.status_code in [200, 201]:
                created_count += 1
                print(f"[CREATE] 영상 생성: {video_id}")
            else:
                print(f"[WARN] 영상 생성 실패 {video_id}: {response.status_code}")
        
        except Exception as e:
            print(f"[ERR] 영상 처리 실패 {video_id}: {e}")
    
    print(f"[VIDEO] {created_count}개 영상 레코드 생성")

def transform_signals_for_upload(signals):
    """시그널 데이터를 Supabase 형식으로 변환"""
    transformed = []
    
    for signal in signals:
        # 한글 시그널을 영문으로 매핑
        signal_mapping = {
            '매수': 'BUY',
            '강력매수': 'STRONG_BUY', 
            '긍정': 'POSITIVE',
            '중립': 'NEUTRAL',
            '경계': 'CONCERN',
            '매도': 'SELL',
            '강력매도': 'STRONG_SELL'
        }
        
        transformed_signal = {
            "video_id": signal.get('video_id'),
            "speaker_id": SESANG101_SPEAKER_ID,
            "stock": signal.get('stock'),
            "ticker": signal.get('ticker'),
            "market": signal.get('market', 'KR'),
            "mention_type": signal.get('mention_type', '분석'),
            "signal": signal_mapping.get(signal.get('signal'), signal.get('signal', 'NEUTRAL')),
            "confidence": signal.get('confidence', 'medium'),
            "timestamp": signal.get('timestamp', '전반부'),
            "key_quote": signal.get('key_quote', ''),
            "reasoning": signal.get('reasoning', ''),
            "pipeline_version": "V9",
            "review_status": "pending"
        }
        
        transformed.append(transformed_signal)
    
    return transformed

def check_existing_signals():
    """기존 세상학개론 시그널 확인"""
    try:
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/influencer_signals?speaker_id=eq.{SESANG101_SPEAKER_ID}&select=id,video_id,stock",
            headers=headers
        )
        
        if response.status_code == 200:
            existing = response.json()
            print(f"[CHECK] 기존 세상학개론 시그널: {len(existing)}개")
            # video_id + stock 조합으로 중복 확인
            existing_keys = set(f"{signal['video_id']}_{signal['stock']}" for signal in existing)
            return existing_keys
        else:
            print(f"[ERR] 기존 시그널 조회 실패: {response.status_code}")
            return set()
    
    except Exception as e:
        print(f"[ERR] 기존 시그널 확인 실패: {e}")
        return set()

def batch_upload_signals(signals):
    """시그널을 배치로 Supabase에 업로드"""
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    # 1. 영상 레코드 생성
    create_video_records_if_needed(signals)
    
    # 2. 시그널 변환
    transformed_signals = transform_signals_for_upload(signals)
    
    # 3. 기존 시그널 확인
    existing_keys = check_existing_signals()
    
    # 4. 새로운 시그널만 필터링
    new_signals = []
    for signal in transformed_signals:
        key = f"{signal['video_id']}_{signal['stock']}"
        if key not in existing_keys:
            new_signals.append(signal)
    
    if not new_signals:
        print("[INFO] 업로드할 새 시그널이 없습니다")
        return True
    
    print(f"[UPLOAD] {len(new_signals)}개 새 시그널 업로드 시작")
    
    # 5. 20개씩 배치로 업로드
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

def main():
    """메인 실행 함수"""
    print("[START] 세상학개론 시그널 Supabase 업로드 (수정버전)\n")
    
    # 1. 시그널 데이터 로드
    signals = load_signals_data()
    if not signals:
        return
    
    # 2. Supabase에 업로드
    if batch_upload_signals(signals):
        print("[SUCCESS] 시그널 업로드 성공!")
    else:
        print("[FAIL] 시그널 업로드 실패")
        return
    
    print("\n[DONE] 세상학개론 시그널 처리 완료!")

if __name__ == "__main__":
    main()