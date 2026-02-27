import json, glob, os

files = glob.glob('C:/Users/Mario/work/invest-sns/subs/*.json')
for f in sorted(files):
    if 'playlist' in os.path.basename(f) or 'parse' in os.path.basename(f):
        continue
    name = os.path.basename(f).replace('.json','')
    try:
        data = json.load(open(f, encoding='utf-8-sig'))
        entries = data.get('entries', [])
        print(f"\n=== {name} ({len(entries)} videos) ===")
        for e in entries:
            print(f"  {e['id']} --- {e.get('title','?')}")
    except Exception as ex:
        print(f"  ERROR: {ex}")
