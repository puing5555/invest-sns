#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V11.3 정확도 테스트 스크립트 - Godofit 영상 (최대 20개)
- VTT 타임코드 포함 파싱 (parse_vtt include_timestamps=True)
- V11.3 프롬프트 사용
- 타임스탬프 초과/게스트 발언/ETF 오추출 검증
"""

import os
import sys
import json
import re
import glob
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# Windows 콘솔 UTF-8 강제 설정
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# === 경로 설정 ===
BASE_DIR = r'C:\Users\Mario\work\invest-sns'
SUBS_DIR = os.path.join(BASE_DIR, 'subs')
PROMPT_PATH = os.path.join(BASE_DIR, 'prompts', 'pipeline_v11.3.md')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data', 'tmp')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'v113_godofit_test.json')
ENV_FILE = os.path.join(BASE_DIR, '.env.local')

SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co'
GODOFIT_CHANNEL_ID = '227ad970-4f05-4fea-9a94-90f9649ca714'
CHANNEL_URL = 'https://www.youtube.com/@GODofIT'
CHANNEL_NAME = 'GODofIT'
MODEL = 'claude-sonnet-4-6'

# ETF 키워드 (오추출 감지)
ETF_KEYWORDS = ['TIGER', 'KODEX', 'ETF', 'KBSTAR', 'ARIRANG', 'HANARO', 'TIMEFOLIO', 'ACE', 'KOSEF']


# === 환경변수 로드 ===
def load_env():
    env = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip()
    return env


def load_openclaw_key():
    """openclaw.json에서 ANTHROPIC_API_KEY 읽기 (SOUL.md 규칙: openclaw.json만 신뢰)"""
    candidates = [
        os.path.expanduser(r'~\.openclaw\openclaw.json'),
        os.path.expanduser(r'~\.openclaw-cto\openclaw.json'),
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                key = d.get('env', {}).get('ANTHROPIC_API_KEY', '')
                if key:
                    return key
            except Exception:
                pass
    return ''


def get_api_keys():
    env = load_env()
    # openclaw.json 우선 (SOUL.md 규칙)
    anthropic_key = load_openclaw_key() or os.environ.get('ANTHROPIC_API_KEY', '')
    supabase_key = env.get('SUPABASE_SERVICE_ROLE_KEY', os.environ.get('SUPABASE_SERVICE_ROLE_KEY', ''))
    return anthropic_key, supabase_key


# === parse_vtt (타임코드 포함 버전) ===
def parse_vtt(vtt_path, include_timestamps=True):
    """
    VTT 자막 파일 파싱
    include_timestamps=True: 타임코드 포함 (시그널 분석용) - 기본값
    include_timestamps=False: 텍스트만 (레거시)
    """
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if include_timestamps:
        lines_out = []
        current_ts = None
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('WEBVTT') or line.startswith('NOTE') \
                    or line.startswith('Kind:') or line.startswith('Language:'):
                continue
            ts_match = re.match(r'(\d{2}:\d{2}:\d{2})\.\d+ -->', line)
            if ts_match:
                current_ts = ts_match.group(1)
                continue
            if re.match(r'^\d+$', line):
                continue
            clean = re.sub(r'<[^>]+>', '', line).strip()
            if clean:
                if current_ts:
                    lines_out.append(f'[{current_ts}] {clean}')
                    current_ts = None
                else:
                    lines_out.append(clean)
        deduped = []
        prev = None
        for l in lines_out:
            if l != prev:
                deduped.append(l)
            prev = l
        return '\n'.join(deduped[:4000])
    else:
        lines = []
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('WEBVTT') or line.startswith('NOTE') \
                    or line.startswith('Kind:') or line.startswith('Language:'):
                continue
            if '-->' in line:
                continue
            if re.match(r'^\d+$', line):
                continue
            line = re.sub(r'<[^>]+>', '', line)
            if line:
                lines.append(line)
        deduped = []
        prev = None
        for l in lines:
            if l != prev:
                deduped.append(l)
            prev = l
        return ' '.join(deduped[:3000])


# === video_id 추출 ===
def get_video_id_from_filename(filename):
    """파일명에서 YouTube video_id 추출
    wsaj_XXXXXXXXXXX_제목.ko.vtt -> XXXXXXXXXXX (wsaj_ 이후 11자)
    """
    base = os.path.basename(filename).replace('.ko.vtt', '')
    if base.startswith('wsaj_') and len(base) > 16:
        return base[5:16]
    return base


# === Supabase REST GET ===
def supabase_get(path, params, supabase_key):
    url = f'{SUPABASE_URL}/rest/v1/{path}?{params}'
    req = urllib.request.Request(url, headers={
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}'
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f'  [WARN] Supabase GET 오류 ({path}): {e}')
        return []


# === Anthropic API 호출 ===
def call_anthropic(prompt_text, anthropic_key):
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': anthropic_key,
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
                print(f'  Rate limit (429). 60초 대기...')
                time.sleep(60)
                continue
            elif e.code == 529:
                print(f'  과부하 (529). 30초 대기...')
                time.sleep(30)
                continue
            else:
                print(f'  HTTP 오류 {e.code}: {err_body[:300]}')
                return None, {}
        except Exception as ex:
            print(f'  API 오류: {ex}')
            time.sleep(5)
    return None, {}


# === 시그널 JSON 파싱 ===
def parse_signals_from_response(text):
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


# === 타임스탬프 문자열 → 초 변환 ===
def ts_to_seconds(ts_str):
    """HH:MM:SS 또는 MM:SS 형태 → 초"""
    if not ts_str:
        return None
    try:
        parts = str(ts_str).split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        else:
            return int(parts[0])
    except Exception:
        return None


# === ETF 오추출 확인 ===
def is_etf(stock_name):
    if not stock_name:
        return False
    for kw in ETF_KEYWORDS:
        if kw.upper() in stock_name.upper():
            return True
    return False


# === 초 → MM:SS 형식 ===
def seconds_to_mmss(secs):
    if secs is None:
        return '?'
    m = secs // 60
    s = secs % 60
    return f'{m:02d}:{s:02d}'


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    anthropic_key, supabase_key = get_api_keys()
    if not anthropic_key:
        print('ERROR: ANTHROPIC_API_KEY 환경변수 없음')
        sys.exit(1)
    if not supabase_key:
        print('WARN: SUPABASE_SERVICE_ROLE_KEY 없음 - 영상 정보 없이 진행')

    # V11.3 프롬프트 로드
    with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    print(f'V11.3 프롬프트 로드 완료 ({len(prompt_template)}자)')

    # VTT 파일 목록 (ko-orig 제외, ko.vtt만)
    all_vtt = sorted(glob.glob(os.path.join(SUBS_DIR, 'wsaj_*.ko.vtt')))
    all_vtt = [f for f in all_vtt if not f.endswith('.ko-orig.vtt')]
    vtt_files = all_vtt[:20]  # 최대 20개
    print(f'VTT 파일: {len(vtt_files)}개 선택')

    # Supabase에서 Godofit 영상 정보 조회
    video_info_map = {}
    if supabase_key:
        print('Supabase에서 영상 정보 조회 중...')
        videos = supabase_get(
            'influencer_videos',
            f'select=id,video_id,title,duration_seconds&channel_id=eq.{GODOFIT_CHANNEL_ID}',
            supabase_key
        )
        for v in videos:
            video_info_map[v.get('video_id', '')] = v
        print(f'  영상 정보: {len(video_info_map)}개')

    # 결과 수집
    results = []
    total_signals = 0
    total_ts_exceed = 0
    total_guest = 0
    total_etf = 0

    print(f'\n=== V11.3 Godofit 테스트 결과 ===\n')

    for i, vtt_path in enumerate(vtt_files, 1):
        filename = os.path.basename(vtt_path)
        video_id = get_video_id_from_filename(filename)

        # 영상 정보
        vinfo = video_info_map.get(video_id, {})
        title = vinfo.get('title', filename)
        duration_seconds = vinfo.get('duration_seconds')

        # 제목 truncate
        title_short = title[:40] + '...' if len(title) > 40 else title
        duration_str = seconds_to_mmss(duration_seconds) if duration_seconds else '??:??'

        print(f'[{i}/{len(vtt_files)}] {video_id} | {duration_str} | {title_short}')

        result_item = {
            'video_id': video_id,
            'video_url': f'https://www.youtube.com/watch?v={video_id}',
            'title': title,
            'duration_seconds': duration_seconds,
            'signals': [],
            'ts_exceed_count': 0,
            'guest_count': 0,
            'etf_count': 0,
            'error': None
        }

        try:
            # VTT 파싱 (타임코드 포함)
            subtitle_text = parse_vtt(vtt_path, include_timestamps=True)

            # VIDEO_DURATION_INFO 치환
            if duration_seconds:
                m_val = duration_seconds // 60
                s_val = duration_seconds % 60
                duration_info = f'이 영상은 {m_val}분 {s_val}초({duration_seconds}초)입니다. 타임스탬프는 이 시간 이내여야 합니다.'
            else:
                duration_info = '영상 길이 정보 없음.'

            prompt = prompt_template.replace('{VIDEO_DURATION_INFO}', duration_info)

            # 채널 URL과 자막 추가
            full_prompt = f"""{prompt}

---

## 분석 대상

채널: {CHANNEL_URL}
영상 URL: https://www.youtube.com/watch?v={video_id}
제목: {title}

## 자막 (타임코드 포함)

{subtitle_text}
"""

            # API 호출
            response_text, usage = call_anthropic(full_prompt, anthropic_key)

            if not response_text:
                print(f'  ⚠ API 응답 없음')
                result_item['error'] = 'API 응답 없음'
                results.append(result_item)
                continue

            # 시그널 파싱
            signals = parse_signals_from_response(response_text)

            # 분석
            ts_exceed = 0
            guest_signals = 0
            etf_signals = 0

            print(f'  시그널: {len(signals)}개')

            for sig in signals:
                stock = sig.get('stock', sig.get('종목', ''))
                signal_type = sig.get('signal', sig.get('신호', sig.get('mention_type', '')))
                timestamp = sig.get('timestamp', sig.get('타임스탬프', ''))
                key_quote = sig.get('key_quote', sig.get('핵심발언', ''))
                speaker = sig.get('speaker_name', sig.get('발표자', CHANNEL_NAME))

                # 타임스탬프 초과 확인
                if duration_seconds and timestamp:
                    ts_secs = ts_to_seconds(timestamp)
                    if ts_secs is not None and ts_secs > duration_seconds:
                        ts_exceed += 1

                # 게스트 발언 확인
                if speaker and speaker != CHANNEL_NAME and speaker.upper() != 'GODOFIT':
                    guest_signals += 1

                # ETF 오추출 확인
                if is_etf(stock):
                    etf_signals += 1

                # 출력
                key_quote_short = str(key_quote)[:50] + '...' if len(str(key_quote)) > 50 else str(key_quote)
                print(f'  - {stock} | {signal_type} | {timestamp} | "{key_quote_short}" | {speaker}')

                result_item['signals'].append({
                    'stock': stock,
                    'signal': signal_type,
                    'timestamp': timestamp,
                    'key_quote': key_quote,
                    'speaker_name': speaker
                })

            result_item['ts_exceed_count'] = ts_exceed
            result_item['guest_count'] = guest_signals
            result_item['etf_count'] = etf_signals

            total_signals += len(signals)
            total_ts_exceed += ts_exceed
            total_guest += guest_signals
            total_etf += etf_signals

            exceed_icon = '⚠' if ts_exceed > 0 else '✅'
            guest_icon = '⚠' if guest_signals > 0 else '✅'
            print(f'  {exceed_icon} 타임스탬프 초과: {ts_exceed}건')
            print(f'  {guest_icon} 게스트 발언: {guest_signals}건')
            if etf_signals > 0:
                print(f'  ⚠ ETF 오추출: {etf_signals}건')

        except Exception as ex:
            import traceback
            err_msg = str(ex)
            print(f'  ❌ 오류: {err_msg}')
            traceback.print_exc()
            result_item['error'] = err_msg

        results.append(result_item)
        print()

        # API 호출 간격 (rate limit 방지)
        if i < len(vtt_files):
            time.sleep(2)

    # 전체 요약
    print('\n=== 전체 요약 ===')
    print(f'총 영상: {len(vtt_files)}개')
    print(f'총 시그널: {total_signals}개')
    print(f'타임스탬프 초과: {total_ts_exceed}건')
    print(f'게스트 발언: {total_guest}건')
    print(f'ETF 오추출: {total_etf}건')

    # JSON 저장
    output_data = {
        'test_date': datetime.now().isoformat(),
        'model': MODEL,
        'prompt_version': 'v11.3',
        'channel': CHANNEL_URL,
        'total_videos': len(vtt_files),
        'total_signals': total_signals,
        'total_ts_exceed': total_ts_exceed,
        'total_guest': total_guest,
        'total_etf': total_etf,
        'results': results
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f'\n결과 저장: {OUTPUT_FILE}')
    return output_data


if __name__ == '__main__':
    main()
