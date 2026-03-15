import re, os, json

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

# Save to file
out_path = r'C:\Users\Mario\work\invest-sns\vtt_extracted.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Saved {len(results)} files to {out_path}")
for vid_id in list(results.keys())[:5]:
    print(f"\n=== {vid_id} ===")
    print(results[vid_id][:300])
