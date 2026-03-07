import json
with open('naver_news.json', encoding='utf-8') as f:
    data = json.load(f)
for d in ['20250305', '20250306']:
    print(f'=== {d} ({len(data[d])} articles) ===')
    for i, n in enumerate(data[d][:20], 1):
        print(f'  {i}. {n["title"]}')
