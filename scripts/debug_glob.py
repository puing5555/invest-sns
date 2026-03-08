#!/usr/bin/env python3
import glob, os, sys

print('Python:', sys.version)
print('FS encoding:', sys.getfilesystemencoding())
print('stdout encoding:', sys.stdout.encoding)

SUBS_DIR = r'C:\Users\Mario\work\invest-sns\subs'
raw_files = glob.glob(os.path.join(SUBS_DIR, '*.ko.vtt'))
print('Raw glob count:', len(raw_files))

sorted_files = sorted(raw_files)
print('Sorted count:', len(sorted_files))

for i, f in enumerate(sorted_files):
    try:
        bn = os.path.basename(f)
        print(f'  [{i+1}] {repr(bn[:50])}')
    except Exception as e:
        print(f'  [{i+1}] ERROR: {e}')
