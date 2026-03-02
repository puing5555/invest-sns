import sys, time, requests
sys.path.append('.')
from pipeline_config import PipelineConfig

config = PipelineConfig()

headers = {
    'Content-Type': 'application/json',
    'x-api-key': config.ANTHROPIC_API_KEY,
    'anthropic-version': '2023-06-01'
}

# Short test with real analysis prompt
prompt = config.load_prompt()
print(f'Prompt length: {len(prompt)} chars')

payload = {
    'model': 'claude-3-haiku-20240307',
    'max_tokens': 4000,
    'messages': [{'role': 'user', 'content': prompt + '\n\nTest: just return {"signals": []}'}]
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
        print(f'Response ({len(text)} chars): {text[:200]}')
    else:
        print(f'Error: {resp.text[:200]}')
except requests.exceptions.Timeout:
    elapsed = time.time() - start
    print(f'TIMEOUT after {elapsed:.1f}s')
except Exception as e:
    elapsed = time.time() - start
    print(f'Error ({elapsed:.1f}s): {e}')
