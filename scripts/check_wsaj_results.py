import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for f in ['wsaj_all_results.json', 'wsaj_signals_analysis.json', 'wsaj_partial_results.json', 'tesla_analysis.json']:
    if not os.path.exists(f):
        print(f"{f}: NOT FOUND")
        continue
    d = json.load(open(f, 'r', encoding='utf-8'))
    if isinstance(d, list):
        print(f"{f}: list, {len(d)} items")
        for item in d:
            print(json.dumps(item, ensure_ascii=False, indent=2)[:400])
            print("---")
    elif isinstance(d, dict):
        print(f"{f}: dict")
        print(json.dumps(d, ensure_ascii=False, indent=2)[:800])
    print("===")
