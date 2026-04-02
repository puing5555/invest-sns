# -*- coding: utf-8 -*-
"""강환국 파트A 검증 — 5개 영상 자막 + AI 응답 raw 출력"""
import sys, os, json, re, subprocess, glob
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from pipeline_config import PipelineConfig

env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
ANTHROPIC_KEY = None
if os.path.exists(env_path):
    for line in open(env_path):
        if line.startswith('ANTHROPIC_API_KEY='):
            ANTHROPIC_KEY = line.split('=', 1)[1].strip()

import anthropic
client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

PROMPT_PATH = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'pipeline_v14.0.md')
with open(PROMPT_PATH, encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

TEST_VIDEOS = [
    ('RLtvychZwVk', '1618. AI 시대 돈은 어디로 (21종목)'),
    ('N7vTvZkmO7I', '1469. AI가 분석한 AI 주식의 미래 (15종목)'),
    ('6AKYd_PUpp8', '1388. 빅테크 버블 임박 경고 (15종목)'),
    ('JVPFKqsZOJw', '1371. 2025 알트코인 황금기 (13종목)'),
    ('8pIjWeurQ8M', '327. 대폭락 후 코스닥 싹쓸이 전략'),
]


def get_subtitle(video_id):
    tmp = f'/tmp/kangv_{video_id}'
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


for vid_id, label in TEST_VIDEOS:
    print(f'\n{"="*80}')
    print(f'영상: {label}')
    print(f'ID: {vid_id}')
    print(f'URL: https://www.youtube.com/watch?v={vid_id}')
    print(f'{"="*80}')

    # 1. 자막
    subtitle = get_subtitle(vid_id)
    if not subtitle:
        print('[자막 추출 실패]')
        continue

    print(f'\n--- 자막 처음 500자 ---')
    print(subtitle[:500])
    print(f'\n--- 자막 총 길이: {len(subtitle)}자 ---')

    # 2. AI 분석
    prompt = SYSTEM_PROMPT.replace('{VIDEO_DURATION_INFO}', '')
    prompt += "\n\n채널 운영자: 강환국"

    # Get title from yt-dlp
    try:
        r = subprocess.run(
            [sys.executable, '-m', 'yt_dlp', '--dump-json', '--skip-download',
             f'https://www.youtube.com/watch?v={vid_id}'],
            capture_output=True, timeout=60
        )
        meta = json.loads(r.stdout.decode('utf-8', errors='replace'))
        title = meta.get('title', label)
    except:
        title = label

    user_msg = f"영상 제목: {title}\n\n자막:\n{subtitle}"

    print(f'\n--- Claude API 호출 ---')
    print(f'System prompt 길이: {len(prompt)}자')
    print(f'User message 길이: {len(user_msg)}자')

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            temperature=0,
            system=prompt,
            messages=[{"role": "user", "content": user_msg}]
        )
        raw = response.content[0].text
        print(f'\n--- Claude 응답 (raw) ---')
        print(raw)
    except Exception as e:
        print(f'\n--- Claude API 에러 ---')
        print(str(e)[:500])

    print(f'\n{"="*80}\n')
