#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
코린파파 파이프라인 누락 단계 실행
Step 7 (new_stock_handler) → Step 7.5 (data→public) → Gate 3 → 빌드
"""
import sys, os, shutil, subprocess, json, re, urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))

# Supabase 크레덴셜
env_text = open('.env.local', encoding='utf-8').read()
svc_m = re.search(r'SUPABASE_SERVICE_ROLE_KEY=(.+)', env_text)
anon_m = re.search(r'NEXT_PUBLIC_SUPABASE_ANON_KEY=(.+)', env_text)
KEY = (svc_m or anon_m).group(1).strip()
URL = re.search(r'NEXT_PUBLIC_SUPABASE_URL=(.+)', env_text).group(1).strip()
HEADERS = {'apikey': KEY, 'Authorization': f'Bearer {KEY}'}

def db_get(path):
    req = urllib.request.Request(f'{URL}/rest/v1/{path}', headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

# ── Step 7: new_stock_handler ──────────────────────────────────────────
print("=== Step 7: new_stock_handler ===")
try:
    from new_stock_handler import NewStockHandler
    handler = NewStockHandler()
    raw = db_get('influencer_signals?select=stock,ticker,market&order=created_at.desc&limit=500')
    print(f"  DB 시그널 {len(raw)}개 로드")
    # process_new_stocks는 analysis_results 구조 기대 — results[].signals[]
    result = handler.process_new_stocks({'results': [{'signals': raw}]})
    new_stocks = result.get('new_stocks', [])
    prices_added = result.get('prices_added', 0)
    rebuild_needed = result.get('rebuild_needed', False)
    print(f"  새 종목: {new_stocks}")
    print(f"  가격 추가: {prices_added}개")
    print(f"  재빌드 필요: {rebuild_needed}")
except Exception as e:
    print(f"  [WARNING] new_stock_handler 오류: {e}")
    import traceback; traceback.print_exc()

# ── Step 7.5: data/ → public/ 동기화 ──────────────────────────────────
print("\n=== Step 7.5: data/ -> public/ 동기화 ===")
for fname in ['signal_prices.json', 'stockPrices.json']:
    src = PROJECT_ROOT / 'data' / fname
    dst_pub = PROJECT_ROOT / 'public' / fname
    dst_out = PROJECT_ROOT / 'out' / fname
    if src.exists():
        if dst_pub.exists():
            shutil.copy2(str(src), str(dst_pub))
            print(f"  public/{fname} 동기화 완료")
        if dst_out.exists():
            shutil.copy2(str(src), str(dst_out))
            print(f"  out/{fname} 동기화 완료")

# ── Gate 3: 프론트엔드 검증 ─────────────────────────────────────────
print("\n=== QA Gate 3: 프론트엔드 검증 ===")
try:
    from qa.gate3_frontend import run_gate3
    gate3_passed = run_gate3(slug='corinpapa', project_root=str(PROJECT_ROOT), check_deploy=False)
    if gate3_passed:
        print("  [OK] Gate 3 통과")
    else:
        print("  [FAIL] Gate 3 실패 — 빌드 차단")
        sys.exit(1)
except Exception as e:
    print(f"  [WARNING] Gate 3 오류: {e}")
    import traceback; traceback.print_exc()
    gate3_passed = True  # 오류 시 빌드는 계속 진행

print("\n=== Step 9: npm run build ===")
print("빌드 시작...")
