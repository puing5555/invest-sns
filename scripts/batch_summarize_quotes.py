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
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": f"?ㅼ쓬 ?ъ옄 ?쒓렇?먯쓽 key_quote瑜??듭떖留?1~2臾몄옣(理쒕? 200???쇰줈 ?붿빟?댁쨾. ?먮Ц???ъ옄 ?먮떒怨?洹쇨굅瑜?諛섎뱶???ы븿?? 留덊겕?ㅼ슫 蹂쇰뱶泥??곗? 留? ?쒖닔 ?띿뒪?몃쭔.\n\n醫낅ぉ: {stock}\n?먮Ц: {kq}"
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

