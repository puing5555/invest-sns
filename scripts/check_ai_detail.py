import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open('data/analyst_reports.json','r',encoding='utf-8'))
count_bold = 0
count_header = 0
count_empty = 0
for ticker in d:
    for r in d[ticker]:
        detail = r.get('ai_detail','') or ''
        if not detail:
            count_empty += 1
        elif '**투자포인트' in detail:
            count_bold += 1
        elif '## 투자포인트' in detail:
            count_header += 1
        else:
            count_empty += 1

print(f"Bold format: {count_bold}")
print(f"Header format: {count_header}")
print(f"Empty/other: {count_empty}")
print(f"Total: {count_bold + count_header + count_empty}")

# Show sample
for ticker in list(d.keys())[:1]:
    r = d[ticker][0]
    detail = r.get('ai_detail','') or ''
    print("\n=== SAMPLE ===")
    print(detail[:600])
