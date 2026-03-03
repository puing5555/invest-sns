import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open('data/analyst_reports.json','r',encoding='utf-8'))

count = 0
for ticker in d:
    for r in d[ticker]:
        detail = r.get('ai_detail','') or ''
        if not detail.strip():
            continue
        if '## 투자포인트' in detail:
            continue
        count += 1
        if count <= 3:
            print(f"=== {ticker} / {r.get('title','')[:50]} ===")
            print(detail[:300])
            print("---")

print(f"\nTotal other format: {count}")
