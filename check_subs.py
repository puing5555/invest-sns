import json, os

subs_dir = r'C:\Users\Mario\work\subs'
for f in sorted(os.listdir(subs_dir)):
    if not f.endswith('.json'):
        continue
    with open(os.path.join(subs_dir, f), 'r', encoding='utf-8') as fh:
        d = json.load(fh)
    subs = d.get('subtitles', d.get('segments', []))
    vid = d.get('video_id', '?')
    ch = d.get('channel', '?')
    title = d.get('title', '(no title)')[:60]
    # Get first line of text
    first = subs[0].get('text', '')[:40] if subs else ''
    print(f"{f}: vid={vid} ch={ch} segs={len(subs)} | {title} | {first}")
