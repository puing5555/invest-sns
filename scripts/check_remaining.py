import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
data = json.load(open('wsaj_remaining_results.json', 'r', encoding='utf-8'))
for item in data:
    sigs = item.get('signals', [])
    vid = item['video_id']
    title = item['video_title'][:50]
    print(f"{vid} | {len(sigs)} sigs | {title}")
    for s in sigs:
        print(f"  -> {s['stock']} ({s['ticker']}) {s['signal_type']} @{s['timestamp']} conf={s.get('confidence','-')}")
        print(f"     quote: {s['key_quote'][:60]}")
