# -*- coding: utf-8 -*-
"""
eval_test5.py - V11.5 vs V12 비교 (5개 테스트)
"""
import sys, os, json, time, re, requests
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / '.env.local')

import anthropic

URL  = os.environ['NEXT_PUBLIC_SUPABASE_URL']
KEY  = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
AKEY = os.environ['ANTHROPIC_API_KEY']
H    = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Accept': 'application/json'}

MODEL       = 'claude-haiku-4-5-20251001'
VALID       = {'매수','긍정','중립','부정','매도'}
PROMPT_V115 = ROOT / 'prompts' / 'pipeline_v11.5.md'
PROMPT_V12  = ROOT / 'prompts' / 'pipeline_v12.md'

def log(msg): print(f'  {msg}', flush=True)

# ── 데이터 로드 ────────────────────────────────────────────────────────────────
def get_videos(n=5):
    r = requests.get(
        f'{URL}/rest/v1/influencer_videos'
        f'?select=id,video_id,title,duration_seconds,channel_id,subtitle_text'
        f'&signal_count=gt.0&subtitle_text=not.is.null'
        f'&order=published_at.desc&limit={n}',
        headers=H)
    videos = r.json()
    ch_r = requests.get(f'{URL}/rest/v1/influencer_channels?select=id,channel_name', headers=H)
    ch   = {c['id']: c['channel_name'] for c in ch_r.json()}
    for v in videos:
        v['channel_name'] = ch.get(v['channel_id'], '?')
    return videos

def get_gt(db_id):
    r = requests.get(
        f'{URL}/rest/v1/influencer_signals?select=stock,signal&video_id=eq.{db_id}',
        headers=H)
    data = r.json()
    if not isinstance(data, list): return []
    return [{'stock': s['stock'], 'signal_type': s['signal']} for s in data if isinstance(s, dict)]

# ── 프롬프트 빌드 ──────────────────────────────────────────────────────────────
def build_prompt(path, video):
    tmpl = path.read_text(encoding='utf-8')
    sub  = video.get('subtitle_text', '')
    if len(sub) > 40000: sub = sub[:40000] + '\n...(생략)'
    dur  = video.get('duration_seconds', 0)
    dur_str = f'{dur//60}분 {dur%60}초' if dur else '알 수 없음'
    header = (
        f'[EVAL MODE - 자막 기반]\n'
        f'영상 제목: {video.get("title","")}\n'
        f'영상 길이: {dur_str}\n'
        f'채널: {video.get("channel_name","")}\n\n'
        f'=== 자막 ===\n{sub}\n=== 자막 끝 ===\n\n'
        f'위 자막을 분석하여 시그널을 추출하세요:\n\n'
    )
    p = header + tmpl
    p = p.replace('{VIDEO_DURATION_INFO}', dur_str)
    p = p.replace('{CHANNEL_URL}', '')
    return p

# ── Claude 호출 ────────────────────────────────────────────────────────────────
def call_claude(prompt, label=''):
    client = anthropic.Anthropic(api_key=AKEY)
    for attempt in range(1, 4):
        try:
            msg = client.messages.create(
                model=MODEL, max_tokens=4096, temperature=0,
                messages=[{'role':'user','content': prompt + '\n\nJSON만 출력: {"signals":[...]}'}])
            raw = msg.content[0].text.strip()
            # JSON 파싱
            for pat in [r'```json\s*(.*?)\s*```', r'(\{.*\})', None]:
                try:
                    text = re.search(pat, raw, re.DOTALL).group(1) if pat else raw
                    parsed = json.loads(text)
                    sigs = parsed.get('signals', [])
                    return [s for s in sigs if isinstance(s,dict) and s.get('signal_type') in VALID]
                except: pass
            log(f'[JSON_FAIL] {label}')
            return []
        except anthropic.RateLimitError:
            log(f'[RATE_LIMIT] 30초 대기...')
            time.sleep(30)
        except Exception as e:
            log(f'[ERR] {e}')
            if attempt < 3: time.sleep(5)
    return []

# ── 비교 ────────────────────────────────────────────────────────────────────────
def compare(gt, pred):
    gt_map   = {s['stock'].strip(): s['signal_type'] for s in gt}
    pred_map = {s['stock'].strip(): s.get('signal_type','') for s in pred}
    correct, wrong, over, under = 0, [], [], []
    for stock, gt_sig in gt_map.items():
        if stock in pred_map:
            if pred_map[stock] == gt_sig: correct += 1
            else: wrong.append((stock, gt_sig, pred_map[stock]))
        else: under.append((stock, gt_sig))
    for stock, p_sig in pred_map.items():
        if stock not in gt_map: over.append((stock, p_sig))
    acc = correct/len(gt_map) if gt_map else None
    return dict(correct=correct, total=len(gt_map), acc=acc,
                wrong=wrong, over=over, under=under)

# ── MAIN ────────────────────────────────────────────────────────────────────────
print('=' * 60)
print(f'모델: {MODEL}  |  테스트: 5개 영상')
print('=' * 60)

videos = get_videos(5)
print(f'\n[영상 목록]')
for i, v in enumerate(videos, 1):
    gt = get_gt(v['id'])
    v['gt'] = gt
    print(f'  {i}. {v["video_id"]} | {v["title"][:35]} | GT {len(gt)}건')

results = []

# V11.5 실행
print(f'\n{"="*60}\n▶ V11.5 실행\n{"="*60}')
for i, v in enumerate(videos, 1):
    print(f'\n[{i}/5] {v["video_id"]} — {v["title"][:40]}')
    t0 = time.time()
    sigs = call_claude(build_prompt(PROMPT_V115, v), f'V11.5/{v["video_id"]}')
    elapsed = time.time() - t0
    cmp = compare(v['gt'], sigs)
    print(f'  소요: {elapsed:.0f}초 | 추출: {len(sigs)}건 | GT: {cmp["total"]}건 | 정확: {cmp["correct"]}건')
    for s in sigs: print(f'    [{s.get("signal_type")}] {s.get("stock")} (conf={s.get("confidence")})')
    results.append({'video': v, 'v115_sigs': sigs, 'v115_cmp': cmp})
    if i < 5: time.sleep(2)

# V12 실행
print(f'\n{"="*60}\n▶ V12 실행\n{"="*60}')
for i, (v, r) in enumerate(zip(videos, results), 1):
    print(f'\n[{i}/5] {v["video_id"]} — {v["title"][:40]}')
    t0 = time.time()
    sigs = call_claude(build_prompt(PROMPT_V12, v), f'V12/{v["video_id"]}')
    elapsed = time.time() - t0
    cmp = compare(v['gt'], sigs)
    print(f'  소요: {elapsed:.0f}초 | 추출: {len(sigs)}건 | GT: {cmp["total"]}건 | 정확: {cmp["correct"]}건')
    for s in sigs: print(f'    [{s.get("signal_type")}] {s.get("stock")} (conf={s.get("confidence")})')
    r['v12_sigs'] = sigs
    r['v12_cmp'] = cmp
    if i < 5: time.sleep(2)

# 비교표
print(f'\n{"="*60}')
print('▶ GT vs V11.5 vs V12 비교표')
print('=' * 60)

total_gt = sum(r['v115_cmp']['total'] for r in results)
tot115   = sum(r['v115_cmp']['correct'] for r in results)
tot12    = sum(r['v12_cmp']['correct'] for r in results)
acc115   = tot115/total_gt if total_gt else 0
acc12    = tot12/total_gt  if total_gt else 0

print(f'\n| {"영상":18} | GT | V11.5 정확/예측 | V12 정확/예측 |')
print(f'|{"-"*20}|{"-"*4}|{"-"*17}|{"-"*15}|')
for r in results:
    v   = r['video']
    c115= r['v115_cmp']
    c12 = r['v12_cmp']
    print(f'| {v["video_id"]:18} | {c115["total"]:2} | {c115["correct"]:2}/{len(r["v115_sigs"]):2}            | {c12["correct"]:2}/{len(r["v12_sigs"]):2}          |')

print(f'\n총 GT: {total_gt}건')
print(f'V11.5 정확도: {acc115:.1%} ({tot115}/{total_gt})')
print(f'V12  정확도: {acc12:.1%}  ({tot12}/{total_gt})')
print(f'개선: {"+" if acc12>=acc115 else ""}{(acc12-acc115):.1%}')

# 오분류 상세
print(f'\n▶ V11.5 오분류')
for r in results:
    for stock, gt_s, p_s in r['v115_cmp']['wrong']:
        print(f'  {r["video"]["video_id"]} | {stock}: GT={gt_s} → 예측={p_s}')
if not any(r['v115_cmp']['wrong'] for r in results): print('  없음')

print(f'\n▶ V12 오분류')
for r in results:
    for stock, gt_s, p_s in r['v12_cmp']['wrong']:
        print(f'  {r["video"]["video_id"]} | {stock}: GT={gt_s} → 예측={p_s}')
if not any(r['v12_cmp']['wrong'] for r in results): print('  없음')

print(f'\n▶ V11.5 과잉추출 (GT에 없는 종목)')
for r in results:
    for stock, p_s in r['v115_cmp']['over']:
        print(f'  {r["video"]["video_id"]} | {stock}: {p_s}')
if not any(r['v115_cmp']['over'] for r in results): print('  없음')

print(f'\n▶ V12 과잉추출')
for r in results:
    for stock, p_s in r['v12_cmp']['over']:
        print(f'  {r["video"]["video_id"]} | {stock}: {p_s}')
if not any(r['v12_cmp']['over'] for r in results): print('  없음')

print('\n완료.')
