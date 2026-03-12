"""404 위험 티커 전체 분류 스크립트"""
import json, os, re
from pathlib import Path

BASE = Path(__file__).parent.parent
data = json.load(open(BASE / 'data' / 'signal_prices.json', encoding='utf-8'))
out_stock = set(os.listdir(BASE / 'out' / 'stock'))
tickers_json = set(json.load(open(BASE / 'data' / 'stock_tickers.json', encoding='utf-8')))

uuid_pat = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}')
uuid_tickers = {}
for k, v in data.items():
    if uuid_pat.match(k) and isinstance(v, dict):
        t = v.get('ticker', '')
        if t:
            uuid_tickers[t] = uuid_tickers.get(t, 0) + 1

usd_issues = []
missing_pages = []
suffix_issues = []

for t, cnt in sorted(uuid_tickers.items()):
    if t in out_stock:
        continue
    if t.endswith('-USD'):
        base = t.replace('-USD', '')
        base_exists = base in out_stock
        usd_issues.append((t, cnt, base, base_exists))
    elif '.' in t and (t.endswith('.KS') or t.endswith('.T') or t.endswith('.HK') or t.endswith('.DE')):
        base = t.split('.')[0]
        base_ok = base in out_stock
        suffix_issues.append((t, cnt, base, base_ok))
    else:
        missing_pages.append((t, cnt))

print("=== [1] -USD 계열 (normalizeTickerForUrl 대상) ===")
for t, cnt, base, base_ok in usd_issues:
    status = "base OK" if base_ok else "base 페이지도 없음"
    print("  %s (%d개) -> %s: %s" % (t, cnt, base, status))

print()
print("=== [2] .KS/.T/.HK 계열 (거래소 suffix) ===")
for t, cnt, base, base_ok in suffix_issues:
    status = "base OK" if base_ok else "base 없음"
    print("  %s (%d개) -> base %s: %s" % (t, cnt, base, status))

print()
print("=== [3] 완전히 누락된 페이지 (stock_tickers.json 추가 필요) ===")
for t, cnt in missing_pages:
    print("  %s (%d개)" % (t, cnt))

print()
print("합계: -USD %d개, suffix %d개, 누락 %d개" % (len(usd_issues), len(suffix_issues), len(missing_pages)))
