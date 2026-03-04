import json, os, requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')

headers = {'apikey': key, 'Authorization': f'Bearer {key}'}
resp = requests.get(
    f'{url}/rest/v1/influencer_signals?select=id,stock_name,signal_type,key_quote,reasoning',
    headers=headers
)
data = resp.json()
print(f'총 시그널: {len(data)}개')

short = [d for d in data if d.get('reasoning') and len(d['reasoning']) < 50]
medium = [d for d in data if d.get('reasoning') and 50 <= len(d['reasoning']) < 100]
long_r = [d for d in data if d.get('reasoning') and len(d['reasoning']) >= 100]
no_reason = [d for d in data if not d.get('reasoning')]
print(f'reasoning 없음: {len(no_reason)}개')
print(f'reasoning <50자: {len(short)}개')
print(f'reasoning 50-100자: {len(medium)}개')
print(f'reasoning 100자+: {len(long_r)}개')

short_kq = [d for d in data if d.get('key_quote') and len(d['key_quote']) < 30]
long_kq = [d for d in data if d.get('key_quote') and len(d['key_quote']) >= 100]
print(f'key_quote <30자: {len(short_kq)}개')
print(f'key_quote 100자+: {len(long_kq)}개')

target = [d for d in data if not d.get('reasoning') or len(d.get('reasoning','')) < 100]
print(f'\n보강 대상 (reasoning <100자): {len(target)}개')
print(f'보강 불필요 (reasoning 100자+): {len(long_r)}개')

input_tokens = len(target) * 250
output_tokens = len(target) * 200
cost_input = input_tokens / 1_000_000 * 3
cost_output = output_tokens / 1_000_000 * 15
print(f'\n비용 추정 (Claude Sonnet):')
print(f'  보강 대상: {len(target)}회 API 호출')
print(f'  입력: ~{input_tokens:,} 토큰 (${cost_input:.2f})')
print(f'  출력: ~{output_tokens:,} 토큰 (${cost_output:.2f})')
print(f'  합계: ~${cost_input + cost_output:.2f}')

if short:
    s = short[0]
    print(f'\n짧은 reasoning 예시:')
    print(f'  종목: {s["stock_name"]} / {s["signal_type"]}')
    print(f'  key_quote: {s.get("key_quote","")[:100]}')
    print(f'  reasoning: {s.get("reasoning","")}')
