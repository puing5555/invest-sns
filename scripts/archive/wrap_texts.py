import re, os, textwrap

def extract_vtt(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
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
out_dir = r'C:\Users\Mario\work\invest-sns\texts2'
os.makedirs(out_dir, exist_ok=True)

files = [f for f in os.listdir(subs_dir) if f.endswith('.vtt') and not f.endswith('-orig.vtt')]
files.sort()

for f in files:
    try:
        path = os.path.join(subs_dir, f)
        text = extract_vtt(path)
        video_id = f.replace('.ko.vtt','')
        safe_id = re.sub(r'[^\w\-]', '_', video_id)[:80]
        out_path = os.path.join(out_dir, f'{safe_id}.txt')
        # Wrap text at 200 chars
        wrapped = textwrap.fill(text, width=200)
        with open(out_path, 'w', encoding='utf-8') as fo:
            fo.write(f'VIDEO_ID: {video_id}\nLEN: {len(text)}\n\n')
            fo.write(wrapped)
        print(f'OK: {safe_id}')
    except Exception as e:
        print(f'ERROR: {f}: {e}')
