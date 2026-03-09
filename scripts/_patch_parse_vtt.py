#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch parse_vtt() in godofIT_analyze.py"""

import re

FILE = r'C:\Users\Mario\work\invest-sns\scripts\godofIT_analyze.py'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the parse_vtt function boundaries
idx = content.find('def parse_vtt(')
if idx == -1:
    print('ERROR: parse_vtt not found')
    exit(1)

# Find next function definition
end_idx = content.find('\ndef ', idx + 1)
if end_idx == -1:
    print('ERROR: could not find end of parse_vtt')
    exit(1)

old_func = content[idx:end_idx]
print('Found old function:')
print(old_func[:100])
print('...')

new_func = '''def parse_vtt(vtt_path, include_timestamps=True):
    """
    VTT 자막 파일 파싱
    include_timestamps=True: 타임코드 포함 (시그널 분석용) - 기본값
    include_timestamps=False: 텍스트만 (레거시)
    """
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if include_timestamps:
        # 타임코드 포함 버전: "[00:05:30] 발언내용" 형태
        lines_out = []
        current_ts = None
        for line in content.split('\\n'):
            line = line.strip()
            if not line or line.startswith('WEBVTT') or line.startswith('NOTE') or line.startswith('Kind:') or line.startswith('Language:'):
                continue
            # 타임코드 라인 캡처 (00:05:30.000 --> 00:05:35.000)
            ts_match = re.match(r'(\\d{2}:\\d{2}:\\d{2})\\.\\d+ -->', line)
            if ts_match:
                current_ts = ts_match.group(1)
                continue
            if re.match(r'^\\d+$', line):
                continue
            clean = re.sub(r'<[^>]+>', '', line).strip()
            if clean:
                if current_ts:
                    lines_out.append(f'[{current_ts}] {clean}')
                    current_ts = None
                else:
                    lines_out.append(clean)
        # 중복 제거
        deduped = []
        prev = None
        for l in lines_out:
            if l != prev:
                deduped.append(l)
            prev = l
        return '\\n'.join(deduped[:4000])
    else:
        # 기존 방식 (텍스트만)
        lines = []
        for line in content.split('\\n'):
            line = line.strip()
            if not line or line.startswith('WEBVTT') or line.startswith('NOTE') or line.startswith('Kind:') or line.startswith('Language:'):
                continue
            if '-->' in line:
                continue
            if re.match(r'^\\d+$', line):
                continue
            line = re.sub(r'<[^>]+>', '', line)
            if line:
                lines.append(line)
        deduped = []
        prev = None
        for l in lines:
            if l != prev:
                deduped.append(l)
            prev = l
        return ' '.join(deduped[:3000])'''

new_content = content[:idx] + new_func + content[end_idx:]

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(new_content)

print('OK: parse_vtt updated successfully')
print(f'Old length: {len(old_func)}, New length: {len(new_func)}')
