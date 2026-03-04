# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/orlando_kim_videos.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

videos = []
for l in lines:
    parts = l.split('|')
    if len(parts) >= 2:
        vid = parts[0]
        title = parts[1]
        date = parts[2] if len(parts) > 2 else 'NA'
        dur = parts[3] if len(parts) > 3 else 'NA'
        videos.append({'id': vid, 'title': title, 'date': date, 'duration': dur})

# Save titles for batch filtering
with open('data/orlando_titles_batch.txt', 'w', encoding='utf-8') as f:
    for i, v in enumerate(videos):
        f.write(f"{i+1}. [{v['id']}] {v['title']}\n")

print(f'Saved {len(videos)} titles')

# Count by prefix pattern
from collections import Counter
prefixes = []
for v in videos:
    t = v['title']
    if '(' in t and ')' in t:
        prefixes.append(t[t.index('(')+1:t.index(')')])
    else:
        prefixes.append('기타')
c = Counter(prefixes)
for k, v in c.most_common(20):
    print(f'  {k}: {v}')
