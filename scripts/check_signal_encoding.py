#!/usr/bin/env python3
with open('lib/supabase.ts', encoding='utf-8') as f:
    lines = f.readlines()

# 28-43번 라인 (getSignalColor)
for i in range(27, 46):
    line = lines[i]
    codepoints = [hex(ord(c)) for c in line.rstrip() if ord(c) > 127]
    if codepoints:
        print(f"Line {i+1}: {line.rstrip()!r}")
        print(f"  Korean chars codepoints: {codepoints}")

# 비교
signals_db = ['매수', '긍정', '중립', '부정', '매도']
signals_code = []
for i in range(27, 46):
    line = lines[i]
    if "case '" in line and "case 'B" not in line and "case 'P" not in line and "case 'N" not in line and "case 'C" not in line and "case 'S" not in line:
        val = line.strip().replace("case '", "").replace("':", "")
        signals_code.append(val)
        print(f"코드 시그널값: {val!r} -> codepoints: {[hex(ord(c)) for c in val]}")

print("\n=== DB 시그널 vs 코드 시그널 비교 ===")
for db_s, code_s in zip(signals_db, signals_code):
    match = db_s == code_s
    print(f"DB: {db_s!r} | Code: {code_s!r} | {'일치' if match else '불일치!!!'}")
