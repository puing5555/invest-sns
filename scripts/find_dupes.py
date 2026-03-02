import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests, json
from difflib import SequenceMatcher
from collections import defaultdict

key = open('.env.local').readlines()[2].split('=',1)[1].strip()
h = {'apikey': key, 'Authorization': 'Bearer ' + key}
r = requests.get('https://arypzhotxflimroprmdk.supabase.co/rest/v1/influencer_signals?select=id,video_id,stock,ticker,signal,key_quote,review_status&order=video_id', headers=h)
data = r.json()
print(f'Total signals: {len(data)}')

groups = defaultdict(list)
for s in data:
    if s['video_id']:
        groups[s['video_id']].append(s)

aliases = {
    'Rocket Lab': 'RKLB', '로켓랩': 'RKLB', '로켓랩 (RKLB)': 'RKLB',
    'Palantir': 'PLTR', '팔라티어': 'PLTR', '팔란티어': 'PLTR',
    'Circle': 'CRCL', '서클': 'CRCL',
    'Tesla': 'TSLA', '테슬라': 'TSLA',
    'MicroStrategy': 'MSTR', '마이크로스트래티지': 'MSTR',
    'NVIDIA': 'NVDA', '엔비디아': 'NVDA',
    'GameStop': 'GME', '게임스탑': 'GME',
    'Iris Energy': 'IREN', '아이리스에너지': 'IREN',
    'Riot Platforms': 'RIOT', '라이엇': 'RIOT',
    'Block': 'SQ', '블록': 'SQ',
    'Coinbase': 'COIN', '코인베이스': 'COIN',
    'ASML': 'ASML',
    'SK하이닉스': '000660', '하이닉스': '000660',
    '삼성전자': '005930',
}

def normalize(stock):
    if not stock:
        return ''
    s = stock.strip()
    if s in aliases:
        return aliases[s]
    return s

def similar(a, b):
    if not a or not b:
        return False
    return SequenceMatcher(None, a[:80], b[:80]).ratio() > 0.6

dupes = []
for vid, sigs in groups.items():
    if len(sigs) < 2:
        continue
    seen = []
    for s in sigs:
        ns = normalize(s['stock'])
        for prev in seen:
            np_ = normalize(prev['stock'])
            same_stock = (ns == np_ and ns) or (s['ticker'] and prev['ticker'] and s['ticker'] == prev['ticker'])
            sim_quote = similar(s.get('key_quote', ''), prev.get('key_quote', ''))
            if same_stock or sim_quote:
                dupes.append((prev, s))
                break
        seen.append(s)

print(f'\nDuplicate pairs found: {len(dupes)}')
delete_ids = []
for i, (a, b) in enumerate(dupes):
    aid = a['id'][:8]
    bid = b['id'][:8]
    print(f'\n--- Pair {i+1} ---')
    print(f'  A: [{aid}] {a["stock"]} | ticker={a["ticker"]} | signal={a["signal"]} | review={a["review_status"]}')
    print(f'     quote: {(a.get("key_quote") or "")[:80]}')
    print(f'  B: [{bid}] {b["stock"]} | ticker={b["ticker"]} | signal={b["signal"]} | review={b["review_status"]}')
    print(f'     quote: {(b.get("key_quote") or "")[:80]}')
    
    if a['ticker'] and not b['ticker']:
        print(f'  -> DELETE B (no ticker)')
        delete_ids.append(b['id'])
    elif b['ticker'] and not a['ticker']:
        print(f'  -> DELETE A (no ticker)')
        delete_ids.append(a['id'])
    elif a['review_status'] == 'approved' and b['review_status'] != 'approved':
        print(f'  -> DELETE B (not approved)')
        delete_ids.append(b['id'])
    elif b['review_status'] == 'approved' and a['review_status'] != 'approved':
        print(f'  -> DELETE A (not approved)')
        delete_ids.append(a['id'])
    else:
        print(f'  -> DELETE B (keep first)')
        delete_ids.append(b['id'])

print(f'\n\n=== SUMMARY ===')
print(f'Total duplicate pairs: {len(dupes)}')
print(f'Delete targets: {len(delete_ids)}')
for did in delete_ids:
    print(f'  DELETE: {did}')
