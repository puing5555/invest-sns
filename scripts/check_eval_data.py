# -*- coding: utf-8 -*-
import os, sys, json, glob
sys.stdout.reconfigure(encoding='utf-8')

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')

# gemini dryrun 로그 파일 목록
files = sorted(glob.glob(os.path.join(LOG_DIR, 'gemini_dryrun_*.json')))
print(f'gemini dryrun 로그 {len(files)}개:')
for f in files:
    size = os.path.getsize(f)
    print(f'  {os.path.basename(f)}  ({size//1024}KB)')

# 가장 최근 파일 구조 확인
if files:
    with open(files[-1], 'r', encoding='utf-8', errors='replace') as fp:
        try:
            d = json.load(fp)
        except:
            fp.seek(0)
            content = fp.read()
            d = json.loads(content.replace('\x00',''))
    
    if isinstance(d, list):
        print(f'\n최근 파일 항목 수: {len(d)}')
        if d:
            print('첫 항목 키:', list(d[0].keys()) if isinstance(d[0], dict) else type(d[0]))
            if isinstance(d[0], dict):
                print(json.dumps(d[0], ensure_ascii=False, indent=2)[:500])
    elif isinstance(d, dict):
        print('키:', list(d.keys()))
