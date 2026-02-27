import json
data = json.load(open('C:/Users/Mario/work/invest-sns/subs/syuka_playlist.json', encoding='utf-8-sig'))
for e in data.get('entries', []):
    print(f"{e['id']} --- {e.get('title','?')}")
