#!/usr/bin/env python3
"""
세상학개론 누락 영상 전체 파이프라인
1. 자막 추출 (이미 있는 것 스킵)
2. 메타데이터 가져오기 (yt-dlp)
3. DB INSERT (influencer_videos)
4. 시그널 분석 (Claude Sonnet)
5. DB INSERT (influencer_signals)
"""

import json, os, sys, time, random, asyncio, aiohttp, subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

load_dotenv(Path(__file__).parent.parent / '.env.local')

# === CONFIG ===
CHANNEL_ID = "d68f8efd-64c8-4c07-9d34-e98c2954f4e1"
CHANNEL_URL = "https://www.youtube.com/@sesang101"
SUBS_DIR = r"C:\Users\Mario\work\subs\sesang101"
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
MODEL = "claude-sonnet-4-20250514"

# All 78 video IDs
ALL_IDS = [
    "Ke7gQMbIFLI", "4wCO1fdl9iU", "4cCGQFHrbK4", "Lszaj6NhNcA", "-3odSn4Wi2E",
    "iNAlXUEw9tc", "A2l1-lyzq4Q", "q4vz1jhWS4s", "JzzXPN5v1BI", "6Bk_eG77-5g",
    "yxt087-C1zk", "QajNAfX5YvI", "BQY0eh1lcUk", "79PFFmQQjOw", "4bClsFvaoLs",
    "RXdOkIaSIzc", "4UvO-6eecv8", "1bcmmTZRX5Q", "uMglUc_vQ6A", "EaclBpfxjCI",
    "0z8e_heKtKk", "vpLSDLs6Fis", "cfwN1eWNlFA", "NlWaAL3SOxE", "blAWrFLQ_Lc",
    "qkpmS6yfO_g", "KvuATAaRxe8", "j3x7149DzDQ", "KkxAjOp-6H4", "Y9JMqS87HEM",
    "sU0zaA0oJVk", "bk-2Y0tjnZQ", "un9IHz9LnrA", "rde-ahZ29UQ", "cjKV1A7UTvI",
    "E0l6aYaff0U", "vE55S-x-6Lc", "CN_T1V1ocjg", "VdxXXSCbiEc", "Qowcv46AneI",
    "NcijgSSeJVU", "zRGNYWXHfV4", "oiAMDjdr334", "Te7EzydvBT4", "YbbV60KVe_c",
    "vR-IeyHBRkg", "4yZDpfDT7K8", "4Bay6eXJH1Q", "UCX7_tJGgc4", "FrOAHoV0pH4",
    "3NUs0JElPvs", "QJf40N2wvh8", "5I9wb6NKNUs", "NVieilk8oHI", "RNvKFfEru-o",
    "HK9jUm9lcEA", "5Py7WIb8iYw", "pmlsIYTKiw4", "OadsiFLklsM", "-JsPLE90h1Q",
    "PPsCEEUIGqk", "tR5OyzvKCgE", "4h-fPWoA2W4", "5aGn5CqbQls", "AaJTT_GTkKY",
    "RrSo7nQFSGY", "peYoNFd3z9E", "WVYVfmpLg4Q", "eiC2ndorjDQ", "Du_VW1HIG5s",
    "U3Xa3h3kztg", "7UoMvJPj0gw", "O0OVrGY7JUc", "eXlKZ1D-mwM", "7mzsY68IhhI",
    "9cg-iVIkg20", "JF34kovcvPk", "ojsKQd_mJmk"
]

# Exclude non-investment videos
EXCLUDE_IDS = {
    "QJf40N2wvh8", "NVieilk8oHI", "WVYVfmpLg4Q", "U3Xa3h3kztg", "7UoMvJPj0gw",
    "Du_VW1HIG5s", "eXlKZ1D-mwM", "9cg-iVIkg20", "JF34kovcvPk", "ojsKQd_mJmk",
    "A2l1-lyzq4Q"
}

INVEST_IDS = [v for v in ALL_IDS if v not in EXCLUDE_IDS]
print(f"투자 영상: {len(INVEST_IDS)}개 (제외: {len(EXCLUDE_IDS)}개)")

# === STEP 1: Subtitle extraction ===
def step1_subtitles():
    """자막 추출 - 이미 있는 건 스킵"""
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.proxies import WebshareProxyConfig
    
    os.makedirs(SUBS_DIR, exist_ok=True)
    api = YouTubeTranscriptApi(
        proxy_config=WebshareProxyConfig(
            proxy_username="pvljrgkf",
            proxy_password="0e0eqk9rbwzq",
        )
    )
    
    existing = {os.path.splitext(f)[0] for f in os.listdir(SUBS_DIR) if f.endswith('.json')}
    need = [v for v in INVEST_IDS if v not in existing]
    print(f"\n=== STEP 1: 자막 추출 ===")
    print(f"이미 있음: {len(INVEST_IDS) - len(need)}, 추출 필요: {len(need)}")
    
    if not need:
        print("모든 자막 있음, 스킵")
        return
    
    success, fail = 0, 0
    no_subs = []
    for i, vid in enumerate(need):
        print(f"[{i+1}/{len(need)}] {vid}...", end=" ", flush=True)
        try:
            transcript = api.fetch(vid, languages=['ko', 'en'])
            entries = [{'text': s.text, 'start': s.start, 'duration': s.duration} for s in transcript]
            with open(os.path.join(SUBS_DIR, f"{vid}.json"), 'w', encoding='utf-8') as f:
                json.dump(entries, f, ensure_ascii=False, indent=1)
            print(f"OK ({len(entries)} segments)")
            success += 1
        except Exception as e:
            err = str(e)[:80]
            print(f"FAIL: {err}")
            fail += 1
            no_subs.append(vid)
        
        # Rate limiting
        if (i + 1) % 20 == 0 and i + 1 < len(need):
            print("--- 20개 완료, 5분 휴식 ---")
            time.sleep(300)
        else:
            time.sleep(random.uniform(2, 3))
    
    print(f"자막 추출 완료: 성공 {success}, 실패 {fail}")
    return no_subs

# === STEP 2: Metadata via yt-dlp ===
def step2_metadata():
    """yt-dlp로 메타데이터 가져오기"""
    print(f"\n=== STEP 2: 메타데이터 ===")
    meta = {}
    errors = []
    
    for i, vid in enumerate(INVEST_IDS):
        print(f"[{i+1}/{len(INVEST_IDS)}] {vid}...", end=" ", flush=True)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "yt_dlp", "--dump-json", "--no-download",
                 f"https://www.youtube.com/watch?v={vid}"],
                capture_output=True, timeout=60
            )
            if result.returncode == 0:
                stdout_text = result.stdout.decode('utf-8', errors='replace')
                data = json.loads(stdout_text)
                upload_date = data.get('upload_date', '')
                if upload_date and len(upload_date) == 8:
                    published = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}T00:00:00Z"
                else:
                    published = None
                meta[vid] = {
                    'title': data.get('title', ''),
                    'published_at': published,
                    'description': (data.get('description', '') or '')[:500]
                }
                print(f"OK: {meta[vid]['title'][:40]}")
            else:
                stderr_text = result.stderr.decode('utf-8', errors='replace')[:80] if result.stderr else 'unknown'
                print(f"FAIL: {stderr_text}")
                errors.append(vid)
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(vid)
        
        time.sleep(0.5)
    
    # Save metadata cache
    cache_file = os.path.join(SUBS_DIR, "_metadata.json")
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"메타데이터 완료: {len(meta)}개 성공, {len(errors)}개 실패")
    return meta, errors

# === STEP 3: DB INSERT videos ===
def step3_insert_videos(meta):
    """Supabase에 영상 INSERT"""
    print(f"\n=== STEP 3: DB INSERT (videos) ===")
    import requests
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
    }
    
    inserted, skipped, errors = 0, 0, []
    
    for vid in INVEST_IDS:
        m = meta.get(vid)
        if not m:
            print(f"  {vid}: 메타데이터 없음, 스킵")
            skipped += 1
            continue
        
        # Check subtitle
        sub_file = os.path.join(SUBS_DIR, f"{vid}.json")
        has_sub = os.path.exists(sub_file)
        subtitle_text = None
        subtitle_lang = None
        if has_sub:
            try:
                with open(sub_file, 'r', encoding='utf-8') as f:
                    segments = json.load(f)
                subtitle_text = " ".join(s.get('text', '') for s in segments if isinstance(s, dict))
                subtitle_lang = 'ko'
            except:
                has_sub = False
        
        row = {
            'channel_id': CHANNEL_ID,
            'video_id': vid,
            'title': m['title'],
            'published_at': m['published_at'],
            'subtitle_text': subtitle_text,
            'has_subtitle': has_sub,
            'subtitle_language': subtitle_lang
        }
        
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/influencer_videos",
            headers=headers,
            json=row
        )
        if resp.status_code in (200, 201):
            inserted += 1
            print(f"  ✓ {vid}: {m['title'][:30]}")
        elif resp.status_code == 409:
            skipped += 1
        else:
            errors.append((vid, resp.status_code, resp.text[:100]))
            print(f"  ✗ {vid}: {resp.status_code} {resp.text[:80]}")
    
    print(f"INSERT 완료: {inserted}개 성공, {skipped}개 스킵, {len(errors)}개 에러")
    return errors

# === STEP 4 & 5: Analyze + Insert signals ===
async def step4_5_analyze_and_insert():
    """Claude Sonnet으로 분석 후 시그널 INSERT"""
    print(f"\n=== STEP 4-5: 분석 + 시그널 INSERT ===")
    
    # Load prompt
    prompt_file = Path(__file__).parent.parent / 'prompts' / 'pipeline_v10.md'
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Load metadata
    cache_file = os.path.join(SUBS_DIR, "_metadata.json")
    with open(cache_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    # Build list of videos to analyze (must have subtitle)
    to_analyze = []
    for vid in INVEST_IDS:
        sub_file = os.path.join(SUBS_DIR, f"{vid}.json")
        if not os.path.exists(sub_file):
            continue
        try:
            with open(sub_file, 'r', encoding='utf-8') as f:
                segments = json.load(f)
            subtitle = " ".join(s.get('text', '') for s in segments if isinstance(s, dict)).strip()
            if len(subtitle) < 100:
                continue
        except:
            continue
        title = meta.get(vid, {}).get('title', f'영상 {vid}')
        to_analyze.append({'video_id': vid, 'title': title, 'subtitle': subtitle})
    
    print(f"분석 대상: {len(to_analyze)}개")
    
    # Check which already have signals in DB
    import requests
    sb_headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Get existing signals
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/influencer_signals?channel_id=eq.{CHANNEL_ID}&select=video_id",
        headers=sb_headers
    )
    existing_signal_vids = set()
    if resp.status_code == 200:
        existing_signal_vids = {r['video_id'] for r in resp.json()}
    
    to_analyze = [v for v in to_analyze if v['video_id'] not in existing_signal_vids]
    print(f"이미 시그널 있는 영상 제외 후: {len(to_analyze)}개")
    
    if not to_analyze:
        print("분석할 영상 없음!")
        return 0, 0
    
    semaphore = asyncio.Semaphore(3)
    stats = {'processed': 0, 'signals': 0, 'errors': 0}
    all_signals = []
    
    async def analyze_one(session, video):
        async with semaphore:
            vid = video['video_id']
            title = video['title']
            subtitle = video['subtitle'][:8000]
            
            prompt = prompt_template + f"""

=== 분석 대상 영상 ===
제목: {title}
URL: https://www.youtube.com/watch?v={vid}

=== 자막 내용 ===
{subtitle}

=== 분석 지시사항 ===
위 영상의 자막을 분석하고 JSON 형태로 시그널을 추출해주세요.
"""
            
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01'
            }
            payload = {
                'model': MODEL,
                'max_tokens': 4000,
                'messages': [{'role': 'user', 'content': prompt}]
            }
            
            for attempt in range(3):
                try:
                    async with session.post(
                        "https://api.anthropic.com/v1/messages",
                        json=payload, headers=headers,
                        timeout=aiohttp.ClientTimeout(total=180)
                    ) as resp:
                        if resp.status == 429:
                            retry = int(resp.headers.get('retry-after', '60'))
                            print(f"  [429] {vid} waiting {retry}s")
                            await asyncio.sleep(retry)
                            continue
                        if resp.status == 529:
                            print(f"  [529] overloaded, waiting 60s")
                            await asyncio.sleep(60)
                            continue
                        resp.raise_for_status()
                        data = await resp.json()
                        text = data['content'][0].get('text', '')
                        
                        # Parse JSON
                        result = None
                        try:
                            if '```json' in text:
                                s = text.find('```json') + 7
                                e = text.find('```', s)
                                result = json.loads(text[s:e].strip())
                            elif '{' in text:
                                s = text.find('{')
                                e = text.rfind('}') + 1
                                result = json.loads(text[s:e])
                        except:
                            pass
                        
                        signals = []
                        if result:
                            signals = result.get('signals', [])
                            if isinstance(result, list):
                                signals = result
                        
                        stats['processed'] += 1
                        stats['signals'] += len(signals)
                        
                        for sig in signals:
                            sig['video_id'] = vid
                            sig['title'] = title
                        
                        all_signals.extend(signals)
                        print(f"  ✓ {vid} '{title[:25]}' → {len(signals)}개 시그널")
                        await asyncio.sleep(1.0)
                        return
                        
                except asyncio.TimeoutError:
                    print(f"  [TIMEOUT] {vid} attempt {attempt+1}")
                    await asyncio.sleep(10)
                except Exception as e:
                    print(f"  [ERROR] {vid}: {str(e)[:60]}")
                    await asyncio.sleep(5)
            
            stats['errors'] += 1
            print(f"  ✗ {vid} 최종 실패")
    
    async with aiohttp.ClientSession() as session:
        tasks = [analyze_one(session, v) for v in to_analyze]
        await asyncio.gather(*tasks)
    
    print(f"\n분석 완료: {stats['processed']}개 처리, {stats['signals']}개 시그널, {stats['errors']}개 에러")
    
    # STEP 5: Insert signals
    if all_signals:
        print(f"\n=== STEP 5: 시그널 INSERT ({len(all_signals)}개) ===")
        import requests as req
        
        insert_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'resolution=merge-duplicates'
        }
        
        # Map signal types
        SIGNAL_MAP = {
            '매수': 'BUY', '긍정': 'POSITIVE', '중립': 'NEUTRAL',
            '경계': 'CONCERN', '매도': 'SELL',
            '강력매수': 'STRONG_BUY', '강력매도': 'STRONG_SELL'
        }
        
        inserted = 0
        for sig in all_signals:
            signal_type_kr = sig.get('signal_type', sig.get('signal', '중립'))
            signal_type_en = SIGNAL_MAP.get(signal_type_kr, 'NEUTRAL')
            
            confidence = sig.get('confidence', 5)
            if isinstance(confidence, str):
                try:
                    confidence = int(confidence)
                except:
                    confidence = 5
            
            row = {
                'channel_id': CHANNEL_ID,
                'video_id': sig['video_id'],
                'stock_name': sig.get('stock', ''),
                'ticker': sig.get('ticker'),
                'signal_type': signal_type_en,
                'key_quote': sig.get('key_quote', ''),
                'reasoning': sig.get('reasoning', ''),
                'timestamp': sig.get('timestamp', ''),
                'confidence': confidence,
                'status': 'pending'
            }
            
            r = req.post(
                f"{SUPABASE_URL}/rest/v1/influencer_signals",
                headers=insert_headers,
                json=row
            )
            if r.status_code in (200, 201):
                inserted += 1
            else:
                print(f"  시그널 INSERT 에러: {r.status_code} {r.text[:80]}")
        
        print(f"시그널 INSERT 완료: {inserted}/{len(all_signals)}")
    
    return stats['processed'], stats['signals']

# === MAIN ===
def main():
    print("=" * 60)
    print("세상학개론 누락 영상 파이프라인 시작")
    print(f"대상: {len(INVEST_IDS)}개 투자 영상")
    print("=" * 60)
    
    # Step 1 - SKIP (already done, 55 have subs, 12 have no transcripts)
    no_subs = []
    print("\n=== STEP 1: 자막 추출 (스킵 - 이미 완료) ===")
    
    # Step 2
    meta, meta_errors = step2_metadata()
    
    # Step 3
    video_errors = step3_insert_videos(meta)
    
    # Step 4-5
    processed, total_signals = asyncio.run(step4_5_analyze_and_insert())
    
    # Summary
    print("\n" + "=" * 60)
    print("파이프라인 완료!")
    print(f"  투자 영상: {len(INVEST_IDS)}개")
    print(f"  메타데이터 에러: {len(meta_errors)}개")
    print(f"  분석 처리: {processed}개")
    print(f"  총 시그널: {total_signals}개")
    print("=" * 60)

if __name__ == '__main__':
    main()
