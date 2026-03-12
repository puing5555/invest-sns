#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DB 데이터 품질 수정:
1. ticker -USD 접미사 제거 (BTC-USD → BTC)
2. market KR → US 수정 (미국주식이 KR로 잘못 저장된 경우)
"""
import json, re, urllib.request
from pathlib import Path

env = Path('.env.local').read_text(encoding='utf-8')
KEY = re.search(r'NEXT_PUBLIC_SUPABASE_ANON_KEY=(.+)', env).group(1).strip()
URL = re.search(r'NEXT_PUBLIC_SUPABASE_URL=(.+)', env).group(1).strip()

HEADERS = {
    'apikey': KEY,
    'Authorization': f'Bearer {KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def db_get(path):
    req = urllib.request.Request(f'{URL}/rest/v1/{path}', headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def db_patch(path, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f'{URL}/rest/v1/{path}', data=body, method='PATCH', headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

# ── 1. ticker -USD 접미사 제거 ────────────────────────────────────────
print("=== 1. ticker -USD 접미사 제거 ===")
# 각 ticker별로 PATCH
usd_tickers = {
    'BTC-USD': 'BTC',
    'ETH-USD': 'ETH',
    'XRP-USD': 'XRP',
    'SOL-USD': 'SOL',
    'LINK-USD': 'LINK',
    'CNTN-USD': 'CNTN',
}
for old_t, new_t in usd_tickers.items():
    # 현재 건수 확인
    rows = db_get(f'influencer_signals?ticker=eq.{old_t}&select=id')
    if not rows:
        print(f"  {old_t}: 없음")
        continue
    # PATCH
    result = db_patch(f'influencer_signals?ticker=eq.{old_t}', {'ticker': new_t})
    print(f"  {old_t} → {new_t}: {len(result)}건 수정")

# ── 2. market KR → US 수정 ──────────────────────────────────────────
print("\n=== 2. market KR → US 수정 ===")
US_TICKERS = ['TSLA', 'PLTR', 'NVDA', 'AAPL', 'META', 'GOOGL', 'AMZN',
              'MSFT', 'OKLO', 'SMR', 'SBET', 'BTBT', 'BLSH', 'MARA',
              'COIN', 'RIOT', 'MSTR', 'AMD', 'INTC', 'QCOM', 'ARM',
              'NFLX', 'PYPL', 'SQ', 'AFRM', 'IONQ', 'RKLB', 'SMCI']

for ticker in US_TICKERS:
    rows = db_get(f'influencer_signals?ticker=eq.{ticker}&market=eq.KR&select=id')
    if not rows:
        continue
    result = db_patch(f'influencer_signals?ticker=eq.{ticker}&market=eq.KR', {'market': 'US'})
    print(f"  {ticker} market KR → US: {len(result)}건 수정")

# ── 3. CNTN ticker도 CC로 통일 (별칭 정리) ────────────────────────────
print("\n=== 3. CNTN 확인 ===")
cntn_rows = db_get('influencer_signals?ticker=eq.CNTN&select=id,market&limit=3')
print(f"  CNTN 시그널: {len(cntn_rows)}건 (시장: {set(r['market'] for r in cntn_rows)})")

# 크립토 market 확인
print("\n=== 크립토 ticker market 확인 ===")
crypto_tickers = ['BTC', 'ETH', 'XRP', 'SOL', 'LINK', 'PENGU', 'UNI', 'ARB', 'WLD', 'XLM', 'ADA', 'ORBS']
for t in crypto_tickers:
    rows = db_get(f'influencer_signals?ticker=eq.{t}&select=market&limit=5')
    markets = list(set(r['market'] for r in rows)) if rows else []
    wrong = [m for m in markets if m != 'CRYPTO']
    if wrong:
        print(f"  {t}: market 오류 {wrong} ({len(rows)}건) → CRYPTO로 수정")
        db_patch(f'influencer_signals?ticker=eq.{t}&market=neq.CRYPTO', {'market': 'CRYPTO'})
    elif rows:
        print(f"  {t}: OK ({len(rows)}건)")

print("\n=== 완료 ===")
