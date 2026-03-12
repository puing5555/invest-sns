"""
전체 influencer_signals에서:
1. 빈/불완전 레코드 찾기 (signal 없음, stock 없음, key_quote 없음)
2. TSMC 중복 레코드 찾기 (같은 video_id에 TSM 시그널 2개 이상)
"""
from dotenv import load_dotenv
import os, requests, json
from collections import defaultdict

load_dotenv('.env.local')
URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
h = {'apikey': KEY, 'Authorization': f'Bearer {KEY}'}

print("전체 influencer_signals 조회 중...")
all_signals = []
offset = 0
while True:
    r = requests.get(
        f'{URL}/rest/v1/influencer_signals'
        f'?select=id,video_id,stock,ticker,signal,key_quote,created_at'
        f'&offset={offset}&limit=500',
        headers=h
    )
    batch = r.json()
    if not isinstance(batch, list) or not batch:
        break
    all_signals.extend(batch)
    if len(batch) < 500:
        break
    offset += 500

print(f"총 {len(all_signals)}건 조회됨")

# 1. 빈 레코드 (signal 없음 or stock 없음 or key_quote 없음)
print("\n=== 빈/불완전 레코드 ===")
blank = []
for s in all_signals:
    reasons = []
    if not s.get('signal') or not s.get('signal', '').strip():
        reasons.append('signal_empty')
    if not s.get('stock') or not s.get('stock', '').strip():
        reasons.append('stock_empty')
    if not s.get('key_quote') or not s.get('key_quote', '').strip():
        reasons.append('key_quote_empty')
    if reasons:
        blank.append({**s, '_reasons': reasons})

print(f"불완전 레코드 총 {len(blank)}건")
for b in blank[:10]:
    print(f"  id={b['id']}, stock={repr(b['stock'])}, signal={repr(b['signal'])}, reasons={b['_reasons']}")

# 전체 빈 레코드 (stock AND signal AND key_quote 모두 없음)
fully_blank = [s for s in blank if set(s['_reasons']) >= {'signal_empty', 'stock_empty', 'key_quote_empty'}]
print(f"\n완전히 빈 레코드(stock+signal+key_quote 모두 없음): {len(fully_blank)}건")
for b in fully_blank:
    print(f"  id={b['id']}, created_at={b['created_at']}")

# 2. TSMC 중복
print("\n=== TSMC 중복 레코드 ===")
tsm_by_video = defaultdict(list)
for s in all_signals:
    tick = (s.get('ticker') or '').upper()
    stk = (s.get('stock') or '').upper()
    if tick == 'TSM' or 'TSMC' in stk:
        tsm_by_video[s['video_id']].append(s)

dups = {vid: sigs for vid, sigs in tsm_by_video.items() if len(sigs) > 1}
print(f"TSMC 중복 video_id: {len(dups)}건")
for vid, sigs in dups.items():
    print(f"\n  video_id={vid}:")
    for s in sigs:
        print(f"    id={s['id']}, signal={s.get('signal')}, created={s['created_at'][:10]}")
