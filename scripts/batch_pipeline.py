# -*- coding: utf-8 -*-
"""범용 배치 파이프라인 — 채널 지정 + 모델 선택으로 자막→AI 분석→DB 저장.

Usage:
  python scripts/batch_pipeline.py --channel 선대인TV --model gpt4o --all
  python scripts/batch_pipeline.py --channel 강환국 --model sonnet --start 0 --end 100
  python scripts/batch_pipeline.py --channel 선대인TV --model gpt4o --all --skip-existing
"""
import sys, os, json, time, re, subprocess, argparse, traceback
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from pipeline_config import PipelineConfig
import requests
import glob

config = PipelineConfig()

# ── 환경변수 ──
env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
ENV = {}
if os.path.exists(env_path):
    for line in open(env_path, encoding='utf-8'):
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            ENV[k.strip()] = v.strip()

SB_URL = config.SUPABASE_URL + "/rest/v1"
SB_KEY = config.SUPABASE_SERVICE_KEY
SB_HEADERS = {
    'apikey': SB_KEY,
    'Authorization': f'Bearer {SB_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'resolution=merge-duplicates'
}
SB_READ = {'apikey': SB_KEY, 'Authorization': f'Bearer {SB_KEY}'}

# ── 프롬프트 (V14.0 운영) ──
PROMPT_PATH = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'pipeline_v14.0.md')
with open(PROMPT_PATH, encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()


# ── AI 클라이언트 초기화 ──
def init_ai(model_name):
    if model_name == 'gpt4o':
        from openai import OpenAI
        return OpenAI(api_key=ENV.get('OPENAI_API_KEY', ''))
    else:
        import anthropic
        return anthropic.Anthropic(api_key=ENV.get('ANTHROPIC_API_KEY', ''))


# ── Supabase 조회 헬퍼 ──
def sb_get(path):
    r = requests.get(f"{SB_URL}/{path}", headers=SB_READ)
    return r.json() if r.status_code == 200 else []


def resolve_channel(channel_name):
    """채널명 → (channel_id, channel_owner, speaker_id)"""
    rows = sb_get(f"influencer_channels?channel_name=eq.{channel_name}&select=id")
    if not rows:
        # 부분 매칭
        rows = sb_get(f"influencer_channels?channel_name=like.*{channel_name}*&select=id,channel_name")
        if rows:
            print(f"  유사 채널: {[r['channel_name'] for r in rows]}")
        return None, None, None
    ch_id = rows[0]['id']

    owner_name = PipelineConfig.get_channel_owner(channel_name) or channel_name
    sp_rows = sb_get(f"speakers?name=eq.{owner_name}&select=id")
    speaker_id = sp_rows[0]['id'] if sp_rows else None

    return ch_id, owner_name, speaker_id


def get_channel_videos(channel_id):
    """채널의 모든 video_id 조회 (published_at 순)"""
    all_vids = []
    offset = 0
    while True:
        rows = sb_get(f"influencer_videos?channel_id=eq.{channel_id}&select=id,video_id,title&order=published_at.asc&offset={offset}&limit=1000")
        if not rows:
            break
        all_vids.extend(rows)
        if len(rows) < 1000:
            break
        offset += 1000
    return all_vids


def get_videos_with_signals(channel_id):
    """이미 시그널이 있는 video의 DB id set"""
    videos = get_channel_videos(channel_id)
    if not videos:
        return set()
    vid_ids = [v['id'] for v in videos]
    has_signals = set()
    for i in range(0, len(vid_ids), 100):
        chunk = vid_ids[i:i+100]
        ids_str = ','.join(chunk)
        rows = sb_get(f"influencer_signals?video_id=in.({ids_str})&select=video_id")
        for r in rows:
            has_signals.add(r['video_id'])
    return has_signals


# ── 자막/메타 ──
def get_subtitle(video_id):
    tmp = f'/tmp/bp_{video_id}'
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
                return {
                    'title': data.get('title', ''),
                    'upload_date': data.get('upload_date', ''),
                    'duration': data.get('duration', 0),
                }
    except Exception as e:
        print(f'    meta_error: {e}', flush=True)
    return None


# ── AI 분석 ──
def analyze_signals(ai_client, model_name, subtitle, title, channel_owner, duration_info=''):
    prompt = SYSTEM_PROMPT.replace('{VIDEO_DURATION_INFO}', duration_info)
    prompt += f"\n\n채널 운영자: {channel_owner}"
    user_msg = f"영상 제목: {title}\n\n자막:\n{subtitle}"

    for attempt in range(3):
        try:
            if model_name == 'gpt4o':
                r = ai_client.chat.completions.create(
                    model="gpt-4o",
                    temperature=0,
                    max_tokens=4096,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": user_msg},
                    ],
                )
                text = r.choices[0].message.content.strip()
            else:
                r = ai_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    temperature=0,
                    system=prompt,
                    messages=[{"role": "user", "content": user_msg}],
                )
                text = r.content[0].text.strip()

            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                return json.loads(json_match.group())
            return {"signals": []}
        except Exception as e:
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                print(f'    AI 분석 실패: {str(e)[:80]}', flush=True)
                return {"signals": []}


# ── DB 저장 ──
def insert_video(video_id, channel_id, title, published_at, duration):
    row = {
        'video_id': video_id,
        'channel_id': channel_id,
        'title': title,
        'published_at': published_at,
        'duration_seconds': duration,
    }
    h = dict(SB_HEADERS)
    h['Prefer'] = 'return=representation,resolution=merge-duplicates'
    r = requests.post(f"{SB_URL}/influencer_videos?on_conflict=video_id", headers=h, json=row)
    if r.status_code in (200, 201):
        try:
            return r.json()[0]['id']
        except:
            pass
    r2 = requests.get(f"{SB_URL}/influencer_videos?video_id=eq.{video_id}&select=id", headers=SB_READ)
    try:
        return r2.json()[0]['id']
    except:
        return None


def insert_signals(db_video_id, speaker_id, signals, model_name):
    count = 0
    pv = f'V14.0-GPT4o' if model_name == 'gpt4o' else 'V14.0'
    for sig in signals:
        row = {
            'video_id': db_video_id,
            'speaker_id': speaker_id,
            'stock': sig.get('stock', ''),
            'ticker': sig.get('ticker'),
            'market': sig.get('market', ''),
            'signal': sig.get('signal_type', '중립'),
            'mention_type': '결론',
            'confidence': sig.get('confidence', 5),
            'timestamp': sig.get('timestamp'),
            'key_quote': sig.get('key_quote', ''),
            'reasoning': sig.get('reasoning', ''),
            'pipeline_version': pv,
        }
        r = requests.post(f"{SB_URL}/influencer_signals", headers=SB_HEADERS, json=row)
        if r.status_code in (200, 201):
            count += 1
    return count


# ── 메인 ──
def main():
    parser = argparse.ArgumentParser(description='범용 배치 파이프라인')
    parser.add_argument('--channel', required=True, help='채널명 (Supabase influencer_channels)')
    parser.add_argument('--model', choices=['gpt4o', 'sonnet'], default='gpt4o', help='AI 모델 (기본: gpt4o)')
    parser.add_argument('--start', type=int, default=0, help='시작 인덱스')
    parser.add_argument('--end', type=int, default=None, help='끝 인덱스 (exclusive)')
    parser.add_argument('--all', action='store_true', help='전체 영상 처리')
    parser.add_argument('--skip-existing', action='store_true', help='이미 시그널 있는 영상 건너뛰기')
    args = parser.parse_args()

    model_label = 'GPT-4o' if args.model == 'gpt4o' else 'Sonnet'
    print(f"\n{'='*60}")
    print(f"  배치 파이프라인 | {args.channel} | {model_label}")
    print(f"{'='*60}")

    # 1) 채널 조회
    print(f"\n[1] 채널 조회: {args.channel}")
    channel_id, owner_name, speaker_id = resolve_channel(args.channel)
    if not channel_id:
        print(f"  ❌ 채널 '{args.channel}' 없음")
        sys.exit(1)
    print(f"  채널 ID: {channel_id}")
    print(f"  운영자: {owner_name}")
    print(f"  Speaker ID: {speaker_id or '(없음 — 새 speaker 등록 필요)'}")

    if not speaker_id:
        print("  ❌ speaker_id 없음. speakers 테이블에 등록 필요.")
        sys.exit(1)

    # 2) 영상 목록
    print(f"[2] 영상 목록 조회...")
    videos = get_channel_videos(channel_id)
    print(f"  총 영상: {len(videos)}개")

    if not videos:
        print("  ❌ 영상 없음")
        sys.exit(1)

    # skip-existing
    skip_db_ids = set()
    if args.skip_existing:
        skip_db_ids = get_videos_with_signals(channel_id)
        print(f"  시그널 있는 영상: {len(skip_db_ids)}개 (건너뛰기)")

    # 범위
    start = args.start
    end = args.end if args.end is not None else len(videos)
    if args.all:
        start, end = 0, len(videos)
    target = videos[start:end]
    print(f"  처리 범위: [{start}:{end}] = {len(target)}개")

    # 3) AI 클라이언트
    print(f"[3] {model_label} 클라이언트 초기화...")
    ai_client = init_ai(args.model)

    # 4) 처리
    print(f"[4] 처리 시작: {time.strftime('%Y-%m-%d %H:%M')}\n")
    total_signals = 0
    processed = 0
    skipped = 0
    errors = 0
    api_calls = 0

    for idx, vid_row in enumerate(target):
        global_idx = start + idx
        db_vid_id = vid_row['id']
        yt_vid_id = vid_row['video_id']

        # skip existing
        if args.skip_existing and db_vid_id in skip_db_ids:
            skipped += 1
            continue

        try:
            # meta
            meta = get_video_meta(yt_vid_id)
            if not meta:
                errors += 1
                time.sleep(1)
                continue

            title = meta['title']
            upload_date = meta.get('upload_date', '')
            published_at = f'{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}' if upload_date and len(upload_date) == 8 else None
            duration = meta.get('duration', 0)

            if duration and (duration < 60 or duration > 7200):
                time.sleep(0.5)
                continue

            # subtitle
            subtitle = get_subtitle(yt_vid_id)
            if not subtitle or len(subtitle) < 100:
                time.sleep(1)
                continue

            # AI
            duration_info = f'{duration//60}분 {duration%60}초' if duration else ''
            result = analyze_signals(ai_client, args.model, subtitle, title, owner_name, duration_info)
            signals = result.get('signals', [])
            api_calls += 1

            # DB
            if signals:
                db_vid = insert_video(yt_vid_id, channel_id, title, published_at, duration)
                if db_vid:
                    inserted = insert_signals(db_vid, speaker_id, signals, args.model)
                    total_signals += inserted
                    print(f'[{global_idx+1:4d}] {title[:42]:42s} → {inserted}건', flush=True)
                else:
                    errors += 1
            else:
                insert_video(yt_vid_id, channel_id, title, published_at, duration)

            processed += 1

            # rate limit
            if args.model == 'gpt4o':
                sleep_time = 2
                batch_interval = 50
            else:
                sleep_time = 5
                batch_interval = 20

            if api_calls > 0 and api_calls % batch_interval == 0:
                pause = 10 if args.model == 'gpt4o' else 60
                print(f'  --- 휴식 {pause}초 (api={api_calls}, 시그널={total_signals}) ---', flush=True)
                time.sleep(pause)
            else:
                time.sleep(sleep_time)

        except Exception as e:
            print(f'[{global_idx+1:4d}] {yt_vid_id}: ERROR {str(e)[:80]}', flush=True)
            errors += 1
            time.sleep(5)

        if (idx + 1) % 50 == 0:
            print(f'  === {idx+1}/{len(target)} | 시그널 {total_signals} | 에러 {errors} | skip {skipped} ===', flush=True)

    print(f'\n{"="*60}')
    print(f'  {args.channel} | {model_label} 완료')
    print(f'  처리: {processed} | 시그널: {total_signals} | 에러: {errors} | skip: {skipped}')
    print(f'  종료: {time.strftime("%Y-%m-%d %H:%M")}')
    print(f'{"="*60}', flush=True)


if __name__ == '__main__':
    main()
