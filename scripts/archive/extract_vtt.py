import re, os, glob, json

def extract_vtt(path):
    with open(path, 'rb') as f: raw = f.read()
    try:
        content = raw.decode('utf-8')
    except:
        content = raw.decode('utf-8-sig')
    lines = content.split('\n')
    text, prev = [], ''
    for line in lines:
        line = line.strip()
        if not line or '-->' in line or re.match(r'^\d+$', line): continue
        if any(line.startswith(x) for x in ['WEBVTT','NOTE','Kind','Language']): continue
        clean = re.sub(r'<[^>]+>', '', line).strip()
        if clean and clean != prev:
            text.append(clean)
            prev = clean
    return ' '.join(text)

subs_dir = r'C:\Users\Mario\work\invest-sns\subs'
files = [f for f in os.listdir(subs_dir) if f.endswith('.vtt') and not f.endswith('-orig.vtt')]
files.sort()

results = {}
for f in files:
    try:
        path = os.path.join(subs_dir, f)
        text = extract_vtt(path)
        video_id = f.replace('.ko.vtt','')
        results[video_id] = text
    except Exception as e:
        results[f] = f'ERROR: {e}'

# Print first 15 files
for i, (vid, text) in enumerate(list(results.items())[:15]):
    print(f'=== {vid} ===')
    print(text[:500])
    print()

print(f'Total: {len(results)} files')
