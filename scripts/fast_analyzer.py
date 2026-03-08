#!/usr/bin/env python3
"""
fast_analyzer.py - 怨좎냽 蹂묐젹 ?쒓렇??遺꾩꽍湲?
- asyncio + aiohttp濡?3~5媛??숈떆 泥섎━
- claude-sonnet-4-6 ?ъ슜 (haiku ?鍮?鍮좊Ⅴ怨??뺥솗)
- rate limit ?먮룞 媛먯? ???숈떆???먮룞 議곗젅
- 紐⑺몴: 100媛??곸긽 1~2?쒓컙 ???꾨즺
"""

import os
import re
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

# ?ㅼ젙
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL', '')
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"  # 鍮좊Ⅴ怨??뺥솗
MAX_CONCURRENT = 3  # ?쒖옉 ?숈떆??(rate limit???먮룞 媛먯냼)
MIN_CONCURRENT = 1
DELAY_BETWEEN = 1.0  # ?붿껌 媛?理쒖냼 媛꾧꺽 (珥?
MAX_RETRIES = 2

# 硫??寃뚯뒪??梨꾨꼸 ?ㅼ젙
MULTI_GUEST_CHANNELS = {
    'https://www.youtube.com/@3protv',
    'https://www.youtube.com/@3ProTV',
    '?쇳봽濡쏷V',
}

def extract_guest_from_title(title: str) -> List[str]:
    """?곸긽 ?쒕ぉ?먯꽌 寃뚯뒪?몃챸 異붿텧 (?쇳봽濡쏷V ??硫??寃뚯뒪??梨꾨꼸??
    ?⑦꽩: "... | 源?μ뿴 ?좊땲?ㅽ넗由ъ옄?곗슫??, "... | ?띿꽑?? 諛뺣챸?? ?댁옱洹?
    """
    if '|' not in title:
        return []
    after_pipe = title.split('|')[-1].strip()
    parts = [p.strip() for p in after_pipe.split(',')]
    names = []
    for part in parts:
        match = re.match(r'([媛-??{2,3})', part.strip())
        if match:
            names.append(match.group(1))
    return names


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
        
        # 寃利?紐⑤뱢
        try:
            from signal_validator import SignalValidator
            self.validator = SignalValidator()
        except ImportError:
            self.validator = None
        
        # ?꾨＼?꾪듃 濡쒕뱶
        if prompt_path:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.prompt_template = f.read()
        else:
            # 湲곕낯 ?꾨＼?꾪듃 寃쎈줈
            default = Path(__file__).parent.parent / 'prompts' / 'pipeline_v10.md'
            if default.exists():
                with open(default, 'r', encoding='utf-8') as f:
                    self.prompt_template = f.read()
            else:
                raise FileNotFoundError(f"?꾨＼?꾪듃 ?뚯씪 ?놁쓬: {default}")
    
    def load_subtitle(self, subtitle_file: str) -> str:
        """?먮쭑 ?뚯씪?먯꽌 ?띿뒪??異붿텧"""
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            segments = json.load(f)
        if not isinstance(segments, list):
            return ""
        return " ".join(s.get('text', '') for s in segments if isinstance(s, dict)).strip()
    
    def create_prompt(self, channel_url: str, video_title: str, video_id: str, subtitle: str) -> str:
        """遺꾩꽍 ?꾨＼?꾪듃 ?앹꽦 ???좏겙 ?덉빟???꾪빐 ?먮쭑 理쒕? 8000??""
        subtitle_trimmed = subtitle[:8000] if len(subtitle) > 8000 else subtitle
        
        prompt = self.prompt_template.replace('{CHANNEL_URL}', channel_url)
        
        # 硫??寃뚯뒪??梨꾨꼸: ?쒕ぉ?먯꽌 寃뚯뒪?몃챸 異붿텧?섏뿬 ?뚰듃 ?쒓났
        speaker_hint = ""
        is_multi_guest = any(ch in channel_url for ch in MULTI_GUEST_CHANNELS)
        if is_multi_guest:
            guests = extract_guest_from_title(video_title)
            if guests:
                speaker_hint = f"\n?좑툘 ???곸긽??異쒖뿰??speaker): {', '.join(guests)}\n?쒓렇?먯쓽 ?붿옄瑜???異쒖뿰?먮챸?쇰줈 ?뺥솗??援щ텇?댁＜?몄슂.\n"
        
        prompt += f"""

=== 遺꾩꽍 ????곸긽 ===
?쒕ぉ: {video_title}
URL: https://www.youtube.com/watch?v={video_id}
{speaker_hint}
=== ?먮쭑 ?댁슜 ===
{subtitle_trimmed}

=== 遺꾩꽍 吏?쒖궗??===
???곸긽???먮쭑??遺꾩꽍?섍퀬 JSON ?뺥깭濡??쒓렇?먯쓣 異붿텧?댁＜?몄슂.
"""
        return prompt
    
    def parse_response(self, text: str) -> Dict:
        """?묐떟 ?뚯떛"""
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
        """?⑥씪 ?곸긽 遺꾩꽍 (?몃쭏?ъ뼱濡??숈떆???쒖뼱)"""
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
                            # Rate limited ??媛먯냽
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
                            
                            # ?덉쭏 寃利?
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
                            
                            # 硫??寃뚯뒪??梨꾨꼸: ?쒓렇?먯뿉 speaker ?뺣낫 異붽?
                            is_multi = any(ch in channel_url for ch in MULTI_GUEST_CHANNELS)
                            if is_multi:
                                guests = extract_guest_from_title(video_title)
                                if guests:
                                    for sig in signals:
                                        if 'speaker' not in sig or not sig.get('speaker'):
                                            sig['speaker'] = guests[0]  # 湲곕낯: 泥?踰덉㎏ 寃뚯뒪??
                            
                            self.stats['processed'] += 1
                            self.stats['signals'] += len(signals)
                            
                            # Rate limit ?댁젣 ??蹂듦뎄
                            if self.rate_limited and self.current_concurrency < MAX_CONCURRENT:
                                self.current_concurrency = min(MAX_CONCURRENT, self.current_concurrency + 1)
                                self.semaphore = asyncio.Semaphore(self.current_concurrency)
                            
                            print(f"  ??{video_id[:12]}... ??{len(signals)}媛??쒓렇??)
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
        """諛곗튂 遺꾩꽍 ?ㅽ뻾"""
        print(f"\n{'='*60}")
        print(f"怨좎냽 蹂묐젹 遺꾩꽍湲??쒖옉")
        print(f"??? {len(videos)}媛??곸긽, ?숈떆?? {MAX_CONCURRENT}, 紐⑤뜽: {MODEL}")
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
            
            # 紐⑤뱺 ?쒖뒪???ㅽ뻾 (?몃쭏?ъ뼱媛 ?숈떆???쒖뼱)
            self.results = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start_time
        
        # 寃곌낵 ???
        output = {
            'timestamp': datetime.now().isoformat(),
            'elapsed_seconds': round(elapsed, 1),
            'stats': self.stats,
            'results': self.results
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"?꾨즺! {elapsed:.0f}珥?({elapsed/60:.1f}遺?")
        rejected = self.stats.get('rejected', 0)
        print(f"泥섎━: {self.stats['processed']}, ?ㅽ궢: {self.stats['skipped']}, "
              f"?먮윭: {self.stats['errors']}, ?쒓렇?? {self.stats['signals']}, "
              f"reject: {rejected}")
        if self.validator:
            self.validator.print_stats()
        print(f"寃곌낵: {output_file}")
        print(f"{'='*60}")


async def main():
    """CLI ?ㅽ뻾"""
    import argparse
    parser = argparse.ArgumentParser(description='怨좎냽 蹂묐젹 ?쒓렇??遺꾩꽍湲?)
    parser.add_argument('--subs-dir', required=True, help='?먮쭑 ?뚯씪 ?붾젆?좊━')
    parser.add_argument('--channel-url', required=True, help='梨꾨꼸 URL')
    parser.add_argument('--titles-file', help='?곸긽 ?쒕ぉ ?뚯씪 (video_id|||title)')
    parser.add_argument('--output', default='fast_analysis_results.json', help='寃곌낵 ?뚯씪')
    parser.add_argument('--skip-ids', help='?ㅽ궢??video_id 紐⑸줉 ?뚯씪')
    parser.add_argument('--concurrency', type=int, default=3, help='?숈떆 泥섎━ ??)
    parser.add_argument('--prompt', help='?꾨＼?꾪듃 ?뚯씪 寃쎈줈')
    args = parser.parse_args()
    
    global MAX_CONCURRENT
    MAX_CONCURRENT = args.concurrency
    
    # ?먮쭑 ?뚯씪 濡쒕뱶
    subs_files = glob.glob(os.path.join(args.subs_dir, '*.json'))
    print(f"?먮쭑 ?뚯씪: {len(subs_files)}媛?)
    
    # ?ㅽ궢 ID 濡쒕뱶
    skip_ids = set()
    if args.skip_ids and os.path.exists(args.skip_ids):
        with open(args.skip_ids, 'r') as f:
            skip_ids = set(line.strip() for line in f if line.strip())
        print(f"?ㅽ궢 ID: {len(skip_ids)}媛?)
    
    # ?쒕ぉ 濡쒕뱶
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
    
    # ?곸긽 紐⑸줉 援ъ꽦 (titles ?뚯씪???덈뒗 寃껊쭔 泥섎━)
    videos = []
    for sf in subs_files:
        vid = os.path.splitext(os.path.basename(sf))[0]
        if vid not in skip_ids:
            # titles ?뚯씪???쒓났??寃쎌슦, ?대떦 ?뚯씪???덈뒗 video_id留?泥섎━
            if titles and vid not in titles:
                continue
            videos.append({
                'video_id': vid,
                'subtitle_file': sf,
                'title': titles.get(vid, f'?곸긽 {vid}')
            })
    
    print(f"遺꾩꽍 ??? {len(videos)}媛?)
    
    if not videos:
        print("遺꾩꽍???곸긽 ?놁쓬!")
        return
    
    analyzer = FastAnalyzer(prompt_path=args.prompt)
    await analyzer.run_batch(videos, args.channel_url, args.output)


if __name__ == '__main__':
    asyncio.run(main())

