#!/usr/bin/env python3
import os, re

# 검사할 파일들
files_to_check = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ['node_modules', '.next', '.git', 'out']]
    for f in files:
        if f.endswith(('.tsx', '.ts')) and 'node_modules' not in root:
            files_to_check.append(os.path.join(root, f))

print("=== signal 빈값/undefined 처리 패턴 검색 ===\n")

PATTERNS = [
    # signal 빈값 폴백
    r"signal.*\|\|.*['\"]",
    r"signal.*\?\?.*['\"]",
    # signal_type 사용 (column name 불일치)  
    r"signal_type",
    # 빈 시그널 필터링
    r"signal.*===.*['\"]['\"]",
    r"filter.*signal",
]

found = {}
for fpath in files_to_check:
    try:
        with open(fpath, encoding='utf-8') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            for pat in PATTERNS:
                if re.search(pat, line, re.IGNORECASE):
                    key = f"{fpath}:{i+1}"
                    found[key] = line.strip()
    except Exception:
        pass

for k, v in list(found.items())[:30]:
    print(f"{k}")
    print(f"  {v}")
    print()

# DB column 확인: signal vs signal_type
print("\n=== 'signal_type' 사용 위치 (column 불일치 위험) ===")
for fpath in files_to_check:
    try:
        with open(fpath, encoding='utf-8') as f:
            content = f.read()
        if 'signal_type' in content:
            lines = [l.strip() for l in content.split('\n') if 'signal_type' in l]
            print(f"\n{fpath}:")
            for l in lines[:5]:
                print(f"  {l}")
    except Exception:
        pass
