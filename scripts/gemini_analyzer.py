# gemini_analyzer.py - Gemini 2.0 Flash 유튜브 직접 분석 모듈
"""
yt-dlp 자막 추출 없이 Gemini 2.0 Flash API로 YouTube URL 직접 분석.
V11.5 프롬프트 기준 시그널 추출.
"""

import os
import json
import time
import re
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path

# .env.local 로드
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'), override=True)

from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL = 'gemini-2.5-flash'
GEMINI_API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent'

PROMPT_PATH = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'pipeline_v12.md')

VALID_SIGNALS = {'매수', '긍정', '중립', '부정', '매도'}
SLASH_SIGNAL_MAP = {
    '매수/긍정': '매수',
    '긍정/매수': '매수',
    '부정/매도': '매도',
    '매도/부정': '매도',
    '긍정/중립': '긍정',
    '중립/긍정': '긍정',
    '부정/중립': '부정',
    '중립/부정': '부정',
    '경계': '부정',  # 구 경계 → 부정
}


def load_prompt() -> str:
    try:
        with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"V11.5 프롬프트 파일 없음: {PROMPT_PATH}")


def build_gemini_prompt(video_data: Dict[str, Any]) -> str:
    """Gemini용 분석 프롬프트 생성 (자막 없이 영상 직접 분석)"""
    prompt_template = load_prompt()

    # VIDEO_DURATION_INFO 플레이스홀더 처리
    dur_secs = video_data.get('duration_seconds') or video_data.get('duration')
    if dur_secs:
        try:
            dur_secs = int(dur_secs)
            dur_str = f"{dur_secs//60}분 {dur_secs%60:02d}초 ({dur_secs}초)"
            duration_info = f"이 영상은 {dur_str}입니다. 타임스탬프는 이 시간을 절대로 초과할 수 없습니다."
        except:
            duration_info = "영상 길이 정보 없음"
    else:
        duration_info = "영상 길이 정보 없음"

    prompt = prompt_template.replace('{VIDEO_DURATION_INFO}', duration_info)

    # CHANNEL_URL 플레이스홀더 처리
    channel_url = video_data.get('channel_url', '')
    prompt = prompt.replace('{CHANNEL_URL}', channel_url)

    # 영상 메타데이터 추가
    video_context = f"""

=== 분석 대상 영상 ===
제목: {video_data.get('title', 'N/A')}
YouTube URL: {video_data.get('url', '')}
길이: {video_data.get('duration', 'N/A')}
업로드: {video_data.get('upload_date', 'N/A')}

=== 분석 지시사항 ===
위 YouTube 영상을 직접 시청하고 V11.5 프롬프트 규칙에 따라 시그널을 추출해주세요.
- 자막 대신 영상 오디오/비주얼을 직접 분석합니다
- 타임스탬프는 영상에서 실제 발언이 나온 시점을 기준으로 추출하세요
- 출력: 반드시 JSON만 (```json 블록 또는 {{...}} 형식)
"""
    return prompt + video_context


def normalize_signal(raw_signal: str) -> Optional[str]:
    """시그널 정규화: 슬래시 복수표기 제거, 경계→부정 등"""
    if not raw_signal:
        return None
    s = raw_signal.strip()
    if s in VALID_SIGNALS:
        return s
    if s in SLASH_SIGNAL_MAP:
        return SLASH_SIGNAL_MAP[s]
    # 영문 → 한글 매핑
    en_map = {
        'BUY': '매수', 'STRONG_BUY': '매수',
        'POSITIVE': '긍정',
        'NEUTRAL': '중립',
        'NEGATIVE': '부정',
        'SELL': '매도', 'STRONG_SELL': '매도',
    }
    if s.upper() in en_map:
        return en_map[s.upper()]
    return None


def repair_json(text: str) -> str:
    """깨진 JSON 보정 — 일반적인 Gemini 응답 오류 패턴 수정"""
    # 1) 마크다운 코드 블록 제거
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()

    # 2) 후행 쉼표 제거 (,} / ,])
    text = re.sub(r',\s*([}\]])', r'\1', text)

    # 3) 줄바꿈 포함 문자열 내 제어문자 이스케이프
    #    (문자열 밖의 실제 줄바꿈은 JSON에서 허용되지만,
    #     따옴표 안에 raw 줄바꿈이 있으면 파싱 실패)
    def escape_inner_newlines(m: re.Match) -> str:
        inner = m.group(1)
        inner = inner.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        return f'"{inner}"'
    # 문자열 리터럴 내부 제어문자만 이스케이프
    text = re.sub(r'"((?:[^"\\]|\\.)*)"', escape_inner_newlines, text, flags=re.DOTALL)

    # 4) 단일 따옴표 → 이중 따옴표 (단순 케이스)
    #    이미 이중 따옴표로 된 부분은 건드리지 않음
    # (복잡한 케이스는 처리 안 함 — 이미 위에서 처리됨)

    # 5) null 대신 None, true/false 대신 True/False 패턴은 JSON 표준이므로 그대로 유지

    # 6) 불완전한 마지막 객체 잘라내기
    #    배열이 중간에 잘린 경우: "[{...}, {..." → "[{...}]"
    #    중괄호/대괄호 균형 맞추기
    open_b = text.count('{') - text.count('}')
    open_a = text.count('[') - text.count(']')
    if open_b > 0:
        text += '}' * open_b
    if open_a > 0:
        text += ']' * open_a

    return text


def extract_signals_fallback(text: str, video_id: str) -> List[Dict]:
    """JSON 전체 파싱이 불가능할 때 개별 시그널 객체를 직접 추출"""
    signals = []
    # 각 시그널 객체 패턴으로 개별 추출 시도
    pattern = re.compile(
        r'\{[^{}]*"stock"\s*:\s*"([^"]+)"[^{}]*"signal_type"\s*:\s*"([^"]+)"[^{}]*\}',
        re.DOTALL
    )
    for m in pattern.finditer(text):
        try:
            obj_str = m.group(0)
            # 후행 쉼표 정리
            obj_str = re.sub(r',\s*([}\]])', r'\1', obj_str)
            obj = json.loads(obj_str)
            signals.append(obj)
        except Exception:
            # 파싱 실패 시 최소 필드만 구성
            try:
                raw = re.search(
                    r'"stock"\s*:\s*"([^"]+)".*?"signal_type"\s*:\s*"([^"]+)".*?"confidence"\s*:\s*(\d+)',
                    m.group(0), re.DOTALL
                )
                if raw:
                    signals.append({
                        'stock': raw.group(1),
                        'signal_type': raw.group(2),
                        'confidence': int(raw.group(3)),
                        'key_quote': '',
                        'reasoning': '',
                    })
            except Exception:
                pass
    if signals:
        print(f"  [REPAIR-FALLBACK] {len(signals)}개 시그널 개별 추출 성공 (video={video_id})")
    return signals


def parse_gemini_response(response_text: str, video_id: str) -> List[Dict[str, Any]]:
    """Gemini 응답 파싱 → 시그널 리스트
    파싱 실패 시 JSON 보정 → 재시도 → 개별 추출 순으로 진행. 스킵하지 않음.
    """
    raw_signals = None

    def try_parse(text: str) -> Optional[List]:
        """JSON 파싱 시도 → signals 리스트 반환 or None"""
        try:
            data = json.loads(text.strip())
            sigs = data.get('signals', [])
            return sigs if isinstance(sigs, list) else None
        except json.JSONDecodeError:
            return None

    # ── 1순위: 직접 파싱 ──────────────────────────────────────
    raw_signals = try_parse(response_text)

    # ── 2순위: ```json 블록 추출 후 파싱 ─────────────────────
    if raw_signals is None:
        m = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if m:
            raw_signals = try_parse(m.group(1))

    # ── 3순위: {…} 블록 추출 후 파싱 ────────────────────────
    if raw_signals is None:
        m = re.search(r'\{.*\}', response_text, re.DOTALL)
        if m:
            raw_signals = try_parse(m.group(0))

    # ── 4순위: JSON 보정(repair) 후 재파싱 ───────────────────
    if raw_signals is None:
        print(f"  [REPAIR] JSON 파싱 실패 → 보정 후 재시도 (video={video_id})")
        repaired = repair_json(response_text)
        raw_signals = try_parse(repaired)
        if raw_signals is not None:
            print(f"  [REPAIR] 보정 성공 ({len(raw_signals)}개 시그널)")
        else:
            # 보정된 텍스트에서 블록 재추출
            m = re.search(r'\{.*\}', repaired, re.DOTALL)
            if m:
                raw_signals = try_parse(m.group(0))
                if raw_signals is not None:
                    print(f"  [REPAIR] 블록 추출 후 성공 ({len(raw_signals)}개 시그널)")

    # ── 5순위: 개별 시그널 객체 직접 추출 ────────────────────
    if raw_signals is None:
        print(f"  [REPAIR] 보정 실패 → 개별 객체 추출 시도 (video={video_id})")
        raw_signals = extract_signals_fallback(response_text, video_id)

    if raw_signals is None or len(raw_signals) == 0:
        if raw_signals is None:
            print(f"  [WARN] 모든 파싱 전략 실패 (video={video_id})")
        return []

    try:
        signals = []
        for s in raw_signals:
            # signal_type 정규화 (슬래시 복수표기 금지)
            raw_type = s.get('signal_type', '')
            normalized = normalize_signal(raw_type)
            if not normalized:
                print(f"  [SKIP] 유효하지 않은 signal_type: '{raw_type}'")
                continue

            # confidence 검증
            conf = s.get('confidence')
            try:
                conf = int(conf)
            except (TypeError, ValueError):
                conf = 5
            if conf < 5:
                print(f"  [SKIP] confidence 낮음 ({conf}): {s.get('stock', '')}")
                continue

            # stock 필수
            if not s.get('stock'):
                continue

            signals.append({
                'stock': s.get('stock', ''),
                'ticker': s.get('ticker'),
                'signal_type': normalized,
                'key_quote': s.get('key_quote', ''),
                'reasoning': s.get('reasoning', ''),
                'timestamp': s.get('timestamp'),
                'confidence': conf,
                'speaker_name': s.get('speaker_name'),
            })

        return signals

    except Exception as e:
        print(f"  [ERROR] 시그널 처리 오류 (video={video_id}): {e}")
        return []


def analyze_video_with_gemini(
    video_data: Dict[str, Any],
    retry: int = 3,
    retry_delay: int = 10
) -> List[Dict[str, Any]]:
    """
    Gemini SDK로 YouTube 영상 직접 분석.
    media_resolution=LOW + video/* mime_type으로 3~4배 속도 개선.

    Args:
        video_data: {video_id, title, url, duration, duration_seconds, upload_date, channel_url}
        retry: 재시도 횟수
        retry_delay: 재시도 대기 초

    Returns:
        시그널 리스트
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY 환경변수 없음 — .env.local에 추가하세요")

    video_url = video_data.get('url', '')
    video_id = video_data.get('video_id', '')
    title = video_data.get('title', '')

    print(f"  [Gemini] 분석 시작: {video_id} | {title[:40]}")

    prompt_text = build_gemini_prompt(video_data)

    # 영상 구간 설정: 최대 10분 (600초)
    dur_secs = video_data.get('duration_seconds') or video_data.get('duration')
    try:
        dur_secs = int(dur_secs)
    except (TypeError, ValueError):
        dur_secs = 600
    end_sec = min(dur_secs, 600)

    # response_schema
    response_schema = types.Schema(
        type=types.Type.OBJECT,
        required=["signals"],
        properties={
            "signals": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.OBJECT,
                    required=["stock", "signal_type", "key_quote", "reasoning", "confidence"],
                    properties={
                        "stock":        types.Schema(type=types.Type.STRING),
                        "ticker":       types.Schema(type=types.Type.STRING),
                        "signal_type":  types.Schema(type=types.Type.STRING),
                        "key_quote":    types.Schema(type=types.Type.STRING),
                        "reasoning":    types.Schema(type=types.Type.STRING),
                        "timestamp":    types.Schema(type=types.Type.STRING),
                        "confidence":   types.Schema(type=types.Type.INTEGER),
                        "speaker_name": types.Schema(type=types.Type.STRING),
                    }
                )
            )
        }
    )

    client = genai.Client(api_key=GEMINI_API_KEY)

    contents = [
        types.Part(
            file_data=types.FileData(
                mime_type="video/*",       # ← video/mp4 고정 대신 와일드카드
                file_uri=video_url,
            ),
            video_metadata=types.VideoMetadata(
                start_offset=f"0s",
                end_offset=f"{end_sec}s",  # 최대 10분
            ),
        ),
        types.Part(text=prompt_text),
    ]

    config = types.GenerateContentConfig(
        temperature=0.1,
        max_output_tokens=8192,
        response_mime_type="application/json",
        response_schema=response_schema,
        media_resolution=types.MediaResolution.MEDIA_RESOLUTION_LOW,  # ← 핵심: 3x 빠름
    )

    for attempt in range(1, retry + 1):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=config,
            )

            finish_reason = str(response.candidates[0].finish_reason) if response.candidates else ''
            if 'SAFETY' in finish_reason or 'RECITATION' in finish_reason:
                print(f"  [SKIP] Gemini 거부 (reason={finish_reason}): {video_id}")
                return []

            response_text = response.text or ''
            signals = parse_gemini_response(response_text, video_id)
            print(f"  [OK] {len(signals)}개 시그널 추출")
            return signals

        except Exception as e:
            err_str = str(e)
            if '429' in err_str or 'RESOURCE_EXHAUSTED' in err_str:
                wait = max(30, retry_delay * attempt * 2)
                print(f"  [RATE LIMIT] 429 → {wait}초 대기 후 재시도 ({attempt}/{retry})")
                time.sleep(wait)
                continue
            if 'deadline' in err_str.lower() or 'timeout' in err_str.lower():
                print(f"  [TIMEOUT] Gemini 타임아웃 (attempt={attempt}/{retry})")
            else:
                print(f"  [ERROR] Gemini 호출 실패 (attempt={attempt}/{retry}): {e}")
            if attempt < retry:
                time.sleep(retry_delay)

    return []
