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
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{"role":"user","content":f"?ㅼ쓬 ?ъ옄 ?쒓렇?먯쓽 key_quote瑜??듭떖留?1~2臾몄옣(理쒕? 200???쇰줈 ?붿빟?댁쨾. ?먮Ц???ъ옄 ?먮떒怨?洹쇨굅瑜?諛섎뱶???ы븿??\n\n醫낅ぉ: {s['stock']}\n?먮Ц: {kq}"}]
    )
    summary = msg.content[0].text.strip()
    print(f"\n=== Sample {i+1}: {s['stock']} ({len(kq)}??-> {len(summary)}?? ===")
    print(f"BEFORE: {kq[:150]}...")
    print(f"AFTER:  {summary}")
    time.sleep(1)

