# -*- coding: utf-8 -*-
"""
Gemini V11.5 vs V12 프롬프트 비교 eval
- DB 기존 시그널을 ground truth로 사용
- 40개 영상에 대해 V11.5 / V12 각각 실행 (5개씩 배치)
- 비교 리포트 생성
"""
import os, sys, json, time, requests
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'scripts'))

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, '.env.local'))

import gemini_analyzer as ga
from gemini_analyzer import GEMINI_API_KEY

BASE = os.environ['NEXT_PUBLIC_SUPABASE_URL']
KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY']
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Accept': 'application/json'}

PROMPT_V115 = os.path.join(PROJECT_ROOT, 'prompts', 'pipeline_v11.5.md')
PROMPT_V12  = os.path.join(PROJECT_ROOT, 'prompts', 'pipeline_v12.md')
BATCH_SIZE  = 5
DELAY       = 6  # 요청 간 딜레이(초)
EVAL_SIZE   = 40

REPORT_PATH = os.path.join(PROJECT_ROOT, 'data', f'eval_v11v12_{datetime.now().strftime("%Y%m%d_%H%M")}.md')
JSON_PATH   = os.path.join(PROJECT_ROOT, 'data', f'eval_v11v12_{datetime.now().strftime("%Y%m%d_%H%M")}.json')


def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f'[{ts}] {msg}', flush=True)


# ── 1. eval 영상 40개 선정 ──────────────────────────────
def get_eval_videos(n=40):
    """DB에서 시그널 있는 영상 n개 선정 (채널 다양성 고려)"""
    # 채널별 영상 목록
    r = requests.get(f'{BASE}/rest/v1/influencer_channels?select=id,channel_name', headers=H)
    channels = r.json()

    videos = []
    per_channel = max(1, n // len(channels))
    for ch in channels:
        # 해당 채널에서 시그널 있는 영상 선정
        r = requests.get(
            f'{BASE}/rest/v1/influencer_videos'
            f'?select=id,video_id,title,duration_seconds,channel_id'
            f'&channel_id=eq.{ch["id"]}'
            f'&signal_count=gt.0'
            f'&duration_seconds=gt.0'
            f'&duration_seconds=lt.3600'
            f'&order=published_at.desc'
            f'&limit={per_channel + 2}',
            headers=H
        )
        ch_videos = r.json()
        for v in ch_videos[:per_channel]:
            v['channel_name'] = ch['channel_name']
            videos.append(v)

    # 부족하면 추가 보충
    if len(videos) < n:
        r = requests.get(
            f'{BASE}/rest/v1/influencer_videos'
            f'?select=id,video_id,title,duration_seconds,channel_id'
            f'&signal_count=gt.0&duration_seconds=gt.0&duration_seconds=lt.3600'
            f'&order=published_at.desc&limit={n * 2}',
            headers=H
        )
        all_vids = r.json()
        existing_ids = {v['video_id'] for v in videos}
        for v in all_vids:
            if v['video_id'] not in existing_ids and len(videos) < n:
                # channel_name 추가
                ch_name = next((c['channel_name'] for c in channels if c['id'] == v['channel_id']), '?')
                v['channel_name'] = ch_name
                videos.append(v)

    return videos[:n]


# ── 2. ground truth 시그널 조회 ──────────────────────────
def get_ground_truth(video_db_id):
    r = requests.get(
        f'{BASE}/rest/v1/influencer_signals'
        f'?select=stock,ticker,signal_type,confidence'
        f'&video_id=eq.{video_db_id}',
        headers=H
    )
    return r.json()


# ── 3. Gemini 실행 (프롬프트 경로 override) ──────────────
def run_gemini_with_prompt(video, prompt_path):
    """gemini_analyzer의 PROMPT_PATH를 override하여 실행"""
    original = ga.PROMPT_PATH
    ga.PROMPT_PATH = prompt_path
    try:
        # url 필드 보장
        if 'url' not in video:
            video['url'] = f"https://www.youtube.com/watch?v={video['video_id']}"
        signals = ga.analyze_video_with_gemini(video)
        return signals, None
    except Exception as e:
        return [], str(e)
    finally:
        ga.PROMPT_PATH = original


# ── 4. 시그널 비교 ──────────────────────────────────────
def compare_signals(gt_signals, pred_signals):
    """ground truth vs 예측 시그널 비교"""
    gt_stocks = {s['stock'].strip(): s['signal_type'] for s in gt_signals}
    pred_stocks = {s['stock'].strip(): s['signal_type'] for s in pred_signals if isinstance(s, dict)}

    correct = 0
    wrong = []
    over_extracted = []
    under_extracted = []

    for stock, gt_type in gt_stocks.items():
        if stock in pred_stocks:
            if pred_stocks[stock] == gt_type:
                correct += 1
            else:
                wrong.append({'stock': stock, 'gt': gt_type, 'pred': pred_stocks[stock]})
        else:
            under_extracted.append({'stock': stock, 'gt_type': gt_type})

    for stock, pred_type in pred_stocks.items():
        if stock not in gt_stocks:
            over_extracted.append({'stock': stock, 'pred_type': pred_type})

    total_gt = len(gt_stocks)
    accuracy = correct / total_gt if total_gt > 0 else None

    return {
        'correct': correct,
        'total_gt': total_gt,
        'accuracy': accuracy,
        'wrong': wrong,
        'over_extracted': over_extracted,
        'under_extracted': under_extracted,
        'pred_count': len(pred_stocks),
    }


# ── MAIN ────────────────────────────────────────────────
def main():
    log(f'=== Gemini V11.5 vs V12 Eval 시작 ===')
    log(f'평가 영상 수: {EVAL_SIZE}개')

    # eval 영상 선정
    log('eval 영상 선정 중...')
    eval_videos = get_eval_videos(EVAL_SIZE)
    log(f'선정 완료: {len(eval_videos)}개')

    # ground truth 로드
    log('ground truth 로드 중...')
    for v in eval_videos:
        v['ground_truth'] = get_ground_truth(v['id'])

    results = []

    # ── V11.5 실행 ──
    log(f'\n=== V11.5 실행 시작 ({len(eval_videos)}개) ===')
    for batch_start in range(0, len(eval_videos), BATCH_SIZE):
        batch = eval_videos[batch_start:batch_start + BATCH_SIZE]
        log(f'  배치 {batch_start//BATCH_SIZE + 1}: 영상 {batch_start+1}~{batch_start+len(batch)}')
        for i, v in enumerate(batch):
            log(f'    [{batch_start+i+1}/{len(eval_videos)}] {v["video_id"]} | {v["title"][:40]}')
            signals, err = run_gemini_with_prompt(v, PROMPT_V115)
            results.append({
                'video_id': v['video_id'],
                'title': v['title'],
                'channel': v['channel_name'],
                'duration': v.get('duration_seconds', 0),
                'ground_truth': v['ground_truth'],
                'v115_signals': signals,
                'v115_error': err,
                'v12_signals': None,
                'v12_error': None,
            })
            time.sleep(DELAY)
        log(f'  배치 완료. 10초 대기...')
        time.sleep(10)

    # ── V12 실행 ──
    log(f'\n=== V12 실행 시작 ({len(eval_videos)}개) ===')
    for batch_start in range(0, len(eval_videos), BATCH_SIZE):
        batch = eval_videos[batch_start:batch_start + BATCH_SIZE]
        log(f'  배치 {batch_start//BATCH_SIZE + 1}: 영상 {batch_start+1}~{batch_start+len(batch)}')
        for i, v in enumerate(batch):
            log(f'    [{batch_start+i+1}/{len(eval_videos)}] {v["video_id"]} | {v["title"][:40]}')
            signals, err = run_gemini_with_prompt(v, PROMPT_V12)
            results[batch_start + i]['v12_signals'] = signals
            results[batch_start + i]['v12_error'] = err
            time.sleep(DELAY)
        log(f'  배치 완료. 10초 대기...')
        time.sleep(10)

    # ── 비교 분석 ──
    log('\n=== 비교 분석 중 ===')

    v115_stats = {'correct':0, 'total_gt':0, 'wrong':[], 'over':[], 'under':[], 'errors':0}
    v12_stats  = {'correct':0, 'total_gt':0, 'wrong':[], 'over':[], 'under':[], 'errors':0}
    diffs = []

    for r in results:
        gt = r['ground_truth']

        # V11.5
        if r['v115_error']:
            v115_stats['errors'] += 1
        else:
            c115 = compare_signals(gt, r['v115_signals'] or [])
            v115_stats['correct']  += c115['correct']
            v115_stats['total_gt'] += c115['total_gt']
            v115_stats['wrong'].extend([{**w, 'video': r['video_id']} for w in c115['wrong']])
            v115_stats['over'].extend([{**o, 'video': r['video_id']} for o in c115['over_extracted']])
            v115_stats['under'].extend([{**u, 'video': r['video_id']} for u in c115['under_extracted']])
            r['v115_cmp'] = c115

        # V12
        if r['v12_error']:
            v12_stats['errors'] += 1
        else:
            c12 = compare_signals(gt, r['v12_signals'] or [])
            v12_stats['correct']  += c12['correct']
            v12_stats['total_gt'] += c12['total_gt']
            v12_stats['wrong'].extend([{**w, 'video': r['video_id']} for w in c12['wrong']])
            v12_stats['over'].extend([{**o, 'video': r['video_id']} for o in c12['over_extracted']])
            v12_stats['under'].extend([{**u, 'video': r['video_id']} for u in c12['under_extracted']])
            r['v12_cmp'] = c12

        # diff
        v115_types = {s['stock']: s['signal_type'] for s in (r['v115_signals'] or [])}
        v12_types  = {s['stock']: s['signal_type'] for s in (r['v12_signals'] or [])}
        all_stocks = set(v115_types) | set(v12_types)
        for stock in all_stocks:
            t115 = v115_types.get(stock)
            t12  = v12_types.get(stock)
            if t115 != t12:
                diffs.append({'video': r['video_id'], 'stock': stock, 'v115': t115, 'v12': t12})

    # 정확도 계산
    acc115 = v115_stats['correct'] / v115_stats['total_gt'] if v115_stats['total_gt'] > 0 else 0
    acc12  = v12_stats['correct']  / v12_stats['total_gt']  if v12_stats['total_gt'] > 0 else 0

    # ── JSON 저장 ──
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump({'results': results, 'v115_stats': v115_stats, 'v12_stats': v12_stats, 'diffs': diffs}, f, ensure_ascii=False, indent=2)
    log(f'JSON 저장: {JSON_PATH}')

    # ── 리포트 생성 ──
    report = [
        f'# Gemini V11.5 vs V12 Eval 리포트',
        f'생성일시: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'평가 영상: {len(eval_videos)}개\n',
        f'## 1. 정확도 요약 (ground truth = DB 기존 시그널)',
        f'| 항목 | V11.5 | V12 | 개선 |',
        f'|---|---|---|---|',
        f'| 정확도 (signal_type 일치율) | {acc115:.1%} | {acc12:.1%} | {"✅ +" if acc12 > acc115 else "❌ " if acc12 < acc115 else "→"}{abs(acc12-acc115):.1%} |',
        f'| 오분류 건수 | {len(v115_stats["wrong"])} | {len(v12_stats["wrong"])} | {"✅" if len(v12_stats["wrong"]) < len(v115_stats["wrong"]) else "❌" if len(v12_stats["wrong"]) > len(v115_stats["wrong"]) else "→"} |',
        f'| 과잉 추출 건수 | {len(v115_stats["over"])} | {len(v12_stats["over"])} | {"✅" if len(v12_stats["over"]) < len(v115_stats["over"]) else "❌"} |',
        f'| 미추출 건수 | {len(v115_stats["under"])} | {len(v12_stats["under"])} | {"✅" if len(v12_stats["under"]) < len(v115_stats["under"]) else "❌"} |',
        f'| API 에러 | {v115_stats["errors"]} | {v12_stats["errors"]} | - |',
        '',
        f'## 2. V11.5 오분류 목록',
    ]
    for w in v115_stats['wrong'][:20]:
        report.append(f'- `{w["video"]}` | {w["stock"]}: GT={w["gt"]} → V11.5={w["pred"]}')

    report += [
        '',
        f'## 3. V12 오분류 목록',
    ]
    for w in v12_stats['wrong'][:20]:
        report.append(f'- `{w["video"]}` | {w["stock"]}: GT={w["gt"]} → V12={w["pred"]}')

    report += [
        '',
        f'## 4. V11.5 → V12 diff (같은 영상에서 달라진 시그널)',
        f'총 {len(diffs)}건',
    ]
    for d in diffs[:30]:
        report.append(f'- `{d["video"]}` | {d["stock"]}: V11.5={d["v115"] or "없음"} → V12={d["v12"] or "없음"}')

    report += [
        '',
        f'## 5. 과잉/미추출 상위 종목',
        '',
        '### V11.5 과잉 추출 (정답에 없는 시그널)',
    ]
    from collections import Counter
    over_counter_115 = Counter(o['stock'] for o in v115_stats['over'])
    for stock, cnt in over_counter_115.most_common(10):
        report.append(f'- {stock}: {cnt}회')

    report += ['', '### V12 과잉 추출']
    over_counter_12 = Counter(o['stock'] for o in v12_stats['over'])
    for stock, cnt in over_counter_12.most_common(10):
        report.append(f'- {stock}: {cnt}회')

    report_text = '\n'.join(report)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report_text)

    log(f'\n=== 리포트 저장: {REPORT_PATH} ===')
    print('\n' + report_text)


if __name__ == '__main__':
    main()
