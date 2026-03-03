import json, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open('data/analyst_reports.json','r',encoding='utf-8'))

fixed = 0
sections = ['투자포인트', '실적전망', '밸류에이션', '리스크', '결론']

for ticker in d:
    for r in d[ticker]:
        detail = r.get('ai_detail','') or ''
        if '## 투자포인트' not in detail:
            continue
        
        new_detail = detail
        for sec in sections:
            # Ensure ## header is on its own line with blank line before it
            new_detail = re.sub(r'(?<!\n)\s*## ' + sec, '\n\n## ' + sec, new_detail)
            # Ensure newline after ## header line
            new_detail = re.sub(r'(## ' + sec + r')\s*(?!\n)', r'\1\n', new_detail)
        
        new_detail = re.sub(r'\n{3,}', '\n\n', new_detail).strip()
        
        if new_detail != detail:
            r['ai_detail'] = new_detail
            fixed += 1

print(f"Fixed newlines: {fixed}")

with open('data/analyst_reports.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print("Saved!")

# Verify
d2 = json.load(open('data/analyst_reports.json','r',encoding='utf-8'))
sample = d2[list(d2.keys())[1]][0]
print("\n=== VERIFY ===")
print((sample.get('ai_detail','') or '')[:500])
