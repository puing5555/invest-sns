import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('joungsoo_videos.json','r',encoding='utf-8') as f:
    d = json.load(f)
print(f"Total: {d['total']}, Investment: {d['invest']}, Non: {d['total']-d['invest']}")
print("\n=== Recent 10 investment videos ===")
for v in d['invest_videos'][:10]:
    print(f"[{v['date']}] {v['title']} ({v['id']})")
print(f"\n=== Non-investment sample (of {len(d['non_invest_videos'])}) ===")
for v in d['non_invest_videos'][:5]:
    print(f"[{v['date']}] {v['title']}")
