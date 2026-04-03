# -*- coding: utf-8 -*-
"""강환국 배치 파이프라인 — 영상 ID 리스트로 자막 추출 + AI 분석 + DB 저장.
Usage:
  python scripts/kang_batch_pipeline.py --part A
  python scripts/kang_batch_pipeline.py --part B
"""
import sys, os, json, time, re, subprocess, argparse, traceback
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from pipeline_config import PipelineConfig
import requests
import glob

config = PipelineConfig()

CHANNEL_ID = '7fceea94-1874-44c0-b25b-cdd13fdeb722'
CHANNEL_NAME = '할 수 있다! 알고 투자'
CHANNEL_OWNER = '강환국'
SPEAKER_ID = '4ab064b4-79ee-4da8-bc47-c4feeb9f7b73'

SB_URL = config.SUPABASE_URL + "/rest/v1"
SB_HEADERS = {
    'apikey': config.SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {config.SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'resolution=merge-duplicates'
}

# Load prompt
PROMPT_PATH = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'pipeline_v14.0.md')
with open(PROMPT_PATH, encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

# API key
env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
ANTHROPIC_KEY = None
if os.path.exists(env_path):
    for line in open(env_path):
        if line.startswith('ANTHROPIC_API_KEY='):
            ANTHROPIC_KEY = line.split('=', 1)[1].strip()

try:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
except:
    print("ERROR: pip install anthropic")
    sys.exit(1)


def get_subtitle(video_id):
    """yt-dlp로 자막 추출"""
    tmp = f'/tmp/kang_{video_id}'
    try:
        subprocess.run(
            [sys.executable, '-m', 'yt_dlp',
             '--write-auto-sub', '--sub-lang', 'ko',
             '--skip-download', '-o', tmp,
             f'https://www.youtube.com/watch?v={video_id}'],
            capture_output=True, timeout=60
        )
        for f in glob.glob(f'{tmp}*.vtt') + glob.glob(f'{tmp}*.srt'):
            with open(f, encoding='utf-8', errors='replace') as fh:
                text = fh.read()
            os.remove(f)
            clean = re.sub(r'\d{2}:\d{2}:\d{2}[\.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[\.,]\d{3}', '', text)
            clean = re.sub(r'<[^>]+>', '', clean)
            clean = re.sub(r'WEBVTT.*?\n', '', clean)
            clean = re.sub(r'\n{2,}', '\n', clean).strip()
            # Deduplicate repeated lines (auto-sub artifact)
            lines = clean.split('\n')
            deduped = []
            for line in lines:
                line = line.strip()
                if line and (not deduped or line != deduped[-1]):
                    deduped.append(line)
            return '\n'.join(deduped)[:20000]
    except:
        pass
    return None


def get_video_meta(video_id):
    """yt-dlp로 영상 메타데이터 수집"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'yt_dlp',
             '--dump-json', '--skip-download',
             f'https://www.youtube.com/watch?v={video_id}'],
            capture_output=True, timeout=120
        )
        if result.returncode == 0 and result.stdout:
            stdout = result.stdout.decode('utf-8', errors='replace').strip()
            if stdout.startswith('{'):
                data = json.loads(stdout)
            else:
                return None

            return {
                'title': data.get('title', ''),
                'upload_date': data.get('upload_date', ''),
                'duration': data.get('duration', 0),
                'view_count': data.get('view_count', 0),
            }
    except Exception as e:
        print(f'    meta_error: {e}', flush=True)
    return None


def analyze_signals(subtitle, title, duration_info=''):
    """Claude Sonnet으로 시그널 분석"""
    prompt = SYSTEM_PROMPT.replace('{VIDEO_DURATION_INFO}', duration_info)
    prompt += f"\n\n채널 운영자: {CHANNEL_OWNER}"

    user_msg = f"영상 제목: {title}\n\n자막:\n{subtitle}"

    for attempt in range(3):
        try:
            r = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0,
                system=prompt,
                messages=[{"role": "user", "content": user_msg}]
            )
            text = r.content[0].text.strip()
            # Extract JSON
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                return json.loads(json_match.group())
            return {"signals": []}
        except Exception as e:
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                print(f'    AI 분석 실패: {str(e)[:80]}')
                return {"signals": []}


def insert_video(video_id, title, published_at, duration):
    """influencer_videos 테이블에 INSERT"""
    row = {
        'video_id': video_id,
        'channel_id': CHANNEL_ID,
        'title': title,
        'published_at': published_at,
        'duration_seconds': duration,
    }
    insert_headers = dict(SB_HEADERS)
    insert_headers['Prefer'] = 'return=representation,resolution=merge-duplicates'
    r = requests.post(
        f"{SB_URL}/influencer_videos?on_conflict=video_id",
        headers=insert_headers,
        json=row
    )
    if r.status_code in (200, 201):
        try:
            data = r.json()
            return data[0]['id'] if data else None
        except:
            pass
    # GET existing
    r2 = requests.get(
        f"{SB_URL}/influencer_videos?video_id=eq.{video_id}&select=id",
        headers={'apikey': config.SUPABASE_SERVICE_KEY, 'Authorization': f'Bearer {config.SUPABASE_SERVICE_KEY}'}
    )
    try:
        data = r2.json()
        return data[0]['id'] if data else None
    except:
        return None


def map_confidence(val):
    """정수 confidence → DB enum 변환"""
    if isinstance(val, str):
        return val
    if val is None:
        return 'medium'
    v = int(val)
    if v >= 9: return 'very_high'
    if v >= 7: return 'high'
    if v >= 5: return 'medium'
    return 'low'


def insert_signals(db_video_id, signals):
    """influencer_signals 테이블에 INSERT"""
    count = 0
    for sig in signals:
        row = {
            'video_id': db_video_id,
            'speaker_id': SPEAKER_ID,
            'stock': sig.get('stock', ''),
            'ticker': sig.get('ticker'),
            'market': sig.get('market', ''),
            'signal': sig.get('signal_type', '중립'),
            'mention_type': '결론',
            'confidence': map_confidence(sig.get('confidence', 5)),
            'timestamp': sig.get('timestamp'),
            'key_quote': sig.get('key_quote', ''),
            'reasoning': sig.get('reasoning', ''),
            'pipeline_version': 'V14.0',
        }
        r = requests.post(
            f"{SB_URL}/influencer_signals",
            headers=SB_HEADERS,
            json=row
        )
        if r.status_code in (200, 201):
            count += 1
        else:
            print(f'    insert_signal FAIL: {r.status_code} {r.text[:150]}', flush=True)
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--part', required=True, choices=['A', 'B'])
    parser.add_argument('--start', type=int, default=0, help='Resume from index')
    args = parser.parse_args()

    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    video_ids = json.load(open(os.path.join(data_dir, f'_kang_part{args.part}.json'), encoding='utf-8'))

    print(f'[파트{args.part}] {len(video_ids)}개 영상, start={args.start}')
    print(f'시작: {time.strftime("%Y-%m-%d %H:%M")}', flush=True)

    total_signals = 0
    processed = 0
    errors = 0
    api_calls = 0

    for i in range(args.start, len(video_ids)):
        vid = video_ids[i]

        try:
            # 1. 메타데이터
            meta = get_video_meta(vid)
            if not meta:
                print(f'[{i+1:4d}/{len(video_ids)}] {vid}: 메타데이터 없음 (skip)', flush=True)
                errors += 1
                time.sleep(1)
                continue

            title = meta['title']
            upload_date = meta.get('upload_date', '')
            if upload_date and len(upload_date) == 8:
                published_at = f'{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}'
            else:
                published_at = None
            duration = meta.get('duration', 0)

            # Skip shorts/too long
            if duration and (duration < 60 or duration > 7200):
                time.sleep(0.5)
                continue

            # 2. 자막
            subtitle = get_subtitle(vid)
            if not subtitle or len(subtitle) < 100:
                time.sleep(1)
                continue

            # 3. AI 분석
            duration_info = f'{duration//60}분 {duration%60}초' if duration else ''
            result = analyze_signals(subtitle, title, duration_info)
            signals = result.get('signals', [])
            api_calls += 1

            # 4. DB 저장
            if signals:
                db_vid = insert_video(vid, title, published_at, duration)
                if db_vid:
                    inserted = insert_signals(db_vid, signals)
                    total_signals += inserted
                    print(f'[{i+1:4d}/{len(video_ids)}] {title[:40]:40s} → {inserted}건', flush=True)
                else:
                    print(f'[{i+1:4d}/{len(video_ids)}] {title[:40]:40s} → video INSERT 실패', flush=True)
                    errors += 1
            else:
                # 시그널 없어도 video는 등록 (중복 방지)
                insert_video(vid, title, published_at, duration)

            processed += 1

            # Rate limit: 20개마다 60초 휴식
            if api_calls > 0 and api_calls % 20 == 0:
                print(f'  --- Rate limit 휴식 60초 (api_calls={api_calls}) ---', flush=True)
                time.sleep(60)
            else:
                time.sleep(5)

        except Exception as e:
            import traceback
            print(f'[{i+1:4d}/{len(video_ids)}] {vid}: ERROR {str(e)[:80]}', flush=True)
            traceback.print_exc()
            errors += 1
            time.sleep(5)

        # 50개마다 진행 보고
        if (i + 1) % 50 == 0:
            print(f'  === 파트{args.part} {i+1}/{len(video_ids)} | 시그널 {total_signals}건 | 에러 {errors} ===', flush=True)

    print(f'\n{"="*60}')
    print(f'파트{args.part} 완료: {processed}건 처리, {total_signals}건 시그널, {errors}건 에러')
    print(f'{"="*60}', flush=True)


if __name__ == '__main__':
    main()
