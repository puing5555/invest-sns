import json, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open('data/analyst_reports.json','r',encoding='utf-8'))

converted = 0
already_ok = 0
empty = 0
other = 0

sections = ['투자포인트', '실적전망', '밸류에이션', '리스크', '결론']

for ticker in d:
    for r in d[ticker]:
        detail = r.get('ai_detail','') or ''
        if not detail.strip():
            empty += 1
            continue
        
        if '## 투자포인트' in detail:
            already_ok += 1
            continue
        
        if '**투자포인트' in detail:
            # Convert **Section**: or **Section**\n patterns to ## Section
            new_detail = detail
            for sec in sections:
                # Pattern: **섹션**: or **섹션**:  or **섹션** 
                new_detail = re.sub(
                    r'\*\*' + sec + r'\*\*\s*:?\s*',
                    '## ' + sec + '\n',
                    new_detail
                )
            # Clean up: remove leading/trailing whitespace per line, double newlines
            lines = new_detail.split('\n')
            cleaned = []
            for line in lines:
                line = line.rstrip()
                cleaned.append(line)
            new_detail = '\n'.join(cleaned)
            # Remove excessive blank lines
            new_detail = re.sub(r'\n{3,}', '\n\n', new_detail).strip()
            
            r['ai_detail'] = new_detail
            converted += 1
        else:
            other += 1

print(f"Converted: {converted}")
print(f"Already OK: {already_ok}")
print(f"Empty: {empty}")
print(f"Other format: {other}")
print(f"Total: {converted + already_ok + empty + other}")

# Save
with open('data/analyst_reports.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print("Saved!")

# Verify
d2 = json.load(open('data/analyst_reports.json','r',encoding='utf-8'))
sample = d2[list(d2.keys())[1]][0]
print("\n=== VERIFY SAMPLE ===")
print((sample.get('ai_detail','') or '')[:400])
