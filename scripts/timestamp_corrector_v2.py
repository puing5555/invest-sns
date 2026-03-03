#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
timestamp_corrector_v2.py - 타임스탬프 전수 교정 도구 (DB 구조 맞춤)
- influencer_signals + influencer_videos JOIN으로 데이터 가져오기
- MM:SS 형식 타임스탬프를 초 단위로 변환
- yt-dlp로 자막 추출하여 key_quote 매칭
- 30초 이상 차이나면 교정
"""

import os
import re
import json
import time
import random
import asyncio
import subprocess
import tempfile
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env.local')

# 설정
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

# 레이트리밋 설정
MIN_DELAY = 2
MAX_DELAY = 3
RETRY_WAIT = 60
BATCH_SIZE = 20
BATCH_BREAK = 300  # 5분

class TimestampCorrectorV2:
    def __init__(self):
        self.headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        self.processed_count = 0
        self.corrected_count = 0
        self.failed_count = 0
        self.results = []
        
    def timestamp_to_seconds(self, timestamp_str: str) -> int:
        """MM:SS 또는 HH:MM:SS 형식을 초 단위로 변환"""
        if not timestamp_str or ':' not in timestamp_str:
            return 0
        
        parts = timestamp_str.split(':')
        try:
            if len(parts) == 2:  # MM:SS
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
        except ValueError:
            pass
        
        return 0
    
    def seconds_to_timestamp(self, seconds: int) -> str:
        """초 단위를 MM:SS 형식으로 변환"""
        if seconds < 3600:  # 1시간 미만
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}:{secs:02d}"
        else:  # 1시간 이상
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}:{minutes:02d}:{secs:02d}"
    
    async def get_subtitles_from_yt_dlp(self, video_id: str) -> Optional[List[Dict]]:
        """yt-dlp로 자막 추출"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                output_template = os.path.join(temp_dir, f"{video_id}.%(ext)s")
                
                # yt-dlp 명령어 실행
                cmd = [
                    'yt-dlp',
                    '--write-auto-subs',
                    '--write-subs',
                    '--sub-lang', 'ko,en',
                    '--sub-format', 'json3',
                    '--skip-download',
                    '--output', output_template,
                    f'https://www.youtube.com/watch?v={video_id}'
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=60,
                    encoding='utf-8',
                    errors='ignore'
                )
                
                if result.returncode == 0:
                    # 자막 파일 찾기
                    for ext in ['.ko.json3', '.en.json3', '.json3']:
                        subtitle_file = output_template.replace('.%(ext)s', ext)
                        if os.path.exists(subtitle_file):
                            with open(subtitle_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                return data.get('events', [])
                
                return None
                
        except Exception as e:
            print(f"    yt-dlp 오류: {e}")
            return None
    
    def find_quote_timestamp(self, subtitles: List[Dict], key_quote: str) -> Optional[int]:
        """자막에서 key_quote 텍스트를 찾아 타임스탬프 반환"""
        if not subtitles or not key_quote:
            return None
        
        # key_quote 정규화 (공백, 특수문자 제거)
        normalized_quote = re.sub(r'[^\w가-힣]', '', key_quote.lower())
        
        if len(normalized_quote) < 5:  # 너무 짧으면 스킵
            return None
        
        # 자막 텍스트 구성
        subtitle_segments = []
        
        for event in subtitles:
            if 'segs' in event:
                start_time = event.get('tStartMs', 0) / 1000  # ms -> s
                for seg in event['segs']:
                    text = seg.get('utf8', '')
                    if text:
                        subtitle_segments.append({
                            'text': text,
                            'timestamp': int(start_time)
                        })
        
        # 연속된 텍스트로 합치고 위치-타임스탬프 매핑 생성
        full_text = ""
        position_to_timestamp = {}
        
        for seg in subtitle_segments:
            start_pos = len(full_text)
            full_text += seg['text']
            end_pos = len(full_text)
            
            # 이 텍스트 범위의 타임스탬프 기록
            for pos in range(start_pos, end_pos):
                position_to_timestamp[pos] = seg['timestamp']
        
        # 정규화된 자막 텍스트
        normalized_subtitle = re.sub(r'[^\w가-힣]', '', full_text.lower())
        
        # key_quote 검색
        quote_pos = normalized_subtitle.find(normalized_quote)
        if quote_pos == -1:
            # 부분 매칭 시도 (첫 절반)
            half_quote = normalized_quote[:len(normalized_quote)//2]
            if len(half_quote) >= 5:
                quote_pos = normalized_subtitle.find(half_quote)
        
        if quote_pos == -1:
            return None
        
        # 해당 위치의 타임스탬프 찾기
        # 정규화로 인해 위치가 달라질 수 있으므로 비율로 계산
        if normalized_subtitle:
            ratio = quote_pos / len(normalized_subtitle)
            target_pos = int(len(full_text) * ratio)
            
            # 가장 가까운 타임스탬프 찾기
            best_timestamp = 0
            min_distance = float('inf')
            
            for pos, timestamp in position_to_timestamp.items():
                distance = abs(pos - target_pos)
                if distance < min_distance:
                    min_distance = distance
                    best_timestamp = timestamp
            
            return best_timestamp
        
        return None
    
    async def correct_timestamp(self, signal: Dict) -> Dict:
        """단일 시그널의 타임스탬프 교정"""
        signal_id = signal['id']
        video_info = signal.get('influencer_videos')
        key_quote = signal['key_quote']
        current_timestamp_str = signal['timestamp']
        
        if not video_info or not key_quote:
            return {
                'signal_id': signal_id,
                'status': 'error',
                'reason': 'missing_data'
            }
        
        video_id = video_info['video_id']
        video_title = video_info.get('title', '')
        
        print(f"  🔍 시그널 {signal_id[:8]}...")
        print(f"      Video: {video_id} | {video_title[:50]}...")
        print(f"      Quote: {key_quote[:50]}...")
        print(f"      Current: {current_timestamp_str}")
        
        # 현재 타임스탬프를 초 단위로 변환
        current_seconds = self.timestamp_to_seconds(current_timestamp_str)
        
        # 자막 추출
        subtitles = await self.get_subtitles_from_yt_dlp(video_id)
        if not subtitles:
            return {
                'signal_id': signal_id,
                'status': 'error',
                'reason': 'no_subtitles',
                'video_id': video_id
            }
        
        # key_quote로 실제 타임스탬프 찾기
        actual_seconds = self.find_quote_timestamp(subtitles, key_quote)
        if actual_seconds is None:
            return {
                'signal_id': signal_id,
                'status': 'error',
                'reason': 'quote_not_found',
                'key_quote': key_quote[:100]
            }
        
        # 30초 이상 차이나는지 확인
        diff = abs(current_seconds - actual_seconds)
        needs_correction = diff >= 30
        
        result = {
            'signal_id': signal_id,
            'video_id': video_id,
            'current_timestamp': current_timestamp_str,
            'current_seconds': current_seconds,
            'actual_seconds': actual_seconds,
            'diff_seconds': diff,
            'needs_correction': needs_correction,
            'status': 'success'
        }
        
        if needs_correction:
            # 새로운 타임스탬프 형식으로 변환
            new_timestamp_str = self.seconds_to_timestamp(actual_seconds)
            
            # Supabase UPDATE 실행
            try:
                update_url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
                params = {'id': f'eq.{signal_id}'}
                data = {'timestamp': new_timestamp_str}
                
                update_response = requests.patch(
                    update_url,
                    headers=self.headers,
                    params=params,
                    json=data
                )
                
                if update_response.status_code in [200, 204]:
                    result['updated'] = True
                    result['status'] = 'corrected'
                    result['new_timestamp'] = new_timestamp_str
                    self.corrected_count += 1
                    print(f"      ✅ 교정 완료: {current_timestamp_str} → {new_timestamp_str} (차이: {diff}s)")
                else:
                    result['updated'] = False
                    result['status'] = 'update_failed'
                    result['error'] = update_response.text
                    print(f"      ❌ 업데이트 실패: {update_response.status_code}")
                    
            except Exception as e:
                result['updated'] = False
                result['status'] = 'update_error'
                result['error'] = str(e)
                print(f"      ❌ 업데이트 오류: {e}")
        else:
            print(f"      ⏭️ 교정 불필요: 차이 {diff}s < 30s")
        
        return result
    
    async def get_all_signals_with_videos(self) -> List[Dict]:
        """JOIN을 통해 시그널과 비디오 정보를 함께 조회"""
        try:
            url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
            params = {
                'select': 'id,timestamp,key_quote,stock,video_id,influencer_videos(video_id,title)'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            signals = response.json()
            print(f"📊 JOIN으로 {len(signals)}개 시그널 조회 완료")
            return signals
                
        except Exception as e:
            print(f"❌ Supabase 조회 오류: {e}")
            return []
    
    async def run_correction(self, output_file: str = 'timestamp_correction_results_v2.json'):
        """타임스탬프 교정 실행"""
        print(f"\n{'='*80}")
        print(f"타임스탬프 전수 교정 시작 (DB 구조 V2)")
        print(f"{'='*80}\n")
        
        start_time = time.time()
        
        # 모든 시그널 조회
        signals = await self.get_all_signals_with_videos()
        if not signals:
            return
        
        total_count = len(signals)
        print(f"📊 교정 대상: {total_count}개 시그널\n")
        
        # 배치별 처리
        for i in range(0, total_count, BATCH_SIZE):
            batch = signals[i:i+BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            total_batches = (total_count + BATCH_SIZE - 1) // BATCH_SIZE
            
            print(f"📦 배치 {batch_num}/{total_batches} ({len(batch)}개) 처리 중...")
            
            for j, signal in enumerate(batch):
                try:
                    # 레이트리밋 딜레이
                    if j > 0:  # 첫 번째가 아니면 딜레이
                        delay = random.uniform(MIN_DELAY, MAX_DELAY)
                        await asyncio.sleep(delay)
                    
                    result = await self.correct_timestamp(signal)
                    self.results.append(result)
                    self.processed_count += 1
                    
                    if result['status'] == 'error':
                        self.failed_count += 1
                    
                    # 진행 상황 표시
                    progress = (i + j + 1) / total_count * 100
                    print(f"      📈 진행: {progress:.1f}% ({i + j + 1}/{total_count})")
                    
                except Exception as e:
                    print(f"      ❌ 시그널 {signal['id'][:8]}... 처리 오류: {e}")
                    self.failed_count += 1
                    self.results.append({
                        'signal_id': signal['id'],
                        'status': 'exception',
                        'error': str(e)
                    })
            
            # 배치 간 휴식 (마지막 배치가 아니면)
            if i + BATCH_SIZE < total_count:
                print(f"    ⏸️ 배치 완료, {BATCH_BREAK}초 대기...")
                await asyncio.sleep(BATCH_BREAK)
        
        elapsed = time.time() - start_time
        
        # 결과 저장
        output = {
            'timestamp': datetime.now().isoformat(),
            'elapsed_seconds': round(elapsed, 1),
            'total_signals': total_count,
            'processed': self.processed_count,
            'corrected': self.corrected_count,
            'failed': self.failed_count,
            'results': self.results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*80}")
        print(f"✅ 타임스탬프 교정 완료!")
        print(f"⏱️ 소요 시간: {elapsed:.0f}초 ({elapsed/60:.1f}분)")
        print(f"📊 처리: {self.processed_count}/{total_count}개")
        print(f"✏️ 교정: {self.corrected_count}개")
        print(f"❌ 실패: {self.failed_count}개")
        print(f"📁 결과 파일: {output_file}")
        print(f"{'='*80}")

async def main():
    corrector = TimestampCorrectorV2()
    await corrector.run_correction()

if __name__ == '__main__':
    asyncio.run(main())