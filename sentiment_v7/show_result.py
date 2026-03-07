import json

with open('today_result.json', 'r', encoding='utf-8') as f:
    r = json.load(f)

print(f"오늘 ({r['date']}): {r['score']}점 [{r['grade']}] - {r['available_count']}개 지표")
for k, v in r['components'].items():
    bar = '#' * int(v['score']/5)
    print(f"  {k:12s} {v['score']:5.1f} {bar}")
print(f"스킵: {r['skipped']}")
