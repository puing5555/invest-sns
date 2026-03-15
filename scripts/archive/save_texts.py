import re, os, json

def extract_vtt(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    lines = content.split('\n')
    text, prev = [], ''
    timestamps = []
    for line in lines:
        line_stripped = line.strip()
        # Capture timestamps
        if '-->' in line_stripped:
            ts = line_stripped.split('-->')[0].strip()
            timestamps.append(ts)
            continue
        if not line_stripped or re.match(r'^\d+$', line_stripped): continue
        if any(line_stripped.startswith(x) for x in ['WEBVTT','NOTE','Kind','Language']): continue
        clean = re.sub(r'<[^>]+>', '', line_stripped).strip()
        if clean and clean != prev:
            text.append(clean)
            prev = clean
    return ' '.join(text)

subs_dir = r'C:\Users\Mario\work\invest-sns\subs'
out_dir = r'C:\Users\Mario\work\invest-sns\texts'
os.makedirs(out_dir, exist_ok=True)

files = [f for f in os.listdir(subs_dir) if f.endswith('.vtt') and not f.endswith('-orig.vtt')]
files.sort()

for f in files:
    try:
        path = os.path.join(subs_dir, f)
        text = extract_vtt(path)
        video_id = f.replace('.ko.vtt','')
        # Clean filename for saving
        safe_id = re.sub(r'[^\w\-]', '_', video_id)[:80]
        out_path = os.path.join(out_dir, f'{safe_id}.txt')
        with open(out_path, 'w', encoding='utf-8') as fo:
            fo.write(f'VIDEO_ID: {video_id}\n')
            fo.write(f'LEN: {len(text)}\n\n')
            fo.write(text)
        print(f'OK: {safe_id} ({len(text)} chars)')
    except Exception as e:
        print(f'ERROR: {f}: {e}')
