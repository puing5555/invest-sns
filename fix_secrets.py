#!/usr/bin/env python3
"""git history에서 API 키 제거 스크립트"""
import subprocess, os, re

TARGET_FILES = [
    'scripts/godofIT_analyze.py',
    'scripts/reanalyze_sesang_v11.js',
]
PATTERN = r'sk-ant-api03-[A-Za-z0-9_\-]+'
REPLACEMENT = 'YOUR_ANTHROPIC_API_KEY_HERE'

# 현재 파일 수정
for f in TARGET_FILES:
    path = os.path.join(r'C:\Users\Mario\work\invest-sns', f)
    if os.path.exists(path):
        with open(path, encoding='utf-8') as fp:
            content = fp.read()
        new_content = re.sub(PATTERN, REPLACEMENT, content)
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as fp:
                fp.write(new_content)
            print(f'Fixed: {f}')
        else:
            print(f'No change: {f}')

print('Done')
