"""
analyst_reports_regenerated.json → Supabase analyst_reports.ai_summary 업데이트
매칭 기준: ticker + title (정확히 일치)
"""
import json
import urllib.request
import urllib.parse
import time

# 환경변수 로드
env = {}
with open('C:/Users/Mario/work/invest-sns/.env.local', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#') and line:
            k, v = line.split('=', 1)
            env[k] = v

service_key = env['SUPABASE_SERVICE_ROLE_KEY']
supabase_url = env['NEXT_PUBLIC_SUPABASE_URL']
headers = {
    'apikey': service_key,
    'Authorization': f'Bearer {service_key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

# 1) regenerated JSON 로드
with open('C:/Users/Mario/work/invest-sns/data/analyst_reports_regenerated.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)

all_reports = []
for ticker, reports in raw.items():
    if isinstance(reports, list):
        all_reports.extend(reports)
    elif isinstance(reports, dict):
        all_reports.append(reports)

print(f'JSON 레코드 수: {len(all_reports)}')

# 2) DB 전체 로드 (id + ticker + title)
url = f'{supabase_url}/rest/v1/analyst_reports?select=id,ticker,title&limit=600'
req = urllib.request.Request(url, headers={'apikey': service_key, 'Authorization': f'Bearer {service_key}'})
res = urllib.request.urlopen(req)
db_records = json.loads(res.read().decode('utf-8'))
print(f'DB 레코드 수: {len(db_records)}')

# 3) 매핑 테이블 생성 (ticker+title → id)
db_map = {}
for r in db_records:
    key = (str(r.get('ticker', '')).strip(), str(r.get('title', '')).strip())
    db_map[key] = r['id']

# 4) 매칭 및 업데이트
matched = 0
not_matched = 0
failed = []

for i, report in enumerate(all_reports):
    ticker = str(report.get('ticker', '')).strip()
    title = str(report.get('title', '')).strip()
    ai_detail = report.get('ai_detail', '')

    if not ai_detail:
        not_matched += 1
        continue

    key = (ticker, title)
    record_id = db_map.get(key)

    if not record_id:
        print(f'  [NO MATCH] ticker={ticker} | title={title[:40]}')
        not_matched += 1
        continue

    # PATCH ai_summary
    patch_url = f'{supabase_url}/rest/v1/analyst_reports?id=eq.{record_id}'
    patch_data = json.dumps({'ai_summary': ai_detail}).encode('utf-8')
    patch_req = urllib.request.Request(patch_url, data=patch_data, headers=headers, method='PATCH')

    try:
        patch_res = urllib.request.urlopen(patch_req)
        matched += 1
        if (i + 1) % 50 == 0:
            print(f'  진행: {i+1}/{len(all_reports)} | 성공: {matched}')
    except Exception as e:
        failed.append({'id': record_id, 'ticker': ticker, 'error': str(e)})
        print(f'  [ERROR] {ticker} | {title[:30]} | {e}')

    time.sleep(0.05)  # rate limit 방지

print(f'\n=== 완료 ===')
print(f'업데이트 성공: {matched}')
print(f'매칭 안됨/ai_detail 없음: {not_matched}')
print(f'실패: {len(failed)}')
if failed:
    print('실패 목록:', failed[:5])
