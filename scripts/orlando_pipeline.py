#!/usr/bin/env python3
"""올랜도 킴 미국주식 채널 파이프라인 - 자막추출 → 시그널분석 → DB INSERT"""

import json, os, sys, time, uuid, re, traceback
from datetime import datetime
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load env
load_dotenv(Path(__file__).parent.parent / '.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
ANTHROPIC_KEY = os.getenv('ANTHROPIC_API_KEY')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

BASE_URL = f"{SUPABASE_URL}/rest/v1"
DATA_DIR = Path(__file__).parent.parent / 'data'
SUBTITLE_DIR = DATA_DIR / 'orlando_subtitles'
SIGNAL_DIR = DATA_DIR / 'orlando_signals'
SUBTITLE_DIR.mkdir(exist_ok=True)
SIGNAL_DIR.mkdir(exist_ok=True)

# Load prompt
PROMPT_PATH = Path(__file__).parent.parent / 'prompts' / 'pipeline_v10.md'
PROMPT = PROMPT_PATH.read_text(encoding='utf-8')


def supabase_get(table, params):
    r = requests.get(f"{BASE_URL}/{table}", headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()


def supabase_post(table, data):
    r = requests.post(f"{BASE_URL}/{table}", headers=HEADERS, json=data)
    if r.status_code >= 400:
        print(f"  [ERROR] POST {table}: {r.status_code} {r.text[:200]}")
    r.raise_for_status()
    return r.json()


def step1_register_channel_speaker():
    """채널/스피커 등록"""
    print("=== Step 1: 채널/스피커 등록 ===")
    
    # Check existing channel
    existing = supabase_get('influencer_channels', {
        'channel_handle': 'eq.@orlandocampus', 'select': 'id'
    })
    if existing:
        channel_id = existing[0]['id']
        print(f"  기존 채널: {channel_id}")
    else:
        channel_data = {
            'id': str(uuid.uuid4()),
            'channel_name': '올랜도 킴 미국주식',
            'channel_handle': '@orlandocampus',
            'channel_url': 'https://www.youtube.com/@orlandocampus',
            'platform': 'youtube',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        result = supabase_post('influencer_channels', channel_data)
        channel_id = result[0]['id']
        print(f"  새 채널 생성: {channel_id}")
    
    # Check existing speaker
    existing_sp = supabase_get('speakers', {
        'name': 'eq.올랜도 킴', 'select': 'id'
    })
    if existing_sp:
        speaker_id = existing_sp[0]['id']
        print(f"  기존 스피커: {speaker_id}")
    else:
        speaker_data = {
            'id': str(uuid.uuid4()),
            'name': '올랜도 킴',
            'aliases': '{올랜도킴,올랜도}',
            'created_at': datetime.now().isoformat()
        }
        result = supabase_post('speakers', speaker_data)
        speaker_id = result[0]['id']
        print(f"  새 스피커 생성: {speaker_id}")
    
    return channel_id, speaker_id


def step2_extract_subtitles(videos):
    """자막 추출 (yt-dlp)"""
    print(f"\n=== Step 2: 자막 추출 ({len(videos)}개) ===")
    
    results = {}  # video_id -> subtitle_text or None
    no_subtitle = []
    
    for i, v in enumerate(videos):
        vid = v['id'].strip('\ufeff')
        sub_file = SUBTITLE_DIR / f"{vid}.txt"
        
        # Skip if already extracted
        if sub_file.exists():
            text = sub_file.read_text(encoding='utf-8').strip()
            if text:
                results[vid] = text
                continue
            
        print(f"  [{i+1}/{len(videos)}] {vid} - {v['title'][:40]}")
        
        try:
            import yt_dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['ko'],
                'subtitlesformat': 'json3',
                'outtmpl': str(SUBTITLE_DIR / f"{vid}"),
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=True)
            
            # Find subtitle file
            sub_json = SUBTITLE_DIR / f"{vid}.ko.json3"
            if not sub_json.exists():
                # Try auto-generated
                for ext in ['ko.json3', 'ko.vtt', 'ko.srv3']:
                    candidate = SUBTITLE_DIR / f"{vid}.{ext}"
                    if candidate.exists():
                        sub_json = candidate
                        break
            
            if sub_json.exists() and sub_json.suffix == '.json3':
                with open(sub_json, 'r', encoding='utf-8') as f:
                    sub_data = json.load(f)
                
                # Parse json3 format
                lines = []
                seen = set()
                for event in sub_data.get('events', []):
                    if 'segs' not in event:
                        continue
                    ts_ms = event.get('tStartMs', 0)
                    ts_sec = ts_ms // 1000
                    mins, secs = divmod(ts_sec, 60)
                    text_parts = [s.get('utf8', '') for s in event['segs']]
                    text = ''.join(text_parts).strip()
                    if text and text not in seen:
                        seen.add(text)
                        lines.append(f"[{mins}:{secs:02d}] {text}")
                
                subtitle_text = '\n'.join(lines)
                sub_file.write_text(subtitle_text, encoding='utf-8')
                results[vid] = subtitle_text
                print(f"    [OK] {len(lines)}줄")
            else:
                sub_file.write_text('', encoding='utf-8')
                no_subtitle.append(vid)
                print(f"    [FAIL] 자막 없음")
                
        except Exception as e:
            err = str(e)
            if '429' in err or 'Too Many' in err:
                print(f"    [WARN] 429 - 60초 대기")
                time.sleep(60)
                # Don't mark as no subtitle, will retry
            else:
                print(f"    [FAIL] 에러: {err[:80]}")
                no_subtitle.append(vid)
                sub_file.write_text('', encoding='utf-8')
        
        # Minimal delay
        time.sleep(0.5)
    
    print(f"\n  자막 추출 완료: {len(results)}개 성공, {len(no_subtitle)}개 실패")
    return results, no_subtitle


def step3_extract_signals(subtitles, videos_dict):
    """Claude Sonnet으로 시그널 추출"""
    print(f"\n=== Step 3: 시그널 추출 ({len(subtitles)}개) ===")
    
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    
    all_signals = {}
    total_cost = 0.0
    
    for i, (vid, subtitle_text) in enumerate(subtitles.items()):
        signal_file = SIGNAL_DIR / f"{vid}.json"
        
        # Skip if already analyzed
        if signal_file.exists():
            try:
                existing = json.loads(signal_file.read_text(encoding='utf-8'))
                all_signals[vid] = existing.get('signals', [])
                continue
            except:
                pass
        
        video_info = videos_dict.get(vid, {})
        title = video_info.get('title', 'Unknown')
        
        print(f"  [{i+1}/{len(subtitles)}] {vid} - {title[:40]}")
        
        # Truncate very long subtitles
        sub_truncated = subtitle_text[:15000] if len(subtitle_text) > 15000 else subtitle_text
        
        user_msg = f"""다음 YouTube 영상의 자막을 분석하여 투자 시그널을 추출하세요.

## 영상 정보
- 제목: {title}
- 채널: 올랜도 킴 미국주식
- 화자: 올랜도 킴
- 영상 길이: {video_info.get('duration', 'N/A')}초

## 자막
{sub_truncated}

위 프롬프트 규칙에 따라 시그널을 JSON으로 추출하세요. 반드시 순수 JSON만 출력하세요."""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=PROMPT,
                messages=[{"role": "user", "content": user_msg}]
            )
            
            # Cost estimation
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = (input_tokens * 3 / 1_000_000) + (output_tokens * 15 / 1_000_000)
            total_cost += cost
            
            # Parse response
            text = response.content[0].text.strip()
            # Extract JSON from possible markdown
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(text)
            signals = result.get('signals', [])
            
            # Save
            signal_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            all_signals[vid] = signals
            
            print(f"    [OK] {len(signals)}개 시그널 (${cost:.4f})")
            
            if total_cost > 5.0:
                print(f"\n  [WARN] 비용 한도 초과! ${total_cost:.2f}")
                break
                
        except Exception as e:
            print(f"    [FAIL] 에러: {str(e)[:80]}")
            all_signals[vid] = []
        
        time.sleep(3)  # API rate limit
    
    total_signals = sum(len(s) for s in all_signals.values())
    print(f"\n  시그널 추출 완료: {total_signals}개 (총 비용: ${total_cost:.2f})")
    return all_signals, total_cost


def step4_validate(all_signals):
    """QA 검증"""
    print(f"\n=== Step 4: QA 검증 ===")
    
    valid_signals = {}
    rejected = 0
    
    VALID_SIGNAL_TYPES = {'매수', '긍정', '중립', '경계', '매도'}
    
    for vid, signals in all_signals.items():
        valid = []
        for sig in signals:
            issues = []
            
            stock = sig.get('stock', '')
            signal_type = sig.get('signal_type', '')
            key_quote = sig.get('key_quote', '')
            reasoning = sig.get('reasoning', '')
            timestamp = sig.get('timestamp', '')
            confidence = sig.get('confidence', 0)
            
            # Basic validation
            if not stock:
                issues.append('stock 없음')
            if signal_type not in VALID_SIGNAL_TYPES:
                issues.append(f'잘못된 signal_type: {signal_type}')
            if len(key_quote) < 20:
                issues.append(f'key_quote 짧음: {len(key_quote)}')
            if len(reasoning) < 50:
                issues.append(f'reasoning 짧음: {len(reasoning)}')
            if timestamp in ('0:00', '00:00', ''):
                issues.append('timestamp 무효')
            if isinstance(confidence, (int, float)) and confidence < 4:
                issues.append(f'confidence 낮음: {confidence}')
            
            # Check stock is Korean
            if stock and re.match(r'^[A-Za-z\s]+$', stock):
                # All English - reject unless exceptions
                if stock not in ('AMD', 'TSMC', 'ASML'):
                    issues.append(f'stock 영문: {stock}')
            
            if issues:
                rejected += 1
                print(f"    [FAIL] {vid[:8]}.. {stock}: {', '.join(issues)}")
            else:
                valid.append(sig)
        
        if valid:
            valid_signals[vid] = valid
    
    total_valid = sum(len(s) for s in valid_signals.values())
    print(f"\n  검증 완료: {total_valid}개 통과, {rejected}개 거부")
    return valid_signals


def step5_db_insert(valid_signals, channel_id, speaker_id, videos_dict):
    """DB INSERT"""
    print(f"\n=== Step 5: DB INSERT ===")
    
    inserted_videos = 0
    inserted_signals = 0
    errors = 0
    
    for vid, signals in valid_signals.items():
        video_info = videos_dict.get(vid, {})
        
        try:
            # Check/create video
            existing_v = supabase_get('influencer_videos', {
                'video_id': f'eq.{vid}', 'select': 'id'
            })
            
            if existing_v:
                video_uuid = existing_v[0]['id']
            else:
                # Get subtitle
                sub_file = SUBTITLE_DIR / f"{vid}.txt"
                subtitle_text = sub_file.read_text(encoding='utf-8') if sub_file.exists() else None
                
                video_data = {
                    'id': str(uuid.uuid4()),
                    'video_id': vid,
                    'channel_id': channel_id,
                    'title': video_info.get('title', ''),
                    'published_at': None,  # date is NA
                    'duration_seconds': int(float(video_info.get('duration', 0))) if video_info.get('duration') else None,
                    'has_subtitle': True,
                    'subtitle_language': 'ko',
                    'subtitle_text': subtitle_text[:50000] if subtitle_text else None,
                    'pipeline_version': 'V10.10',
                    'created_at': datetime.now().isoformat()
                }
                result = supabase_post('influencer_videos', video_data)
                video_uuid = result[0]['id']
                inserted_videos += 1
            
            # Insert signals (check duplicates)
            for sig in signals:
                stock = sig.get('stock', '')
                
                # Check duplicate
                existing_s = supabase_get('influencer_signals', {
                    'video_id': f'eq.{video_uuid}',
                    'stock': f'eq.{stock}',
                    'select': 'id'
                })
                
                if existing_s:
                    continue
                
                signal_data = {
                    'id': str(uuid.uuid4()),
                    'video_id': video_uuid,
                    'speaker_id': speaker_id,
                    'stock': stock,
                    'ticker': sig.get('ticker'),
                    'market': sig.get('market', 'US'),
                    'signal': sig.get('signal_type', '중립'),
                    'confidence': str(sig.get('confidence', 'medium')),
                    'timestamp': sig.get('timestamp', ''),
                    'key_quote': sig.get('key_quote', ''),
                    'reasoning': sig.get('reasoning', ''),
                    'review_status': 'pending',
                    'pipeline_version': 'V10.10',
                    'created_at': datetime.now().isoformat()
                }
                
                try:
                    supabase_post('influencer_signals', signal_data)
                    inserted_signals += 1
                except:
                    errors += 1
                    
        except Exception as e:
            print(f"  [FAIL] {vid}: {str(e)[:80]}")
            errors += 1
    
    print(f"\n  DB INSERT 완료: 영상 {inserted_videos}개, 시그널 {inserted_signals}개, 에러 {errors}개")
    return inserted_videos, inserted_signals, errors


def main():
    print("=" * 60)
    print("올랜도 킴 미국주식 파이프라인 V10.10")
    print("=" * 60)
    
    # Load video list
    videos_file = DATA_DIR / 'orlando_filter_final.json'
    with open(videos_file, 'r', encoding='utf-8-sig') as f:
        videos = json.load(f)
    
    # Clean BOM from ids
    for v in videos:
        v['id'] = v['id'].strip('\ufeff')
    
    videos_dict = {v['id']: v for v in videos}
    print(f"대상 영상: {len(videos)}개\n")
    
    # Step 1
    channel_id, speaker_id = step1_register_channel_speaker()
    
    # Step 2
    subtitles, no_subtitle = step2_extract_subtitles(videos)
    
    # Step 3
    all_signals, cost = step3_extract_signals(subtitles, videos_dict)
    
    # Step 4
    valid_signals = step4_validate(all_signals)
    
    # Step 5
    v_count, s_count, e_count = step5_db_insert(valid_signals, channel_id, speaker_id, videos_dict)
    
    # Summary
    total_signals = sum(len(s) for s in valid_signals.values())
    print("\n" + "=" * 60)
    print("최종 결과:")
    print(f"  총 영상: {len(videos)}개")
    print(f"  자막 추출: {len(subtitles)}개 성공, {len(no_subtitle)}개 실패")
    print(f"  시그널 추출: {total_signals}개")
    print(f"  DB INSERT: 영상 {v_count}개, 시그널 {s_count}개, 에러 {e_count}개")
    print(f"  총 비용: ${cost:.2f}")
    print("=" * 60)
    
    return {
        'total_videos': len(videos),
        'subtitles_ok': len(subtitles),
        'no_subtitle': len(no_subtitle),
        'total_signals': total_signals,
        'inserted_videos': v_count,
        'inserted_signals': s_count,
        'errors': e_count,
        'cost': cost
    }


if __name__ == '__main__':
    main()


