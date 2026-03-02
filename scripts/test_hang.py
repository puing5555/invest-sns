"""Test if requests.post actually respects timeout"""
import sys, time, json, os, requests
sys.path.append('.')
from pipeline_config import PipelineConfig

config = PipelineConfig()

# Load subtitle
sub_file = os.path.join('..', '..', 'subs', 'sesang101', 'BeEHwOe-J98.json')
with open(sub_file, 'r', encoding='utf-8') as f:
    segments = json.load(f)
subtitle = " ".join(s.get('text', '') for s in segments if isinstance(s, dict)).strip()

prompt_template = config.load_prompt()
prompt = prompt_template.replace('{CHANNEL_URL}', 'https://www.youtube.com/@sesang101')
prompt += f"\n\n=== 자막 ===\n{subtitle}\n\n시그널 JSON으로 추출:"

headers = {
    'Content-Type': 'application/json',
    'x-api-key': config.ANTHROPIC_API_KEY,
    'anthropic-version': '2023-06-01'
}

payload = {
    'model': 'claude-3-haiku-20240307',
    'max_tokens': 4000,
    'messages': [{'role': 'user', 'content': prompt}]
}

print(f'Prompt: {len(prompt)} chars')
print(f'Start: {time.strftime("%H:%M:%S")}')

start = time.time()
try:
    resp = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers=headers,
        json=payload,
        timeout=(10, 120)
    )
    elapsed = time.time() - start
    print(f'Done: {resp.status_code} in {elapsed:.1f}s')
    if resp.status_code == 200:
        text = resp.json()['content'][0]['text'][:200]
        print(f'Text: {text}')
except requests.exceptions.Timeout:
    elapsed = time.time() - start
    print(f'TIMEOUT after {elapsed:.1f}s')
except Exception as e:
    elapsed = time.time() - start
    print(f'Error ({elapsed:.1f}s): {type(e).__name__}: {e}')
