import sys, time, json, os, requests
sys.path.append('.')
from pipeline_config import PipelineConfig

config = PipelineConfig()
prompt_template = config.load_prompt()

# Load subtitle
sub_file = os.path.join('..', '..', 'subs', 'sesang101', 'BeEHwOe-J98.json')
with open(sub_file, 'r', encoding='utf-8') as f:
    segments = json.load(f)
subtitle = " ".join(s.get('text', '') for s in segments if isinstance(s, dict)).strip()

print(f'Subtitle: {len(subtitle)} chars')

# Build prompt
prompt = prompt_template.replace('{CHANNEL_URL}', 'https://www.youtube.com/@sesang101')
prompt += f"""

=== 분석 대상 영상 ===
제목: Palantir's Future Amidst the New Year's Market Crash
URL: https://www.youtube.com/watch?v=BeEHwOe-J98

=== 자막 내용 ===
{subtitle}

=== 분석 지시사항 ===
위 영상의 자막을 V10.1 프롬프트 규칙에 따라 분석하고, JSON 형태로 시그널을 추출해주세요.
"""

print(f'Full prompt: {len(prompt)} chars')

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

print(f'Request at {time.strftime("%H:%M:%S")}...')
start = time.time()
try:
    resp = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers=headers,
        json=payload,
        timeout=(10, 120)
    )
    elapsed = time.time() - start
    print(f'Status: {resp.status_code} ({elapsed:.1f}s)')
    if resp.status_code == 200:
        data = resp.json()
        text = data["content"][0]["text"]
        print(f'Response ({len(text)} chars): {text[:500]}')
    else:
        print(f'Error ({resp.status_code}): {resp.text[:300]}')
except requests.exceptions.Timeout:
    elapsed = time.time() - start
    print(f'TIMEOUT after {elapsed:.1f}s')
except Exception as e:
    elapsed = time.time() - start
    print(f'Error ({elapsed:.1f}s): {e}')
