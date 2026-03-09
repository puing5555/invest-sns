import json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open('public/disclosure_seed.json', encoding='utf-8'))
total = len(data)
with_v = sum(1 for d in data if d.get('verdict'))
grades = collections.Counter(d.get('grade') for d in data if d.get('grade'))
types = collections.Counter(d.get('disclosure_type') for d in data if d.get('disclosure_type'))
print(f'전체: {total}건 | verdict 있음: {with_v}건 | 없음: {total-with_v}건')
print(f'등급: {dict(grades)}')
print(f'유형: {dict(types.most_common(8))}')

# 샘플: B등급 이상 우선
sample = next((d for d in data if d.get('verdict') and d.get('grade') in ('A','B')), None)
if not sample:
    sample = next((d for d in data if d.get('verdict')), None)
if sample:
    print()
    print('=== 샘플 AI 분석 ===')
    for k in ['corp_name','grade','verdict','verdict_tone','what','so_what','now_what_holding','now_what_not_holding','risk','size_assessment','percentile','tags']:
        val = sample.get(k, '')
        print(f'{k}: {val}')
    print()
    print('so_what_data:', json.dumps(sample.get('so_what_data'), ensure_ascii=False))
    print('key_date:', sample.get('key_date'))
