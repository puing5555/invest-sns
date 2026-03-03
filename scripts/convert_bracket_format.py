import json, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open('data/analyst_reports.json','r',encoding='utf-8'))

sections = ['투자포인트', '실적전망', '밸류에이션', '리스크', '결론']
converted = 0

for ticker in d:
    for r in d[ticker]:
        detail = r.get('ai_detail','') or ''
        if '## 투자포인트' in detail:
            continue
        if '【투자포인트】' not in detail:
            continue
        
        new_detail = detail
        for sec in sections:
            new_detail = re.sub(r'【' + sec + r'】\s*', '\n\n## ' + sec + '\n', new_detail)
        
        new_detail = re.sub(r'\n{3,}', '\n\n', new_detail).strip()
        r['ai_detail'] = new_detail
        converted += 1

print(f"Converted bracket format: {converted}")

with open('data/analyst_reports.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print("Saved!")

# Check remaining
remaining = 0
for ticker in d:
    for r in d[ticker]:
        detail = r.get('ai_detail','') or ''
        if detail.strip() and '## 투자포인트' not in detail:
            remaining += 1
            if remaining <= 1:
                print(f"\nRemaining: {detail[:200]}")

print(f"\nTotal remaining non-standard: {remaining}")
