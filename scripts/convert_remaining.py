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
        if not detail.strip():
            continue
        
        new_detail = detail
        changed = False
        for sec in sections:
            # **섹션:** or **섹션**: or **섹션**:
            patterns = [
                r'\*\*' + sec + r':\*\*\s*',
                r'\*\*' + sec + r'\*\*:\s*',
                r'\*\*' + sec + r'\*\*\s*',
                r'【' + sec + r'】\s*',
            ]
            for pat in patterns:
                if re.search(pat, new_detail):
                    new_detail = re.sub(pat, '\n\n## ' + sec + '\n', new_detail)
                    changed = True
                    break
        
        if changed:
            new_detail = re.sub(r'\n{3,}', '\n\n', new_detail).strip()
            r['ai_detail'] = new_detail
            converted += 1

print(f"Converted remaining: {converted}")

with open('data/analyst_reports.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

# Final count
ok = 0
not_ok = 0
for ticker in d:
    for r in d[ticker]:
        detail = r.get('ai_detail','') or ''
        if '## 투자포인트' in detail:
            ok += 1
        else:
            not_ok += 1
            if not_ok <= 2:
                print(f"NOT OK: {detail[:150]}")

print(f"\nFinal: {ok} OK, {not_ok} not OK (total {ok+not_ok})")
