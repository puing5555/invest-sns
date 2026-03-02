import sys, time, requests
sys.path.append('.')
from pipeline_config import PipelineConfig

config = PipelineConfig()
print(f'API key: {config.ANTHROPIC_API_KEY[:10]}...')

headers = {
    'Content-Type': 'application/json',
    'x-api-key': config.ANTHROPIC_API_KEY,
    'anthropic-version': '2023-06-01'
}

payload = {
    'model': 'claude-3-haiku-20240307',
    'max_tokens': 100,
    'messages': [{'role': 'user', 'content': 'Say hello in Korean'}]
}

print('API test...')
start = time.time()
try:
    resp = requests.post('https://api.anthropic.com/v1/messages', headers=headers, json=payload, timeout=30)
    elapsed = time.time() - start
    print(f'Status: {resp.status_code} ({elapsed:.1f}s)')
    if resp.status_code == 200:
        data = resp.json()
        print(f'Response: {data["content"][0]["text"]}')
    else:
        print(f'Error: {resp.text[:200]}')
except Exception as e:
    elapsed = time.time() - start
    print(f'Error ({elapsed:.1f}s): {e}')
