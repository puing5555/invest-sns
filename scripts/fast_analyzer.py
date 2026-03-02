#!/usr/bin/env python3
"""
fast_analyzer.py - 고속 병렬 시그널 분석기
- asyncio + aiohttp로 3~5개 동시 처리
- claude-sonnet-4-20250514 사용 (haiku 대비 빠르고 정확)
- rate limit 자동 감지 → 동시성 자동 조절
- 목표: 100개 영상 1~2시간 내 완료
"""

import os
import json
import asyncio
import aiohttp
import time
import glob
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env.local')

# 설정
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL', '')
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-20250514"  # 빠르고 정확
MAX_CONCURRENT = 3  # 시작 동시성 (rate limit시 자동 감소)
MIN_CONCURRENT = 1
DELAY_BETWEEN = 1.0  # 요청 간 최소 간격 (초)
MAX_RETRIES = 2

class FastAnalyzer:
    def __init__(self, prompt_path: str = None):
        self.api_key = ANTHROPIC_API_KEY
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        self.current_concurrency = MAX_CONCURRENT
        self.rate_limited = False
        self.stats = {'processed': 0, 'skipped': 0, 'errors': 0, 'signals': 0}
        self.results = []
        
        # 검증 모듈
        try:
            from signal_validator import SignalValidator
            self.validator = SignalValidator()
        except ImportError:
            self.validator = None
        
        # 프롬프트 로드
        if prompt_path:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.prompt_template = f.read()
        else:
            # 기본 프롬프트 경로
            default = Path(__file__).parent.parent / 'prompts' / 'pipeline_v10.md'
            if default.exists():
                with open(default, 'r', encoding='utf-8') as f:
                    self.prompt_template = f.read()
            else:
                raise FileNotFoundError(f"프롬프트 파일 없음: {default}")
    
    def load_subtitle(self, subtitle_file: str) -> str:
        """자막 파일에서 텍스트 추출"""
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            segments = json.load(f)
        if not isinstance(segments, list):
            return ""
        return " ".join(s.get('text', '') for s in segments if isinstance(s, dict)).strip()
    
    def create_prompt(self, channel_url: str, video_title: str, video_id: str, subtitle: str) -> str:
        """분석 프롬프트 생성 — 토큰 절약을 위해 자막 최대 8000자"""
        subtitle_trimmed = subtitle[:8000] if len(subtitle) > 8000 else subtitle
        
        prompt = self.prompt_template.replace('{CHANNEL_URL}', channel_url)
        prompt += f"""

=== 분석 대상 영상 ===
제목: {video_title}
URL: https://www.youtube.com/watch?v={video_id}

=== 자막 내용 ===
{subtitle_trimmed}

=== 분석 지시사항 ===
위 영상의 자막을 분석하고 JSON 형태로 시그널을 추출해주세요.
"""
        return prompt
    
    def parse_response(self, text: str) -> Dict:
        """응답 파싱"""
        try:
            if '```json' in text:
                start = text.find('```json') + 7
                end = text.find('```', start)
                return json.loads(text[start:end].strip())
            elif '{' in text:
                start = text.find('{')
                end = text.rfind('}') + 1
                return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
        return {"error": "parse_failed", "raw": text[:500]}
    
    async def analyze_one(self, session: aiohttp.ClientSession, video_id: str, 
                          subtitle_file: str, channel_url: str, video_title: str) -> Dict:
        """단일 영상 분석 (세마포어로 동시성 제어)"""
        async with self.semaphore:
            subtitle = self.load_subtitle(subtitle_file)
            if len(subtitle) < 100:
                self.stats['skipped'] += 1
                return {'video_id': video_id, 'status': 'skipped', 'reason': 'too_short'}
            
            prompt = self.create_prompt(channel_url, video_title, video_id, subtitle)
            
            for attempt in range(MAX_RETRIES + 1):
                try:
                    payload = {
                        'model': MODEL,
                        'max_tokens': 4000,
                        'messages': [{'role': 'user', 'content': prompt}]
                    }
                    
                    async with session.post(API_URL, json=payload, headers=self.headers, 
                                          timeout=aiohttp.ClientTimeout(total=180)) as resp:
                        if resp.status == 429:
                            # Rate limited — 감속
                            retry_after = int(resp.headers.get('retry-after', '30'))
                            print(f"  [429] Rate limited, waiting {retry_after}s, reducing concurrency")
                            self.rate_limited = True
                            self.current_concurrency = max(MIN_CONCURRENT, self.current_concurrency - 1)
                            self.semaphore = asyncio.Semaphore(self.current_concurrency)
                            await asyncio.sleep(retry_after)
                            continue
                        
                        if resp.status == 529:
                            # Overloaded
                            print(f"  [529] API overloaded, waiting 60s")
                            await asyncio.sleep(60)
                            continue
                            
                        resp.raise_for_status()
                        data = await resp.json()
                        
                        if 'content' in data and data['content']:
                            text = data['content'][0].get('text', '')
                            result = self.parse_response(text)
                            signals = result.get('signals', [])
                            
                            # 품질 검증
                            if self.validator:
                                validated = []
                                for sig in signals:
                                    sig['video_id'] = video_id
                                    vr = self.validator.validate(sig)
                                    if vr.passed:
                                        validated.append(sig)
                                    else:
                                        self.stats.setdefault('rejected', 0)
                                        self.stats['rejected'] += 1
                                signals = validated
                            
                            self.stats['processed'] += 1
                            self.stats['signals'] += len(signals)
                            
                            # Rate limit 해제 시 복구
                            if self.rate_limited and self.current_concurrency < MAX_CONCURRENT:
                                self.current_concurrency = min(MAX_CONCURRENT, self.current_concurrency + 1)
                                self.semaphore = asyncio.Semaphore(self.current_concurrency)
                            
                            print(f"  ✓ {video_id[:12]}... → {len(signals)}개 시그널")
                            await asyncio.sleep(DELAY_BETWEEN)
                            return {
                                'video_id': video_id,
                                'title': video_title,
                                'status': 'ok',
                                'signals': signals,
                                'raw_result': result
                            }
                
                except asyncio.TimeoutError:
                    print(f"  [TIMEOUT] {video_id} attempt {attempt+1}")
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(10)
                except Exception as e:
                    print(f"  [ERROR] {video_id}: {e}")
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(5)
            
            self.stats['errors'] += 1
            return {'video_id': video_id, 'status': 'error', 'reason': 'max_retries'}
    
    async def run_batch(self, videos: List[Dict], channel_url: str, output_file: str):
        """배치 분석 실행"""
        print(f"\n{'='*60}")
        print(f"고속 병렬 분석기 시작")
        print(f"대상: {len(videos)}개 영상, 동시성: {MAX_CONCURRENT}, 모델: {MODEL}")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for v in videos:
                task = self.analyze_one(
                    session, v['video_id'], v['subtitle_file'],
                    channel_url, v.get('title', '')
                )
                tasks.append(task)
            
            # 모든 태스크 실행 (세마포어가 동시성 제어)
            self.results = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start_time
        
        # 결과 저장
        output = {
            'timestamp': datetime.now().isoformat(),
            'elapsed_seconds': round(elapsed, 1),
            'stats': self.stats,
            'results': self.results
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"완료! {elapsed:.0f}초 ({elapsed/60:.1f}분)")
        rejected = self.stats.get('rejected', 0)
        print(f"처리: {self.stats['processed']}, 스킵: {self.stats['skipped']}, "
              f"에러: {self.stats['errors']}, 시그널: {self.stats['signals']}, "
              f"reject: {rejected}")
        if self.validator:
            self.validator.print_stats()
        print(f"결과: {output_file}")
        print(f"{'='*60}")


async def main():
    """CLI 실행"""
    import argparse
    parser = argparse.ArgumentParser(description='고속 병렬 시그널 분석기')
    parser.add_argument('--subs-dir', required=True, help='자막 파일 디렉토리')
    parser.add_argument('--channel-url', required=True, help='채널 URL')
    parser.add_argument('--titles-file', help='영상 제목 파일 (video_id|||title)')
    parser.add_argument('--output', default='fast_analysis_results.json', help='결과 파일')
    parser.add_argument('--skip-ids', help='스킵할 video_id 목록 파일')
    parser.add_argument('--concurrency', type=int, default=3, help='동시 처리 수')
    parser.add_argument('--prompt', help='프롬프트 파일 경로')
    args = parser.parse_args()
    
    global MAX_CONCURRENT
    MAX_CONCURRENT = args.concurrency
    
    # 자막 파일 로드
    subs_files = glob.glob(os.path.join(args.subs_dir, '*.json'))
    print(f"자막 파일: {len(subs_files)}개")
    
    # 스킵 ID 로드
    skip_ids = set()
    if args.skip_ids and os.path.exists(args.skip_ids):
        with open(args.skip_ids, 'r') as f:
            skip_ids = set(line.strip() for line in f if line.strip())
        print(f"스킵 ID: {len(skip_ids)}개")
    
    # 제목 로드
    titles = {}
    if args.titles_file and os.path.exists(args.titles_file):
        for enc in ['utf-8', 'cp949', 'utf-16']:
            try:
                with open(args.titles_file, 'r', encoding=enc) as f:
                    for line in f:
                        if '|||' in line:
                            vid, title = line.strip().split('|||', 1)
                            titles[vid.strip()] = title.strip()
                break
            except:
                continue
    
    # 영상 목록 구성 (titles 파일에 있는 것만 처리)
    videos = []
    for sf in subs_files:
        vid = os.path.splitext(os.path.basename(sf))[0]
        if vid not in skip_ids:
            # titles 파일이 제공된 경우, 해당 파일에 있는 video_id만 처리
            if titles and vid not in titles:
                continue
            videos.append({
                'video_id': vid,
                'subtitle_file': sf,
                'title': titles.get(vid, f'영상 {vid}')
            })
    
    print(f"분석 대상: {len(videos)}개")
    
    if not videos:
        print("분석할 영상 없음!")
        return
    
    analyzer = FastAnalyzer(prompt_path=args.prompt)
    await analyzer.run_batch(videos, args.channel_url, args.output)


if __name__ == '__main__':
    asyncio.run(main())
