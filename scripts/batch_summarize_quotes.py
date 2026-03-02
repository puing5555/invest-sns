import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests, json, time
import anthropic

key = open('.env.local').readlines()[2].split('=',1)[1].strip()
h = {'apikey': key, 'Authorization': 'Bearer ' + key}
r = requests.get('https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals?select=id,stock,ticker,key_quote', headers=h)
data = r.json()
long = [d for d in data if d.get('key_quote') and len(d['key_quote']) > 200]
long.sort(key=lambda x: len(x['key_quote']), reverse=True)

print(f"Found {len(long)} signals with key_quote > 200 chars")

client = anthropic.Anthropic()
h_update = {
    'apikey': key,
    'Authorization': 'Bearer ' + key,
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

success = 0
fail = 0

for i, s in enumerate(long):
    kq = s['key_quote']
    stock = s['stock']
    sid = s['id']
    
    try:
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": f"다음 투자 시그널의 key_quote를 핵심만 1~2문장(최대 200자)으로 요약해줘. 원문의 투자 판단과 근거를 반드시 포함해. 마크다운 볼드체 쓰지 마. 순수 텍스트만.\n\n종목: {stock}\n원문: {kq}"
            }]
        )
        summary = msg.content[0].text.strip()
        
        # Update DB
        r2 = requests.patch(
            f'https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals?id=eq.{sid}',
            headers=h_update,
            json={'key_quote': summary}
        )
        
        status = "OK" if r2.status_code == 200 else f"FAIL({r2.status_code})"
        print(f"  {i+1}/{len(long)} [{sid[:8]}] {stock}: {len(kq)} -> {len(summary)} chars | {status}")
        
        if r2.status_code == 200:
            success += 1
        else:
            fail += 1
        
        time.sleep(1)
    except Exception as e:
        print(f"  {i+1}/{len(long)} [{sid[:8]}] ERROR: {e}")
        fail += 1

print(f"\nDone! Success={success}, Fail={fail}")
