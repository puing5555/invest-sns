# -*- coding: utf-8 -*-
import sys, json, re, time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
import os
ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / '.env.local')
import anthropic
client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

import requests
SUPABASE_URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
SB_H = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}', 'Accept': 'application/json'}
r = requests.get(
    f'{SUPABASE_URL}/rest/v1/influencer_videos?select=video_id,title,subtitle_text,duration_seconds,channel_id&video_id=eq.f3XyT2v2WVc',
    headers=SB_H
)
v = r.json()[0]
print(f'subtitle len: {len(v.get("subtitle_text") or "")}')

PROMPT_V12 = ROOT / 'prompts' / 'pipeline_v12.md'
prompt_text = PROMPT_V12.read_text(encoding='utf-8')
subtitle = v.get('subtitle_text', '') or ''
dur = v.get('duration_seconds', 0) or 0
dur_str = f'{dur//60}분 {dur%60}초' if dur else '알 수 없음'
header = f"""[EVAL MODE - 자막 텍스트 기반 분석]
영상 제목: {v.get('title', '')}
영상 길이: {dur_str}

=== 자막 텍스트 시작 ===
{subtitle}
=== 자막 텍스트 끝 ===

위 자막을 분석하여 다음 프롬프트 지시에 따라 시그널을 추출하세요:

"""
full_prompt = header + prompt_text
full_prompt = full_prompt.replace('{VIDEO_DURATION_INFO}', f'영상 길이 {dur_str}')
full_prompt = full_prompt.replace('{CHANNEL_URL}', '')
full_prompt_final = full_prompt + '\n\n반드시 JSON 형식으로만 출력하세요: {"signals": [...]}'
print(f'Prompt total len: {len(full_prompt_final)}')
print('Calling Claude V12...')

try:
    msg = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=8192,
        temperature=0,
        messages=[{'role': 'user', 'content': full_prompt_final}]
    )
    print(f'stop_reason: {msg.stop_reason}')
    print(f'content count: {len(msg.content)}')
    if msg.content:
        print(f'content[0] type: {type(msg.content[0]).__name__}')
        text = msg.content[0].text
        print(f'text type: {type(text).__name__}')
        if text:
            print(f'text[:300]: {text[:300]}')
        else:
            print('TEXT IS NONE/EMPTY')
    else:
        print('CONTENT IS EMPTY')
except BaseException as e:
    print(f'ERROR TYPE: {type(e).__name__}')
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
