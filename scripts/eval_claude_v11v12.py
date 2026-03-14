# -*- coding: utf-8 -*-
"""
eval_claude_v11v12.py
자막 텍스트 기반 V11.5 vs V12 프롬프트 비교 eval — Claude Haiku 4.5
- DB의 subtitle_text를 Claude API에 직접 전달 (영상 시청 없음)
- 최대 40개 영상, 5개씩 배치 처리
- ground truth = DB 기존 시그널
"""
import os, sys, json, time, re, requests
from datetime import datetime
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).parent.parent

from dotenv import load_dotenv
load_dotenv(ROOT / '.env.local')

import anthropic

SUPABASE_URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']

CLAUDE_MODEL = 'claude-haiku-4-5-20251001'
BATCH_SIZE   = 5     # 5개씩 배치
BATCH_DELAY  = 15    # 배치 간 대기(초)
REQ_DELAY    = 2     # 요청 간 딜레이(초)
MAX_VIDEOS   = 26    # 자막+시그널 영상 전체

SB_H = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}', 'Accept': 'application/json'}
VALID_SIGNALS = {'매수', '긍정', '중립', '부정', '매도'}

PROMPT_V115 = ROOT / 'prompts' / 'pipeline_v11.5.md'
PROMPT_V12  = ROOT / 'prompts' / 'pipeline_v12.md'

TS = datetime.now().strftime('%Y%m%d_%H%M')
REPORT_PATH = ROOT / 'data' / f'eval_claude_{TS}.md'
JSON_PATH   = ROOT / 'data' / f'eval_claude_{TS}.json'


def log(msg):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {msg}', flush=True)


# ── Supabase helpers ───────────────────────────────────────────────────────────
def get_eval_videos():
    """자막+시그널 모두 있는 영상 최대 40개"""
    r = requests.get(
        f'{SUPABASE_URL}/rest/v1/influencer_videos'
        f'?select=id,video_id,title,duration_seconds,channel_id,subtitle_text'
        f'&signal_count=gt.0&subtitle_text=not.is.null'
        f'&order=published_at.desc&limit=100',
        headers=SB_H
    )
    videos = r.json()
    # 채널 이름 맵
    ch_r = requests.get(f'{SUPABASE_URL}/rest/v1/influencer_channels?select=id,channel_name', headers=SB_H)
    ch_map = {c['id']: c['channel_name'] for c in ch_r.json()}
    for v in videos:
        v['channel_name'] = ch_map.get(v['channel_id'], '?')
    # MAX_VIDEOS까지만 사용
    selected = videos[:MAX_VIDEOS]
    log(f'eval 대상: {len(selected)}개 (자막+시그널 모두 있는 영상, 최대 {MAX_VIDEOS}개)')
    return selected


def get_ground_truth(video_db_id):
    r = requests.get(
        f'{SUPABASE_URL}/rest/v1/influencer_signals'
        f'?select=stock,ticker,signal&video_id=eq.{video_db_id}',
        headers=SB_H
    )
    data = r.json()
    # DB uses 'signal' column; normalize to 'signal_type' for comparison
    if isinstance(data, list):
        for s in data:
            if isinstance(s, dict) and 'signal' in s:
                s['signal_type'] = s.pop('signal')
        return data
    return []


# ── 프롬프트 빌드 ──────────────────────────────────────────────────────────────
def build_text_prompt(prompt_path: Path, video: dict) -> str:
    prompt = prompt_path.read_text(encoding='utf-8')
    subtitle = video.get('subtitle_text', '')
    if len(subtitle) > 40000:
        subtitle = subtitle[:40000] + '\n...(자막 일부 생략)'

    dur = video.get('duration_seconds', 0)
    dur_str = f'{dur//60}분 {dur%60}초' if dur else '알 수 없음'

    header = f"""[EVAL MODE - 자막 텍스트 기반 분석]
아래는 YouTube 영상의 자막 텍스트입니다. 영상을 직접 보는 대신 이 자막을 기반으로 분석해주세요.

영상 제목: {video.get('title', '')}
영상 길이: {dur_str}
채널: {video.get('channel_name', '')}

=== 자막 텍스트 시작 ===
{subtitle}
=== 자막 텍스트 끝 ===

위 자막을 분석하여 다음 프롬프트 지시에 따라 시그널을 추출하세요:

"""
    # VIDEO_DURATION_INFO 플레이스홀더 처리
    full_prompt = header + prompt
    full_prompt = full_prompt.replace('{VIDEO_DURATION_INFO}', f'영상 길이 {dur_str}')
    full_prompt = full_prompt.replace('{CHANNEL_URL}', '')
    return full_prompt


# ── Claude API 호출 ────────────────────────────────────────────────────────────
def call_claude(prompt_text: str, video_id: str, retry=3) -> list:
    """Claude Haiku 4.5 텍스트 분석"""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    for attempt in range(1, retry + 1):
        try:
            message = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=8192,
                messages=[{
                    "role": "user",
                    "content": prompt_text + '\n\n반드시 JSON 형식으로만 출력하세요: {"signals": [...]}'
                }]
            )
            raw_text = message.content[0].text if message.content else None
            if not raw_text:
                raise ValueError(f"Empty/None text from API (stop_reason={getattr(message, 'stop_reason', '?')})")
            raw = raw_text.strip()

            # JSON 파싱
            parsed = None
            # 1) 직접 파싱
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                pass
            # 2) ```json 블록 추출
            if parsed is None:
                m = re.search(r'```json\s*(.*?)\s*```', raw, re.DOTALL)
                if m:
                    try: parsed = json.loads(m.group(1))
                    except: pass
            # 3) {...} 블록 추출
            if parsed is None:
                m = re.search(r'\{.*\}', raw, re.DOTALL)
                if m:
                    try: parsed = json.loads(m.group(0))
                    except: pass
            # 4) repair
            if parsed is None:
                repaired = raw
                open_b = repaired.count('{') - repaired.count('}')
                open_a = repaired.count('[') - repaired.count(']')
                if open_b > 0: repaired += '}' * open_b
                if open_a > 0: repaired += ']' * open_a
                try: parsed = json.loads(repaired)
                except: pass

            if parsed is None:
                log(f'    [JSON_FAIL] {video_id}, attempt={attempt}')
                if attempt < retry: time.sleep(3); continue
                return []

            signals = parsed.get('signals', [])
            clean = []
            for s in signals:
                st = (s.get('signal_type') or '').strip()
                if st in VALID_SIGNALS:
                    clean.append(s)
                elif st:
                    log(f'    [SKIP] 비정규: {st}')
            return clean

        except anthropic.RateLimitError:
            wait = 30 * attempt
            log(f'  [RATE_LIMIT] {wait}초 대기...')
            time.sleep(wait)
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as e:
            log(f'  [ERR] {type(e).__name__}: {e} (attempt={attempt})')
            if attempt < retry: time.sleep(5)

    return []


# ── 비교 분석 ──────────────────────────────────────────────────────────────────
def compare(gt_signals, pred_signals):
    gt   = {s['stock'].strip(): s['signal_type'] for s in gt_signals if isinstance(s, dict) and s.get('stock')}
    pred = {s['stock'].strip(): s['signal_type'] for s in pred_signals if isinstance(s, dict) and s.get('stock')}
    correct, wrong, over, under = 0, [], [], []
    for stock, gt_type in gt.items():
        if stock in pred:
            if pred[stock] == gt_type: correct += 1
            else: wrong.append({'stock': stock, 'gt': gt_type, 'pred': pred[stock]})
        else:
            under.append({'stock': stock, 'gt_type': gt_type})
    for stock, pred_type in pred.items():
        if stock not in gt:
            over.append({'stock': stock, 'pred_type': pred_type})
    return {
        'correct': correct, 'total_gt': len(gt),
        'accuracy': correct / len(gt) if gt else None,
        'wrong': wrong, 'over': over, 'under': under,
        'pred_count': len(pred),
    }


# ── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    log(f'=== Claude V11.5 vs V12 Eval (자막 텍스트 기반) ===')
    log(f'모델: {CLAUDE_MODEL} | 배치: {BATCH_SIZE}개씩 | 배치간대기: {BATCH_DELAY}초')

    videos = get_eval_videos()
    if not videos:
        log('ERROR: eval 영상 없음')
        return

    log('ground truth 로드...')
    for v in videos:
        v['ground_truth'] = get_ground_truth(v['id'])

    results = []

    # ── V11.5 실행 ──────────────────────────────────────────────────────────────
    log(f'\n=== V11.5 실행 ({len(videos)}개, {BATCH_SIZE}개씩 배치) ===')
    for i, v in enumerate(videos, 1):
        try:
            log(f'  V11.5 [{i}/{len(videos)}] {v["video_id"]} | {v["title"][:40]}')
            prompt = build_text_prompt(PROMPT_V115, v)
            signals = call_claude(prompt, v['video_id'])
            log(f'    → {len(signals)}개 시그널')
            results.append({
                'video_id': v['video_id'], 'title': v['title'],
                'channel': v['channel_name'], 'duration': v.get('duration_seconds', 0),
                'ground_truth': v['ground_truth'],
                'v115_signals': signals, 'v115_error': None,
                'v12_signals': None,    'v12_error': None,
            })
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as e:
            log(f'    [FATAL] {type(e).__name__}: {e}')
            results.append({
                'video_id': v['video_id'], 'title': v.get('title','?'),
                'channel': v.get('channel_name','?'), 'duration': v.get('duration_seconds',0),
                'ground_truth': v.get('ground_truth',[]),
                'v115_signals': [], 'v115_error': str(e),
                'v12_signals': None, 'v12_error': None,
            })
        time.sleep(REQ_DELAY)
        # 배치 딜레이
        if i % BATCH_SIZE == 0 and i < len(videos):
            log(f'  [배치 {i//BATCH_SIZE} 완료] {BATCH_DELAY}초 대기...')
            time.sleep(BATCH_DELAY)

    # ── V12 실행 ────────────────────────────────────────────────────────────────
    log(f'\n=== V12 실행 ({len(videos)}개, {BATCH_SIZE}개씩 배치) ===')
    for i, v in enumerate(videos, 1):
        try:
            log(f'  V12 [{i}/{len(videos)}] {v["video_id"]} | {v["title"][:40]}')
            prompt = build_text_prompt(PROMPT_V12, v)
            signals = call_claude(prompt, v['video_id'])
            log(f'    → {len(signals)}개 시그널')
            for res in results:
                if res['video_id'] == v['video_id']:
                    res['v12_signals'] = signals
                    break
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as e:
            log(f'    [FATAL] {type(e).__name__}: {e}')
            for res in results:
                if res['video_id'] == v['video_id']:
                    res['v12_signals'] = []
                    res['v12_error'] = str(e)
                    break
        time.sleep(REQ_DELAY)
        if i % BATCH_SIZE == 0 and i < len(videos):
            log(f'  [배치 {i//BATCH_SIZE} 완료] {BATCH_DELAY}초 대기...')
            time.sleep(BATCH_DELAY)

    # ── 집계 ────────────────────────────────────────────────────────────────────
    log(f'\n=== 집계 (총 {len(results)}개 결과) ===')
    def zero_stats():
        return {'correct':0,'total_gt':0,'wrong':[],'over':[],'under':[],'errors':0}
    s115, s12 = zero_stats(), zero_stats()
    diffs = []

    for r in results:
        gt = r['ground_truth']
        c115 = compare(gt, r['v115_signals'] or [])
        c12  = compare(gt, r['v12_signals']  or [])
        r['v115_cmp'], r['v12_cmp'] = c115, c12
        for key in ('correct','total_gt'):
            s115[key] += c115[key]; s12[key] += c12[key]
        s115['wrong'].extend([{**w,'video':r['video_id']} for w in c115['wrong']])
        s115['over'].extend( [{**o,'video':r['video_id']} for o in c115['over']])
        s115['under'].extend([{**u,'video':r['video_id']} for u in c115['under']])
        s12['wrong'].extend( [{**w,'video':r['video_id']} for w in c12['wrong']])
        s12['over'].extend(  [{**o,'video':r['video_id']} for o in c12['over']])
        s12['under'].extend( [{**u,'video':r['video_id']} for u in c12['under']])
        t115 = {s.get('stock'): s.get('signal_type') for s in (r['v115_signals'] or []) if s.get('stock')}
        t12  = {s.get('stock'): s.get('signal_type') for s in (r['v12_signals']  or []) if s.get('stock')}
        for stock in set(t115)|set(t12):
            if t115.get(stock) != t12.get(stock):
                diffs.append({'video':r['video_id'],'stock':stock,'v115':t115.get(stock),'v12':t12.get(stock)})

    acc115 = s115['correct']/s115['total_gt'] if s115['total_gt'] else 0
    acc12  = s12['correct'] /s12['total_gt']  if s12['total_gt']  else 0

    # JSON 저장
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump({'results':results,'v115_stats':s115,'v12_stats':s12,'diffs':diffs,
                   'model':CLAUDE_MODEL}, f, ensure_ascii=False, indent=2)

    # 리포트
    imp = acc12 - acc115
    imp_str = f'{"✅ +" if imp>0 else "❌ " if imp<0 else "→ "}{abs(imp):.1%}'

    lines = [
        f'# Claude V11.5 vs V12 Eval 리포트',
        f'생성: {datetime.now().strftime("%Y-%m-%d %H:%M")} | 모델: {CLAUDE_MODEL} | 평가 영상: {len(videos)}개',
        '',
        '## 1. 정확도 요약',
        '| 항목 | V11.5 | V12 | 개선 |',
        '|---|---|---|---|',
        f'| 정확도 (signal_type 일치율) | {acc115:.1%} | {acc12:.1%} | {imp_str} |',
        f'| 정답 시그널 수 (총합) | {s115["total_gt"]} | {s12["total_gt"]} | - |',
        f'| 정확 일치 건수 | {s115["correct"]} | {s12["correct"]} | - |',
        f'| 오분류 건수 | {len(s115["wrong"])} | {len(s12["wrong"])} | {"✅" if len(s12["wrong"])<len(s115["wrong"]) else "❌" if len(s12["wrong"])>len(s115["wrong"]) else "→"} |',
        f'| 과잉 추출 건수 | {len(s115["over"])} | {len(s12["over"])} | {"✅" if len(s12["over"])<len(s115["over"]) else "❌"} |',
        f'| 미추출 건수 | {len(s115["under"])} | {len(s12["under"])} | {"✅" if len(s12["under"])<len(s115["under"]) else "❌"} |',
        '',
        '## 2. V11.5 오분류',
    ]
    for w in s115['wrong']:
        lines.append(f'- `{w["video"]}` | {w["stock"]}: GT={w["gt"]} → V11.5={w["pred"]}')
    if not s115['wrong']: lines.append('(없음)')

    lines += ['', '## 3. V12 오분류']
    for w in s12['wrong']:
        lines.append(f'- `{w["video"]}` | {w["stock"]}: GT={w["gt"]} → V12={w["pred"]}')
    if not s12['wrong']: lines.append('(없음)')

    lines += ['', f'## 4. V11.5 → V12 달라진 시그널 ({len(diffs)}건)']
    for d in diffs[:50]:
        lines.append(f'- `{d["video"]}` | {d["stock"]}: V11.5={d["v115"] or "없음"} → V12={d["v12"] or "없음"}')

    lines += ['', '## 5. 과잉 추출 TOP']
    lines.append('### V11.5')
    for s, c in Counter(o['stock'] for o in s115['over']).most_common(8):
        lines.append(f'- {s}: {c}회')
    lines.append('### V12')
    for s, c in Counter(o['stock'] for o in s12['over']).most_common(8):
        lines.append(f'- {s}: {c}회')

    lines += ['', '## 6. 미추출 TOP']
    lines.append('### V11.5')
    for s, c in Counter(u['stock'] for u in s115['under']).most_common(8):
        lines.append(f'- {s}: {c}회')
    lines.append('### V12')
    for s, c in Counter(u['stock'] for u in s12['under']).most_common(8):
        lines.append(f'- {s}: {c}회')

    lines += ['', '## 7. 영상별 결과']
    lines.append('| 영상ID | 채널 | GT건 | V11.5(정확/예측) | V12(정확/예측) |')
    lines.append('|---|---|---|---|---|')
    for r in results:
        c1, c2 = r['v115_cmp'], r['v12_cmp']
        lines.append(f'| {r["video_id"]} | {r["channel"]} | {c1["total_gt"]} | {c1["correct"]}/{c1["pred_count"]} | {c2["correct"]}/{c2["pred_count"]} |')

    report = '\n'.join(lines)
    REPORT_PATH.write_text(report, encoding='utf-8')

    log(f'\n=== 완료 ===')
    log(f'JSON: {JSON_PATH}')
    log(f'리포트: {REPORT_PATH}')
    print('\n' + '='*60)
    print(f'V11.5 정확도: {acc115:.1%}  |  V12 정확도: {acc12:.1%}  |  개선: {imp_str}')
    print('='*60)
    print('\n' + report[:3000])


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log('[INTERRUPTED]')
        sys.exit(0)
    except Exception as e:
        log(f'[FATAL] {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
