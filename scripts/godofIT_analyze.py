#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GODofIT 梨꾨꼸 ?쒓렇??遺꾩꽍 ?ㅽ겕由쏀듃
- VTT ?먮쭑 ?뚯씪 ?쎌뼱??V11 ?꾨＼?꾪듃濡?遺꾩꽍
- REST API濡?Supabase DB INSERT
- 吏꾪뻾?곹솴 ???(以묐떒??蹂듦뎄 媛??

?ㅼ젣 DB ?ㅽ궎留?湲곗?:
  influencer_channels: id, channel_name, channel_handle, channel_url, platform, subscriber_count, description
  influencer_videos: id, channel_id, video_id, title, published_at, duration_seconds, has_subtitle, subtitle_language, analyzed_at, pipeline_version, signal_count, video_summary, subtitle_text
  influencer_signals: id, video_id, speaker_id, stock, ticker, market, mention_type, signal, confidence, timestamp, key_quote, reasoning, review_status, pipeline_version
"""

import os, sys, json, re, time, glob
from datetime import datetime

# --- 寃쎈줈 ?ㅼ젙 ---
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
SUBS_DIR = r'C:\Users\Mario\work\invest-sns\subs'
PROMPT_PATH = r'C:\Users\Mario\work\prompts\pipeline_v11.md'
PROGRESS_FILE = r'C:\Users\Mario\work\invest-sns\pipeline\data\godofIT_progress.json'
LOG_FILE = r'C:\Users\Mario\work\invest-sns\pipeline\data\godofIT_log.txt'

SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY', 'YOUR_ANTHROPIC_API_KEY_HERE')
MODEL = 'claude-sonnet-4-6'

CHANNEL_URL = 'https://www.youtube.com/@GODofIT'
CHANNEL_NAME = 'GODofIT'
CHANNEL_HANDLE = '@GODofIT'

# TEST_MODE: True?대㈃ 泥섏쓬 5媛쒕쭔 ?ㅽ뻾
TEST_MODE = '--test' in sys.argv or os.environ.get('TEST_MODE') == '1'

# ?곗씠???붾젆?좊━ ?앹꽦
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
    """VTT ?먮쭑 ?뚯씪?먯꽌 ?띿뒪??異붿텧"""
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
    # 以묐났 ?쒓굅 (?곗냽 媛숈? 以?
    deduped = []
    prev = None
    for l in lines:
        if l != prev:
            deduped.append(l)
        prev = l
    return ' '.join(deduped[:3000])


def get_video_id_from_filename(filename):
    """?뚯씪紐낆뿉??YouTube video_id 異붿텧
    ?⑦꽩1: AbcdXyz.ko.vtt -> AbcdXyz (11??ID)
    ?⑦꽩2: wsaj_AbcdXyz_?쒕ぉ.ko.vtt -> AbcdXyz (wsaj_ ?댄썑 11??
    """
    base = filename.replace('.ko.vtt', '')
    if base.startswith('wsaj_') and len(base) > 16:
        # wsaj_ ?ㅼ쓬 11?먭? YouTube ID
        return base[5:16]
    return base


def call_anthropic(prompt_text):
    """Claude API ?몄텧"""
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
                log('  Rate limit (429). 60珥??湲?..')
                sleep(60)
                continue
            elif e.code == 529:
                log('  怨쇰???(529). 30珥??湲?..')
                sleep(30)
                continue
            else:
                log('  HTTP ?ㅻ쪟 {}: {}'.format(e.code, err_body[:300]))
                return None, {}
        except Exception as ex:
            log('  API ?ㅻ쪟: {}'.format(ex))
            sleep(5)
    return None, {}


def parse_signals_from_response(text):
    """?묐떟?먯꽌 JSON ?쒓렇??異붿텧"""
    # ```json [...] ``` ?⑦꽩
    m = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # 吏곸젒 [] 諛곗뿴 李얘린
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
        log('  REST GET ?ㅻ쪟 ({}): {}'.format(path, e))
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
        log('  REST POST ?ㅻ쪟 ({}): {} {}'.format(path, e.code, e.read().decode()[:300]))
        return None
    except Exception as e:
        log('  REST POST ?ㅻ쪟 ({}): {}'.format(path, e))
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
        log('  REST PATCH ?ㅻ쪟 ({}): {}'.format(path, e))
        return None


def get_or_create_channel():
    """GODofIT 梨꾨꼸 ID 議고쉶/?앹꽦"""
    existing = rest_get('influencer_channels', 'select=id,channel_name&channel_handle=eq.%40GODofIT')
    if not existing:
        existing = rest_get('influencer_channels', 'select=id,channel_name&channel_name=ilike.*GODofIT*')
    if existing and len(existing) > 0:
        log('梨꾨꼸 諛쒓껄: {} ({})'.format(existing[0]['id'], existing[0].get('channel_name', '')))
        return existing[0]['id']
    # ?놁쑝硫??앹꽦
    import uuid
    channel_data = {
        'id': str(uuid.uuid4()),
        'channel_name': CHANNEL_NAME,
        'channel_handle': CHANNEL_HANDLE,
        'channel_url': CHANNEL_URL,
        'platform': 'youtube',
        'description': '二쇱떇/?ъ옄 ?좏뒠釉?梨꾨꼸',
    }
    result = rest_post('influencer_channels', channel_data)
    if result:
        cid = result[0]['id'] if isinstance(result, list) else result.get('id')
        log('梨꾨꼸 ?앹꽦: {}'.format(cid))
        return cid
    return None


def get_or_create_video(channel_id, video_id, subtitle_text=''):
    """?곸긽 ID 議고쉶/?앹꽦"""
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
    """?곸긽 signal_count ?낅뜲?댄듃"""
    rest_patch('influencer_videos', 'id=eq.{}'.format(video_uuid),
               {'signal_count': count, 'analyzed_at': datetime.utcnow().isoformat()})


def insert_signal(video_uuid, channel_id, signal_data):
    """?쒓렇??DB INSERT"""
    import uuid

    VALID_SIGNALS = {'\ub9e4\uc218', '\uae0d\uc815', '\uc911\ub9bd', '\ubd80\uc815', '\ub9e4\ub3c4'}
    signal_val = signal_data.get('signal', '')
    if signal_val not in VALID_SIGNALS:
        return False

    # ??꾩뒪?ы봽 ?뺤떇 寃利?
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
    mode_str = ' [TEST MODE - 5媛쒕쭔]' if TEST_MODE else ''
    log('=== GODofIT 梨꾨꼸 ?쒓렇??遺꾩꽍 ?쒖옉{} ==='.format(mode_str))

    # ?꾨＼?꾪듃 濡쒕뱶
    prompt_template = load_prompt()
    log('V11 ?꾨＼?꾪듃 濡쒕뱶 ?꾨즺 ({} chars)'.format(len(prompt_template)))

    # VTT ?뚯씪 紐⑸줉
    vtt_files = sorted(glob.glob(os.path.join(SUBS_DIR, '*.ko.vtt')))
    log('VTT ?뚯씪: {}媛?.format(len(vtt_files)))

    if TEST_MODE:
        vtt_files = vtt_files[:5]
        log('TEST MODE: 5媛쒕쭔 泥섎━')

    # 吏꾪뻾?곹솴 濡쒕뱶
    progress = load_progress()
    done_set = set(progress['done'])
    log('湲곗쭊?? {}媛??꾨즺'.format(len(done_set)))

    # 梨꾨꼸 ID ?뺣낫
    channel_id = get_or_create_channel()
    if not channel_id:
        log('ERROR: 梨꾨꼸 ID ?뺣낫 ?ㅽ뙣. 醫낅즺.')
        return
    log('梨꾨꼸 ID: {}'.format(channel_id))

    total = len(vtt_files)
    processed = 0

    for i, vtt_path in enumerate(vtt_files):
        filename = os.path.basename(vtt_path)
        video_id = get_video_id_from_filename(filename)

        if video_id in done_set:
            log('[{}/{}] {} - 湲곗셿猷??ㅽ궢'.format(i + 1, total, video_id))
            continue

        # 諛곗튂 ?댁떇 (20媛쒕쭏??5遺? - TEST MODE?먯꽌???앸왂
        if not TEST_MODE and processed > 0 and processed % 20 == 0:
            log('  [諛곗튂 ?댁떇] 20媛?泥섎━ ?꾨즺. 5遺??湲?..')
            sleep(300)

        log('[{}/{}] {}'.format(i + 1, total, video_id))

        # ?먮쭑 ?뚯떛
        subtitle = parse_vtt(vtt_path)
        if len(subtitle) < 100:
            log('  ?먮쭑 ?덈Т 吏㏃쓬 ({}??. ?ㅽ궢.'.format(len(subtitle)))
            done_set.add(video_id)
            progress['done'].append(video_id)
            save_progress(progress)
            continue

        # ?곸긽 DB ?깅줉
        video_uuid = get_or_create_video(channel_id, video_id)
        if not video_uuid:
            log('  ?곸긽 UUID ?띾뱷 ?ㅽ뙣. ?먮윭 紐⑸줉??異붽?.')
            progress['errors'].append(video_id)
            save_progress(progress)
            continue

        # V11 遺꾩꽍 ?꾨＼?꾪듃 援ъ꽦
        analysis_prompt = """{prompt}

=== 遺꾩꽍 ???===
梨꾨꼸: GODofIT (https://www.youtube.com/@GODofIT)
?곸긽 ID: {vid}
YouTube URL: https://www.youtube.com/watch?v={vid}

=== ?먮쭑 ?댁슜 ===
{sub}

???먮쭑??V11 ?꾨＼?꾪듃 洹쒖튃???곕씪 遺꾩꽍?섍퀬 JSON 諛곗뿴濡??쒓렇?먯쓣 異붿텧?댁＜?몄슂.
?쒓렇?먯씠 ?놁쑝硫?鍮?諛곗뿴 []??諛섑솚?섏꽭??
""".format(prompt=prompt_template, vid=video_id, sub=subtitle)

        # API ?몄텧
        response_text, usage = call_anthropic(analysis_prompt)

        if not response_text:
            log('  API ?몄텧 ?ㅽ뙣. ?먮윭 紐⑸줉??異붽?.')
            progress['errors'].append(video_id)
            save_progress(progress)
            sleep(5)
            continue

        # 鍮꾩슜 怨꾩궛 (sonnet-4 媛寃?
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)
        cost = (input_tokens * 3.0 + output_tokens * 15.0) / 1_000_000
        progress['total_cost'] += cost

        # ?쒓렇???뚯떛
        signals = parse_signals_from_response(response_text)

        inserted = 0
        for sig in signals:
            if insert_signal(video_uuid, channel_id, sig):
                inserted += 1

        # ?곸긽 signal_count ?낅뜲?댄듃
        if inserted > 0:
            update_video_signal_count(video_uuid, inserted)

        progress['total_signals'] += inserted
        done_set.add(video_id)
        progress['done'].append(video_id)
        save_progress(progress)

        log('  -> ?쒓렇??{}媛?/ {}媛?INSERT | 鍮꾩슜 ${:.4f} | ?꾩쟻 ${:.3f}'.format(
            inserted, len(signals), cost, progress['total_cost']))

        processed += 1
        delay = 2 if TEST_MODE else 3
        sleep(delay)

    log('=== {}?꾨즺 ==='.format('TEST ' if TEST_MODE else ''))
    log('珥?泥섎━: {}媛?/ {}媛?.format(len(progress['done']), total))
    log('珥??쒓렇?? {}媛?.format(progress['total_signals']))
    log('珥?鍮꾩슜: ${:.3f}'.format(progress['total_cost']))
    log('?ㅻ쪟: {}媛?.format(len(progress['errors'])))
    if progress['errors']:
        log('?ㅻ쪟 紐⑸줉: {}'.format(progress['errors']))


if __name__ == '__main__':
    main()


