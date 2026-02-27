import json
data = json.load(open('C:/Users/Mario/work/invest-sns/subs/syuka_30.json', encoding='utf-8-sig'))
for i, e in enumerate(data.get('entries', []), 1):
    print(f"{i:2d}. {e['id']} --- {e.get('title','?')}")
