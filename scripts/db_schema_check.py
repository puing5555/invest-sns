"""DB 스키마 전체 조회 - Supabase REST API 사용 (Service Role Key)"""
import os, requests, json
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))

BASE = os.environ['NEXT_PUBLIC_SUPABASE_URL']
# Service Role Key 사용 (information_schema 접근 가능)
KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
HEADERS = {
    'apikey': KEY,
    'Authorization': 'Bearer ' + KEY,
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Prefer': 'return=representation'
}

def sql(query):
    """Supabase REST RPC로 SQL 실행"""
    r = requests.post(f"{BASE}/rest/v1/rpc/query", json={"sql": query}, headers=HEADERS)
    return r.status_code, r.json() if r.headers.get('content-type','').startswith('application/json') else r.text

# ─── 1. 테이블 목록 (REST /rest/v1/ 경로 목록) ───
print("=" * 60)
print("1. 전체 테이블 목록 (public schema)")
print("=" * 60)

# information_schema 직접 쿼리는 RPC 없이 안 됨
# 대신 각 알려진 테이블 존재 여부 + count 확인
KNOWN_TABLES = [
    'influencer_channels', 'influencer_videos', 'influencer_signals',
    'channels', 'videos', 'signals', 'speakers', 'disclosures',
    'signal_prices', 'stock_prices', 'analyst_reports',
    'research_invest_platforms'
]

print(f"\n{'테이블명':<35} {'건수':>10}")
print("-" * 47)
existing = []
for tbl in KNOWN_TABLES:
    r = requests.get(
        f"{BASE}/rest/v1/{tbl}?select=id",
        headers={**HEADERS, 'Prefer': 'count=exact', 'Range': '0-0'}
    )
    if r.status_code in (200, 206):
        ct = r.headers.get('content-range', '?/?')
        total = ct.split('/')[-1] if '/' in ct else '?'
        print(f"  {tbl:<33} {total:>10}")
        existing.append(tbl)
    elif r.status_code == 404:
        pass  # 없는 테이블
    else:
        print(f"  {tbl:<33} 오류 {r.status_code}")

# ─── 2. 주요 테이블 컬럼 ───
print("\n\n" + "=" * 60)
print("2. 테이블 컬럼 상세")
print("=" * 60)

for tbl in existing:
    r = requests.get(
        f"{BASE}/rest/v1/{tbl}?limit=1",
        headers=HEADERS
    )
    if r.status_code == 200:
        rows = r.json()
        if rows and isinstance(rows, list) and rows[0]:
            cols = list(rows[0].keys())
            print(f"\n  [{tbl}]")
            for col in cols:
                val = rows[0][col]
                typ = type(val).__name__
                print(f"    - {col:<35} ({typ})")
        else:
            # 빈 테이블 - OPTIONS로 컬럼 확인
            r2 = requests.options(f"{BASE}/rest/v1/{tbl}", headers=HEADERS)
            try:
                schema = r2.json()
                props = schema.get('definitions', {}).get(tbl, {}).get('properties', {})
                if props:
                    print(f"\n  [{tbl}] (빈 테이블, OPTIONS 스키마)")
                    for col, info in props.items():
                        print(f"    - {col:<35} ({info.get('type','?')})")
            except:
                print(f"\n  [{tbl}] 빈 테이블")
