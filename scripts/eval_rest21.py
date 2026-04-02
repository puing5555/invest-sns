# -*- coding: utf-8 -*-
"""eval_rest21.py - V11.5 vs V12 비교 (6~26번째 영상, 21개)"""
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

def get_videos():
    r = requests.get(
        f'{URL}/rest/v1/influencer_videos'
        f'?select=id,video_id,title,duration_seconds,channel_id,subtitle_text'
        f'&signal_count=gt.0&subtitle_text=not.is.null'
        f'&order=published_at.desc&limit=26',
        headers=H)
    videos = r.json()
    ch_r = requests.get(f'{URL}/rest/v1/influencer_channels?select=id,channel_name', headers=H)
    ch   = {c['id']: c['channel_name'] for c in ch_r.json()}
    for v in videos:
        v['channel_name'] = ch.get(v['channel_id'], '?')
    return videos[5:]  # 6번째부터 (앞 5개는 이미 완료)

def get_gt(db_id):
    r = requests.get(f'{URL}/rest/v1/influencer_signals?select=stock,signal&video_id=eq.{db_id}', headers=H)
    data = r.json()
    if not isinstance(data, list): return []
    return [{'stock': s['stock'], 'signal_type': s['signal']} for s in data if isinstance(s, dict)]

def build_prompt(path, video):
    tmpl = path.read_text(encoding='utf-8')
    sub  = video.get('subtitle_text', '')
    if len(sub) > 40000: sub = sub[:40000] + '\n...(생략)'
    dur  = video.get('duration_seconds', 0)
    dur_str = f'{dur//60}분 {dur%60}초' if dur else '알 수 없음'
    header = (f'[EVAL MODE - 자막 기반]\n영상 제목: {video.get("title","")}\n'
              f'영상 길이: {dur_str}\n채널: {video.get("channel_name","")}\n\n'
              f'=== 자막 ===\n{sub}\n=== 자막 끝 ===\n\n위 자막을 분석하여 시그널을 추출하세요:\n\n')
    p = header + tmpl
    p = p.replace('{VIDEO_DURATION_INFO}', dur_str).replace('{CHANNEL_URL}', '')
    return p

def call_claude(prompt, label=''):
    client = anthropic.Anthropic(api_key=AKEY)
    for attempt in range(1, 4):
        try:
            msg = client.messages.create(
                model=MODEL, max_tokens=4096, temperature=0,
                messages=[{'role':'user','content': prompt + '\n\nJSON만 출력: {"signals":[...]}'}])
            raw = msg.content[0].text.strip()
            for pat in [r'```json\s*(.*?)\s*```', r'(\{.*\})', None]:
                try:
                    text = re.search(pat, raw, re.DOTALL).group(1) if pat else raw
                    sigs = json.loads(text).get('signals', [])
                    return [s for s in sigs if isinstance(s,dict) and s.get('signal_type') in VALID]
                except: pass
            log(f'[JSON_FAIL] {label}'); return []
        except anthropic.RateLimitError:
            log(f'[RATE_LIMIT] 30초 대기...'); time.sleep(30)
        except Exception as e:
            log(f'[ERR] {e}')
            if attempt < 3: time.sleep(5)
    return []

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
    return dict(correct=correct, total=len(gt_map), acc=correct/len(gt_map) if gt_map else None,
                wrong=wrong, over=over, under=under)

# ── 5개 테스트 결과 (이미 완료) ─────────────────────────────────────────────
prev = [
    # (video_id, gt_total, v115_correct, v115_pred, v12_correct, v12_pred)
    ('IjYr0FrINis', 0, 0, 3, 0, 3),
    ('kFa9RxL4HnA', 2, 2, 2, 2, 3),
    ('x0TKvrIdIwI', 3, 1, 6, 2, 3),
    ('I4Tt3tevuTU', 1, 0, 5, 0, 3),
    ('5mvn3PfKf9Y', 1, 0, 4, 0, 4),
]

# ── MAIN ────────────────────────────────────────────────────────────────────────
print('=' * 60)
print(f'모델: {MODEL}  |  나머지 21개 (6~26번)')
print('=' * 60)

videos = get_videos()
print(f'영상 수: {len(videos)}개\n')

for i, v in enumerate(videos, 1):
    v['gt'] = get_gt(v['id'])

results = []

# V11.5 실행
print(f'{"="*60}\n▶ V11.5 (21개)\n{"="*60}')
for i, v in enumerate(videos, 1):
    print(f'\n[{i+5}/26] {v["video_id"]} | {v["title"][:40]}')
    t0 = time.time()
    sigs = call_claude(build_prompt(PROMPT_V115, v), f'V115/{v["video_id"]}')
    elapsed = time.time() - t0
    cmp = compare(v['gt'], sigs)
    print(f'  {elapsed:.0f}초 | GT:{cmp["total"]} | 정확:{cmp["correct"]} | 추출:{len(sigs)}')
    for s in sigs: print(f'    [{s.get("signal_type")}] {s.get("stock")} (conf={s.get("confidence")})')
    results.append({'video': v, 'v115_sigs': sigs, 'v115_cmp': cmp})
    if i % 5 == 0:
        print(f'\n  [배치 완료] 10초 대기...')
        time.sleep(10)
    elif i < len(videos): time.sleep(2)

# V12 실행
print(f'\n{"="*60}\n▶ V12 (21개)\n{"="*60}')
for i, (v, r) in enumerate(zip(videos, results), 1):
    print(f'\n[{i+5}/26] {v["video_id"]} | {v["title"][:40]}')
    t0 = time.time()
    sigs = call_claude(build_prompt(PROMPT_V12, v), f'V12/{v["video_id"]}')
    elapsed = time.time() - t0
    cmp = compare(v['gt'], sigs)
    print(f'  {elapsed:.0f}초 | GT:{cmp["total"]} | 정확:{cmp["correct"]} | 추출:{len(sigs)}')
    for s in sigs: print(f'    [{s.get("signal_type")}] {s.get("stock")} (conf={s.get("confidence")})')
    r['v12_sigs'] = sigs; r['v12_cmp'] = cmp
    if i % 5 == 0:
        print(f'\n  [배치 완료] 10초 대기...')
        time.sleep(10)
    elif i < len(videos): time.sleep(2)

# ── 전체 집계 (5개 + 21개) ─────────────────────────────────────────────────────
print(f'\n{"="*60}')
print('▶ 전체 26개 최종 집계')
print('=' * 60)

# 21개 집계
gt21   = sum(r['v115_cmp']['total']   for r in results)
c115_21= sum(r['v115_cmp']['correct'] for r in results)
c12_21 = sum(r['v12_cmp']['correct']  for r in results)

# 5개 + 21개 합산
gt_total  = 7  + gt21
tot115    = 3  + c115_21
tot12     = 4  + c12_21
acc115    = tot115/gt_total if gt_total else 0
acc12     = tot12 /gt_total if gt_total else 0

print(f'\n[21개 추가분]')
print(f'  V11.5: {c115_21}/{gt21}')
print(f'  V12:   {c12_21}/{gt21}')

print(f'\n[전체 26개 합산]')
print(f'  총 GT: {gt_total}건')
print(f'  V11.5 정확도: {acc115:.1%} ({tot115}/{gt_total})')
print(f'  V12  정확도: {acc12:.1%}  ({tot12}/{gt_total})')
print(f'  개선: {"+" if acc12>=acc115 else ""}{(acc12-acc115):.1%}')

print(f'\n[21개 오분류 상세]')
print('V11.5:')
for r in results:
    for stock, gt_s, p_s in r['v115_cmp']['wrong']:
        print(f'  {r["video"]["video_id"]} | {stock}: GT={gt_s} → {p_s}')
print('V12:')
for r in results:
    for stock, gt_s, p_s in r['v12_cmp']['wrong']:
        print(f'  {r["video"]["video_id"]} | {stock}: GT={gt_s} → {p_s}')

print('\n완료.')
