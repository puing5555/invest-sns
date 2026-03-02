import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests, json, os, time

key = open('.env.local').readlines()[2].split('=',1)[1].strip()
h = {'apikey': key, 'Authorization': 'Bearer ' + key}
r = requests.get('https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals?select=id,stock,ticker,key_quote', headers=h)
data = r.json()
long = [d for d in data if d.get('key_quote') and len(d['key_quote']) > 200]
long.sort(key=lambda x: len(x['key_quote']), reverse=True)

# Sample 3
samples = long[:3]

import anthropic
client = anthropic.Anthropic()

for i, s in enumerate(samples):
    kq = s['key_quote']
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role":"user","content":f"다음 투자 시그널의 key_quote를 핵심만 1~2문장(최대 200자)으로 요약해줘. 원문의 투자 판단과 근거를 반드시 포함해.\n\n종목: {s['stock']}\n원문: {kq}"}]
    )
    summary = msg.content[0].text.strip()
    print(f"\n=== Sample {i+1}: {s['stock']} ({len(kq)}자 -> {len(summary)}자) ===")
    print(f"BEFORE: {kq[:150]}...")
    print(f"AFTER:  {summary}")
    time.sleep(1)
