#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GODofIT 채널 시그널 분석 스크립트
- VTT 자막 파일 읽어서 V11 프롬프트로 분석
- REST API로 Supabase DB INSERT
- 진행상황 저장 (중단점 복구 가능)

실제 DB 스키마 기준:
  influencer_channels: id, channel_name, channel_handle, channel_url, platform, subscriber_count, description
  influencer_videos: id, channel_id, video_id, title, published_at, duration_seconds, has_subtitle, subtitle_language, analyzed_at, pipeline_version, signal_count, video_summary, subtitle_text
  influencer_signals: id, video_id, speaker_id, stock, ticker, market, mention_type, signal, confidence, timestamp, key_quote, reasoning, review_status, pipeline_version
"""

import os, sys, json, re, time, glob
from datetime import datetime

# --- 경로 설정 ---
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
SUBS_DIR = r'C:\Users\Mario\work\invest-sns\subs'
PROMPT_PATH = r'C:\Users\Mario\work\prompts\pipeline_v11.md'
PROGRESS_FILE = r'C:\Users\Mario\work\invest-sns\pipeline\data\godofIT_progress.json'
LOG_FILE = r'C:\Users\Mario\work\invest-sns\pipeline\data\godofIT_log.txt'

SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY', 'YOUR_ANTHROPIC_API_KEY_HERE')
MODEL = 'claude-sonnet-4-20250514'

CHANNEL_URL = 'https://www.youtube.com/@GODofIT'
CHANNEL_NAME = 'GODofIT'
CHANNEL_HANDLE = '@GODofIT'

# TEST_MODE: True이면 처음 5개만 실행
TEST_MODE = '--test' in sys.argv or os.environ.get('TEST_MODE') == '1'

# 데이터 디렉토리 생성
os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)


def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = '[{}] {}'.format(ts, msg)
    try:
        print(line, flush=True)
    except UnicodeEncodeError:
        print(line.encode('ascii', errors='replace').decode('ascii'), flush=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def sleep(s):
    time.sleep(s)


def load_prompt():
    with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
        return f.read()


def parse_vtt(vtt_path):
    """VTT 자막 파일에서 텍스트 추출"""
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = []
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('WEBVTT') or line.startswith('NOTE') or line.startswith('Kind:') or line.startswith('Language:'):
            continue
        if '-->' in line:
            continue
        if re.match(r'^\d+$', line):
            continue
        line = re.sub(r'<[^>]+>', '', line)
        if line:
            lines.append(line)
    # 중복 제거 (연속 같은 줄)
    deduped = []
    prev = None
    for l in lines:
        if l != prev:
            deduped.append(l)
        prev = l
    return ' '.join(deduped[:3000])


def get_video_id_from_filename(filename):
    """파일명에서 YouTube video_id 추출
    패턴1: AbcdXyz.ko.vtt -> AbcdXyz (11자 ID)
    패턴2: wsaj_AbcdXyz_제목.ko.vtt -> AbcdXyz (wsaj_ 이후 11자)
    """
    base = filename.replace('.ko.vtt', '')
    if base.startswith('wsaj_') and len(base) > 16:
        # wsaj_ 다음 11자가 YouTube ID
        return base[5:16]
    return base


def call_anthropic(prompt_text):
    """Claude API 호출"""
    import urllib.request
    import urllib.error

    headers = {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_KEY,
        'anthropic-version': '2023-06-01'
    }
    body = json.dumps({
        'model': MODEL,
        'max_tokens': 4000,
        'messages': [{'role': 'user', 'content': prompt_text}]
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=body,
        headers=headers,
        method='POST'
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return result['content'][0]['text'], result.get('usage', {})
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            if e.code == 429:
                log('  Rate limit (429). 60초 대기...')
                sleep(60)
                continue
            elif e.code == 529:
                log('  과부하 (529). 30초 대기...')
                sleep(30)
                continue
            else:
                log('  HTTP 오류 {}: {}'.format(e.code, err_body[:300]))
                return None, {}
        except Exception as ex:
            log('  API 오류: {}'.format(ex))
            sleep(5)
    return None, {}


def parse_signals_from_response(text):
    """응답에서 JSON 시그널 추출"""
    # ```json [...] ``` 패턴
    m = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # 직접 [] 배열 찾기
    m = re.search(r'(\[.*\])', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    return []


def rest_get(path, params=''):
    """Supabase REST GET"""
    import urllib.request
    url = '{}/rest/v1/{}?{}'.format(SUPABASE_URL, path, params)
    req = urllib.request.Request(url, headers={
        'apikey': SUPABASE_KEY,
        'Authorization': 'Bearer {}'.format(SUPABASE_KEY)
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        log('  REST GET 오류 ({}): {}'.format(path, e))
        return []


def rest_post(path, data):
    """Supabase REST POST"""
    import urllib.request
    import urllib.error
    url = '{}/rest/v1/{}'.format(SUPABASE_URL, path)
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers={
        'apikey': SUPABASE_KEY,
        'Authorization': 'Bearer {}'.format(SUPABASE_KEY),
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        log('  REST POST 오류 ({}): {} {}'.format(path, e.code, e.read().decode()[:300]))
        return None
    except Exception as e:
        log('  REST POST 오류 ({}): {}'.format(path, e))
        return None


def rest_patch(path, params, data):
    """Supabase REST PATCH"""
    import urllib.request
    import urllib.error
    url = '{}/rest/v1/{}?{}'.format(SUPABASE_URL, path, params)
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers={
        'apikey': SUPABASE_KEY,
        'Authorization': 'Bearer {}'.format(SUPABASE_KEY),
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        log('  REST PATCH 오류 ({}): {}'.format(path, e))
        return None


def get_or_create_channel():
    """GODofIT 채널 ID 조회/생성"""
    existing = rest_get('influencer_channels', 'select=id,channel_name&channel_handle=eq.%40GODofIT')
    if not existing:
        existing = rest_get('influencer_channels', 'select=id,channel_name&channel_name=ilike.*GODofIT*')
    if existing and len(existing) > 0:
        log('채널 발견: {} ({})'.format(existing[0]['id'], existing[0].get('channel_name', '')))
        return existing[0]['id']
    # 없으면 생성
    import uuid
    channel_data = {
        'id': str(uuid.uuid4()),
        'channel_name': CHANNEL_NAME,
        'channel_handle': CHANNEL_HANDLE,
        'channel_url': CHANNEL_URL,
        'platform': 'youtube',
        'description': '주식/투자 유튜브 채널',
    }
    result = rest_post('influencer_channels', channel_data)
    if result:
        cid = result[0]['id'] if isinstance(result, list) else result.get('id')
        log('채널 생성: {}'.format(cid))
        return cid
    return None


def get_or_create_video(channel_id, video_id, subtitle_text=''):
    """영상 ID 조회/생성"""
    existing = rest_get('influencer_videos', 'select=id&video_id=eq.{}'.format(video_id))
    if existing and len(existing) > 0:
        return existing[0]['id']
    import uuid
    video_data = {
        'id': str(uuid.uuid4()),
        'channel_id': channel_id,
        'video_id': video_id,
        'title': video_id,
        'has_subtitle': True,
        'subtitle_language': 'ko',
        'pipeline_version': 'V11',
    }
    result = rest_post('influencer_videos', video_data)
    if result:
        return result[0]['id'] if isinstance(result, list) else result.get('id')
    return None


def update_video_signal_count(video_uuid, count):
    """영상 signal_count 업데이트"""
    rest_patch('influencer_videos', 'id=eq.{}'.format(video_uuid),
               {'signal_count': count, 'analyzed_at': datetime.utcnow().isoformat()})


def insert_signal(video_uuid, channel_id, signal_data):
    """시그널 DB INSERT"""
    import uuid

    VALID_SIGNALS = {'\ub9e4\uc218', '\uae0d\uc815', '\uc911\ub9bd', '\ubd80\uc815', '\ub9e4\ub3c4'}
    signal_val = signal_data.get('signal', '')
    if signal_val not in VALID_SIGNALS:
        return False

    # 타임스탬프 형식 검증
    ts = signal_data.get('timestamp', '')
    if ts and not re.match(r'^\d{1,2}:\d{2}(:\d{2})?$', str(ts)):
        ts = None

    data = {
        'id': str(uuid.uuid4()),
        'video_id': video_uuid,
        'stock': signal_data.get('stock', ''),
        'ticker': signal_data.get('ticker', ''),
        'market': signal_data.get('market', 'KR'),
        'mention_type': signal_data.get('mention_type', '\uacb0\ub860'),
        'signal': signal_val,
        'confidence': signal_data.get('confidence', 'medium'),
        'timestamp': ts,
        'key_quote': (signal_data.get('key_quote', '') or '')[:500],
        'reasoning': (signal_data.get('reasoning', '') or '')[:500],
        'pipeline_version': 'V11',
        'review_status': 'pending',
    }

    result = rest_post('influencer_signals', data)
    return result is not None


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'done': [], 'errors': [], 'total_signals': 0, 'total_cost': 0.0}


def save_progress(progress):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def main():
    mode_str = ' [TEST MODE - 5개만]' if TEST_MODE else ''
    log('=== GODofIT 채널 시그널 분석 시작{} ==='.format(mode_str))

    # 프롬프트 로드
    prompt_template = load_prompt()
    log('V11 프롬프트 로드 완료 ({} chars)'.format(len(prompt_template)))

    # VTT 파일 목록
    vtt_files = sorted(glob.glob(os.path.join(SUBS_DIR, '*.ko.vtt')))
    log('VTT 파일: {}개'.format(len(vtt_files)))

    if TEST_MODE:
        vtt_files = vtt_files[:5]
        log('TEST MODE: 5개만 처리')

    # 진행상황 로드
    progress = load_progress()
    done_set = set(progress['done'])
    log('기진행: {}개 완료'.format(len(done_set)))

    # 채널 ID 확보
    channel_id = get_or_create_channel()
    if not channel_id:
        log('ERROR: 채널 ID 확보 실패. 종료.')
        return
    log('채널 ID: {}'.format(channel_id))

    total = len(vtt_files)
    processed = 0

    for i, vtt_path in enumerate(vtt_files):
        filename = os.path.basename(vtt_path)
        video_id = get_video_id_from_filename(filename)

        if video_id in done_set:
            log('[{}/{}] {} - 기완료 스킵'.format(i + 1, total, video_id))
            continue

        # 배치 휴식 (20개마다 5분) - TEST MODE에서는 생략
        if not TEST_MODE and processed > 0 and processed % 20 == 0:
            log('  [배치 휴식] 20개 처리 완료. 5분 대기...')
            sleep(300)

        log('[{}/{}] {}'.format(i + 1, total, video_id))

        # 자막 파싱
        subtitle = parse_vtt(vtt_path)
        if len(subtitle) < 100:
            log('  자막 너무 짧음 ({}자). 스킵.'.format(len(subtitle)))
            done_set.add(video_id)
            progress['done'].append(video_id)
            save_progress(progress)
            continue

        # 영상 DB 등록
        video_uuid = get_or_create_video(channel_id, video_id)
        if not video_uuid:
            log('  영상 UUID 획득 실패. 에러 목록에 추가.')
            progress['errors'].append(video_id)
            save_progress(progress)
            continue

        # V11 분석 프롬프트 구성
        analysis_prompt = """{prompt}

=== 분석 대상 ===
채널: GODofIT (https://www.youtube.com/@GODofIT)
영상 ID: {vid}
YouTube URL: https://www.youtube.com/watch?v={vid}

=== 자막 내용 ===
{sub}

위 자막을 V11 프롬프트 규칙에 따라 분석하고 JSON 배열로 시그널을 추출해주세요.
시그널이 없으면 빈 배열 []을 반환하세요.
""".format(prompt=prompt_template, vid=video_id, sub=subtitle)

        # API 호출
        response_text, usage = call_anthropic(analysis_prompt)

        if not response_text:
            log('  API 호출 실패. 에러 목록에 추가.')
            progress['errors'].append(video_id)
            save_progress(progress)
            sleep(5)
            continue

        # 비용 계산 (sonnet-4 가격)
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)
        cost = (input_tokens * 3.0 + output_tokens * 15.0) / 1_000_000
        progress['total_cost'] += cost

        # 시그널 파싱
        signals = parse_signals_from_response(response_text)

        inserted = 0
        for sig in signals:
            if insert_signal(video_uuid, channel_id, sig):
                inserted += 1

        # 영상 signal_count 업데이트
        if inserted > 0:
            update_video_signal_count(video_uuid, inserted)

        progress['total_signals'] += inserted
        done_set.add(video_id)
        progress['done'].append(video_id)
        save_progress(progress)

        log('  -> 시그널 {}개 / {}개 INSERT | 비용 ${:.4f} | 누적 ${:.3f}'.format(
            inserted, len(signals), cost, progress['total_cost']))

        processed += 1
        delay = 2 if TEST_MODE else 3
        sleep(delay)

    log('=== {}완료 ==='.format('TEST ' if TEST_MODE else ''))
    log('총 처리: {}개 / {}개'.format(len(progress['done']), total))
    log('총 시그널: {}개'.format(progress['total_signals']))
    log('총 비용: ${:.3f}'.format(progress['total_cost']))
    log('오류: {}개'.format(len(progress['errors'])))
    if progress['errors']:
        log('오류 목록: {}'.format(progress['errors']))


if __name__ == '__main__':
    main()
