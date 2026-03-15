import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import anthropic
import json
import os
import glob
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('.env.local')

client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
MODEL = "claude-sonnet-4-6"

# Read prompts
v10_8 = Path('prompts/pipeline_v10_backup.md').read_text(encoding='utf-8')
v10_9 = Path('prompts/pipeline_v10.md').read_text(encoding='utf-8')

# Select 5 diverse VTT files
selected = [
    '4wCO1fdl9iU.ko.vtt',  # shortest
]

# Find wsaj files by keyword
all_vtt = glob.glob('subs/*.ko.vtt')
all_vtt = [f for f in all_vtt if 'orig' not in f]

keywords = {'Amazon': None, 'Nvidia': None, 'Meta': None, 'Tesla': None, 'IPO': None}
for f in all_vtt:
    for kw in keywords:
        if kw.lower() in f.lower() and keywords[kw] is None:
            keywords[kw] = os.path.basename(f)

for kw, fname in keywords.items():
    if fname and len(selected) < 5:
        selected.append(fname)

print(f"Selected {len(selected)} files:")
for f in selected:
    sz = os.path.getsize(f'subs/{f}')
    print(f"  {f} ({sz:,} bytes)")

def run_extraction(prompt, subtitle_text, video_title):
    resp = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"{prompt}\n\n---\n\n## ?곸긽 ?쒕ぉ: {video_title}\n\n## ?먮쭑:\n{subtitle_text}"
        }]
    )
    return resp.content[0].text

NON_STOCK_TICKERS = {'BTC', 'ETH', 'XRP', 'SOL', 'DOGE', 'ADA', 'DOT', 'AVAX', 'MATIC', 'LINK'}
NON_STOCK_NAMES = ['鍮꾪듃肄붿씤', '?대뜑由ъ?', '由ы뵆', '?붾씪??, '?꾩?肄붿씤', '湲?, '?', '?먯쑀', '?щ윭', '?뷀솕', '?좊줈']

def analyze_response(raw_text):
    """Parse and analyze a response"""
    # Extract JSON
    try:
        # Try to find JSON in the response
        start = raw_text.find('{')
        end = raw_text.rfind('}') + 1
        if start >= 0 and end > start:
            data = json.loads(raw_text[start:end])
        else:
            return {'signals': [], 'parse_error': True}
    except json.JSONDecodeError:
        return {'signals': [], 'parse_error': True}
    
    signals = data.get('signals', [])
    
    non_stock_count = 0
    long_quote_count = 0
    
    for s in signals:
        # Check non-stock
        ticker = (s.get('ticker') or '').upper()
        stock = s.get('stock', '')
        if ticker in NON_STOCK_TICKERS or any(ns in stock for ns in NON_STOCK_NAMES):
            non_stock_count += 1
        # Check key_quote length
        kq = s.get('key_quote', '')
        if len(kq) > 200:
            long_quote_count += 1
    
    return {
        'signals': signals,
        'count': len(signals),
        'non_stock': non_stock_count,
        'long_quote': long_quote_count,
        'parse_error': False
    }

results = []

for fname in selected:
    print(f"\n{'='*60}")
    print(f"Processing: {fname}")
    
    sub_text = Path(f'subs/{fname}').read_text(encoding='utf-8')
    # Truncate if too long (keep first 80K chars)
    if len(sub_text) > 80000:
        sub_text = sub_text[:80000]
    
    title = fname.replace('.ko.vtt', '').replace('wsaj_', '')
    
    print(f"  Running V10.8...")
    raw_v8 = run_extraction(v10_8, sub_text, title)
    time.sleep(1)
    
    print(f"  Running V10.9...")
    raw_v9 = run_extraction(v10_9, sub_text, title)
    time.sleep(1)
    
    a8 = analyze_response(raw_v8)
    a9 = analyze_response(raw_v9)
    
    results.append({
        'file': fname,
        'v8_raw': raw_v8,
        'v9_raw': raw_v9,
        'v8': a8,
        'v9': a9,
    })
    
    print(f"  V10.8: {a8['count']} signals, {a8['non_stock']} non-stock, {a8['long_quote']} long quotes")
    print(f"  V10.9: {a9['count']} signals, {a9['non_stock']} non-stock, {a9['long_quote']} long quotes")

# Generate report
os.makedirs('data', exist_ok=True)

total_v8 = sum(r['v8']['count'] for r in results)
total_v9 = sum(r['v9']['count'] for r in results)
total_ns_v8 = sum(r['v8']['non_stock'] for r in results)
total_ns_v9 = sum(r['v9']['non_stock'] for r in results)
total_lq_v8 = sum(r['v8']['long_quote'] for r in results)
total_lq_v9 = sum(r['v9']['long_quote'] for r in results)

report = f"""# V10.8 vs V10.9 A/B ?뚯뒪??寃곌낵

?뚯뒪???쇱떆: 2026-03-04
紐⑤뜽: {MODEL}
?뚯뒪???먮쭑: {len(selected)}媛?

## ?붿빟

| ??ぉ | V10.8 | V10.9 |
|------|-------|-------|
| 珥??쒓렇??| {total_v8} | {total_v9} |
| 鍮꾩쥌紐??ы븿 (?뷀샇?뷀룓/?먯옄???? | {total_ns_v8} | {total_ns_v9} |
| key_quote 200??珥덇낵 | {total_lq_v8} | {total_lq_v9} |

## V10.9 二쇱슂 蹂寃쎌궗???곸슜 ?щ?

### 1. 鍮꾩쥌紐??꾪꽣留?(?뷀샇?뷀룓, 湲? ?먯옄????
- V10.8: {total_ns_v8}媛?鍮꾩쥌紐??쒓렇???앹꽦
- V10.9: {total_ns_v9}媛?鍮꾩쥌紐??쒓렇???앹꽦
- **{'??媛쒖꽑?? if total_ns_v9 < total_ns_v8 else '?좑툘 李⑥씠 ?놁쓬' if total_ns_v9 == total_ns_v8 else '???낇솕'}**

### 2. key_quote 200???쒗븳
- V10.8: {total_lq_v8}媛?珥덇낵
- V10.9: {total_lq_v9}媛?珥덇낵
- **{'??媛쒖꽑?? if total_lq_v9 < total_lq_v8 else '?좑툘 李⑥씠 ?놁쓬' if total_lq_v9 == total_lq_v8 else '???낇솕'}**

### 3. confidence 4 ?댄븯 ?쒖쇅 (V10.9 ?좉퇋)
"""

for r in results:
    low_conf_v8 = len([s for s in r['v8']['signals'] if isinstance(s.get('confidence'), (int, float)) and s['confidence'] <= 4])
    low_conf_v9 = len([s for s in r['v9']['signals'] if isinstance(s.get('confidence'), (int, float)) and s['confidence'] <= 4])
    report += f"- {r['file']}: V10.8={low_conf_v8}媛?low-conf, V10.9={low_conf_v9}媛?low-conf\n"

report += "\n### 4. 1?곸긽 1醫낅ぉ 1?쒓렇??n"
for r in results:
    for ver, key in [('V10.8', 'v8'), ('V10.9', 'v9')]:
        stocks = {}
        for s in r[key]['signals']:
            st = s.get('stock', 'unknown')
            stocks[st] = stocks.get(st, 0) + 1
        dupes = {k: v for k, v in stocks.items() if v > 1}
        if dupes:
            report += f"- ??{r['file']} ({ver}): 以묐났 - {dupes}\n"

report += "\n"

# Per-file details
for i, r in enumerate(results):
    report += f"""
---

## ?먮쭑 {i+1}: {r['file']}

### V10.8 寃곌낵 ({r['v8']['count']}媛??쒓렇??

```json
{json.dumps(r['v8']['signals'], ensure_ascii=False, indent=2)}
```

### V10.9 寃곌낵 ({r['v9']['count']}媛??쒓렇??

```json
{json.dumps(r['v9']['signals'], ensure_ascii=False, indent=2)}
```

### 李⑥씠??遺꾩꽍
- ?쒓렇???? V10.8={r['v8']['count']} vs V10.9={r['v9']['count']}
- 鍮꾩쥌紐? V10.8={r['v8']['non_stock']} vs V10.9={r['v9']['non_stock']}
- key_quote 200??珥덇낵: V10.8={r['v8']['long_quote']} vs V10.9={r['v9']['long_quote']}

### V10.8 API ?먮Ц ?묐떟

```
{r['v8_raw']}
```

### V10.9 API ?먮Ц ?묐떟

```
{r['v9_raw']}
```
"""

Path('data/v10_ab_test_report.md').write_text(report, encoding='utf-8')
print(f"\n??Report saved to data/v10_ab_test_report.md")

