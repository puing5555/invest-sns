#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
timestamp_corrector_alternative.py - 대안적 타임스탬프 교정
- 기존 자막 데이터 활용 (subs 디렉토리)
- key_quote 매칭으로 정확한 타임스탬프 찾기
- 30초 이상 차이나면 교정
"""

import os
import re
import json
import time
import random
import asyncio
import requests
import glob
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env.local')

# 설정
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

# 레이트리밋 설정
MIN_DELAY = 1
MAX_DELAY = 2
BATCH_SIZE = 10

class TimestampCorrectorAlt:
    def __init__(self, subs_dir: str):
        self.subs_dir = Path(subs_dir)
        self.headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        self.processed_count = 0
        self.corrected_count = 0
        self.failed_count = 0
        self.results = []
        
        # 사용 가능한 자막 파일 스캔
        self.available_subtitles = {}
        self.scan_subtitle_files()
        
    def scan_subtitle_files(self):
        """자막 파일들 스캔하여 video_id 매핑 생성"""
        if not self.subs_dir.exists():
            print(f"자막 디렉토리 없음: {self.subs_dir}")
            return
        
        subtitle_files = list(self.subs_dir.glob('*.json'))
        for file_path in subtitle_files:
            video_id = file_path.stem
            self.available_subtitles[video_id] = str(file_path)
        
        print(f"사용 가능한 자막 파일: {len(self.available_subtitles)}개")
        if self.available_subtitles:
            sample_ids = list(self.available_subtitles.keys())[:5]
            print(f"샘플 video_id: {sample_ids}")
        
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
    
    def load_subtitle_segments(self, subtitle_file: str) -> List[Dict]:
        """자막 파일에서 세그먼트 로드"""
        try:
            with open(subtitle_file, 'r', encoding='utf-8') as f:
                segments = json.load(f)
            if not isinstance(segments, list):
                return []
            return segments
        except Exception as e:
            print(f"    자막 로드 오류: {e}")
            return []
    
    def find_quote_in_segments(self, segments: List[Dict], key_quote: str) -> Optional[int]:
        """자막 세그먼트에서 key_quote를 찾아 초 단위 타임스탬프 반환"""
        if not segments or not key_quote:
            return None
        
        # key_quote 정규화
        normalized_quote = re.sub(r'[^\w가-힣]', '', key_quote.lower())
        if len(normalized_quote) < 5:
            return None
        
        # 자막 텍스트 구성 (시간 정보와 함께)
        text_with_timestamps = []
        full_text = ""
        
        for seg in segments:
            if isinstance(seg, dict) and 'text' in seg:
                text = seg.get('text', '')
                timestamp = seg.get('timestamp', '0:00')
                
                start_pos = len(full_text)
                full_text += text
                end_pos = len(full_text)
                
                text_with_timestamps.append({
                    'text': text,
                    'timestamp': timestamp,
                    'start_pos': start_pos,
                    'end_pos': end_pos
                })
        
        # 정규화된 자막에서 quote 검색
        normalized_full = re.sub(r'[^\w가-힣]', '', full_text.lower())
        quote_pos = normalized_full.find(normalized_quote)
        
        if quote_pos == -1:
            # 부분 매칭 시도 (50% 이상)
            half_quote = normalized_quote[:len(normalized_quote)//2]
            if len(half_quote) >= 5:
                quote_pos = normalized_full.find(half_quote)
        
        if quote_pos == -1:
            return None
        
        # 위치에 해당하는 타임스탬프 찾기
        if normalized_full:
            ratio = quote_pos / len(normalized_full)
            target_pos = int(len(full_text) * ratio)
            
            # 가장 가까운 세그먼트 찾기
            best_timestamp = "0:00"
            min_distance = float('inf')
            
            for seg_info in text_with_timestamps:
                # 텍스트 범위 내에 있는지 확인
                if seg_info['start_pos'] <= target_pos <= seg_info['end_pos']:
                    best_timestamp = seg_info['timestamp']
                    break
                
                # 또는 가장 가까운 거리
                distance = min(
                    abs(seg_info['start_pos'] - target_pos),
                    abs(seg_info['end_pos'] - target_pos)
                )
                if distance < min_distance:
                    min_distance = distance
                    best_timestamp = seg_info['timestamp']
            
            return self.timestamp_to_seconds(best_timestamp)
        
        return None
    
    async def correct_signal_timestamp(self, signal: Dict) -> Dict:
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
        print(f"      Video: {video_id}")
        print(f"      Quote: {key_quote[:80]}...")
        print(f"      Current: {current_timestamp_str}")
        
        # 현재 타임스탬프를 초 단위로 변환
        current_seconds = self.timestamp_to_seconds(current_timestamp_str)
        
        # 해당 비디오의 자막 파일 찾기
        if video_id not in self.available_subtitles:
            return {
                'signal_id': signal_id,
                'status': 'error',
                'reason': 'no_subtitle_file',
                'video_id': video_id
            }
        
        subtitle_file = self.available_subtitles[video_id]
        
        # 자막 세그먼트 로드
        segments = self.load_subtitle_segments(subtitle_file)
        if not segments:
            return {
                'signal_id': signal_id,
                'status': 'error',
                'reason': 'subtitle_load_failed',
                'subtitle_file': subtitle_file
            }
        
        # key_quote로 실제 타임스탬프 찾기
        actual_seconds = self.find_quote_in_segments(segments, key_quote)
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
            'status': 'analyzed'
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
                    result['error'] = update_response.text[:200]
                    print(f"      ❌ 업데이트 실패: {update_response.status_code}")
                    
            except Exception as e:
                result['updated'] = False
                result['status'] = 'update_error'
                result['error'] = str(e)
                print(f"      ❌ 업데이트 오류: {e}")
        else:
            print(f"      ⏭️ 교정 불필요: 차이 {diff}s < 30s")
        
        return result
    
    async def get_signals_with_available_subtitles(self) -> List[Dict]:
        """자막 파일이 있는 시그널들만 조회"""
        try:
            url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
            params = {
                'select': 'id,timestamp,key_quote,stock,video_id,influencer_videos(video_id,title)'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            all_signals = response.json()
            
            # 자막 파일이 있는 시그널들만 필터링
            available_signals = []
            for signal in all_signals:
                video_info = signal.get('influencer_videos')
                if video_info and video_info.get('video_id') in self.available_subtitles:
                    available_signals.append(signal)
            
            print(f"📊 전체 시그널: {len(all_signals)}개")
            print(f"📊 자막 파일 보유: {len(available_signals)}개")
            
            return available_signals
                
        except Exception as e:
            print(f"❌ Supabase 조회 오류: {e}")
            return []
    
    async def run_correction(self, limit: int = None, 
                           output_file: str = 'timestamp_correction_alt_results.json'):
        """타임스탬프 교정 실행 (자막 파일 기반)"""
        print(f"\n{'='*80}")
        print(f"타임스탬프 교정 (자막 파일 기반)")
        print(f"{'='*80}\n")
        
        start_time = time.time()
        
        # 자막 파일이 있는 시그널들 조회
        signals = await self.get_signals_with_available_subtitles()
        if not signals:
            print("❌ 처리할 시그널이 없습니다.")
            return
        
        if limit:
            signals = signals[:limit]
            print(f"📊 처리 제한: {limit}개")
        
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
                    # 딜레이
                    if j > 0:
                        delay = random.uniform(MIN_DELAY, MAX_DELAY)
                        await asyncio.sleep(delay)
                    
                    result = await self.correct_signal_timestamp(signal)
                    self.results.append(result)
                    self.processed_count += 1
                    
                    if result['status'] in ['error', 'update_failed', 'update_error']:
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
            
            # 배치 간 휴식
            if i + BATCH_SIZE < total_count:
                print(f"    ⏸️ 배치 완료, 3초 대기...")
                await asyncio.sleep(3)
        
        elapsed = time.time() - start_time
        
        # 결과 저장
        output = {
            'timestamp': datetime.now().isoformat(),
            'subtitle_dir': str(self.subs_dir),
            'available_subtitles': len(self.available_subtitles),
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
    import argparse
    parser = argparse.ArgumentParser(description='타임스탬프 교정 (자막 파일 기반)')
    parser.add_argument('--subs-dir', required=True, help='자막 파일 디렉토리')
    parser.add_argument('--limit', type=int, help='처리할 시그널 수 제한')
    parser.add_argument('--output', default='timestamp_correction_alt_results.json', help='결과 파일')
    args = parser.parse_args()
    
    corrector = TimestampCorrectorAlt(args.subs_dir)
    await corrector.run_correction(limit=args.limit, output_file=args.output)

if __name__ == '__main__':
    asyncio.run(main())