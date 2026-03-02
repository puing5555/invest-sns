#!/usr/bin/env python3
import os, json, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; from pathlib import Path
load_dotenv(Path(__file__).parent.parent / '.env.local')

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY','') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY','')

def fetch(ep):
    req = urllib.request.Request(url+'/rest/v1/'+ep, headers={'apikey':key,'Authorization':'Bearer '+key})
    return json.loads(urllib.request.urlopen(req).read())

# All signals
sigs = fetch('influencer_signals?select=id,video_id,speaker_id,stock,timestamp,key_quote&limit=500')
print(f"Total signals: {len(sigs)}")

null_ts = []
zero_ts = []
valid_ts = []
for s in sigs:
    ts = s.get('timestamp')
    if not ts or ts in ('null', 'None', ''):
        null_ts.append(s)
    elif ts in ('0:00', '00:00', '0:00:00', '00:00:00'):
        zero_ts.append(s)
    else:
        valid_ts.append(s)

print(f"Valid timestamp: {len(valid_ts)}")
print(f"Null timestamp: {len(null_ts)}")
print(f"0:00 timestamp: {len(zero_ts)}")

# Sesang specific
sesang_sp = 'b9496a5f-06fa-47eb-bc2d-47060b095534'
sesang_sigs = [s for s in sigs if s['speaker_id'] == sesang_sp]
sesang_null = [s for s in sesang_sigs if s in null_ts or s in zero_ts]
print(f"\n세상학개론: {len(sesang_sigs)} signals, {len(sesang_null)} without timestamp")

print("\n=== Sesang signals without timestamp (sample) ===")
for s in sesang_null[:10]:
    quote = (s.get('key_quote') or '')[:60]
    print(f"  {s['stock']} | ts={s.get('timestamp')} | vid={s['video_id'][:12]} | quote={quote}")

print("\n=== All signals without timestamp by speaker ===")
from collections import Counter
no_ts = null_ts + zero_ts
sp_counts = Counter(s['speaker_id'][:8] for s in no_ts)
for sp, cnt in sp_counts.most_common():
    print(f"  {sp}...: {cnt}")
