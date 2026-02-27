import json
for fname in ['search_booread.json']:
    try:
        data = json.load(open(f'C:/Users/Mario/work/invest-sns/subs/{fname}', encoding='utf-8-sig'))
        entries = data.get('entries', [])
        print(f"=== {fname} ({len(entries)}) ===")
        for e in entries:
            ch = e.get('channel', '?')
            print(f"  {e['id']} [{ch}] --- {e.get('title','?')}")
    except Exception as ex:
        print(f"ERROR {fname}: {ex}")
