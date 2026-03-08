#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_v11_2_sesang101.py - V11.2 프롬프트 세상학개론 테스트
V11.1(과필터): 3개 → V11.2(목표): 10~15개
"""

import os
import json
import sys
import time
import glob
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.path.append(os.path.dirname(__file__))

from pipeline_config import PipelineConfig
from signal_analyzer_rest import SignalAnalyzer

# V11.2 프롬프트 경로 (pipeline_config 대신 직접 지정)
V11_2_PROMPT_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'prompts', 'pipeline_v11.2.md'
)

SUBS_DIR = os.path.join(os.path.dirname(__file__), '..', 'subs')
CHANNEL_INFO = {
    'url': 'https://www.youtube.com/@sesang101',
    'name': '세상학개론',
}

def load_prompt_v11_2():
    with open(V11_2_PROMPT_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def get_subtitle_files(limit=10):
    # VTT 파일 지원
    files = glob.glob(os.path.join(SUBS_DIR, "*.vtt"))
    files += glob.glob(os.path.join(SUBS_DIR, "*.json"))
    files = [f for f in files if '_failed' not in f]
    files.sort(key=os.path.getmtime, reverse=True)  # 최신 파일 우선
    return files[:limit]

def analyze_with_v11_2(video_id, subtitle_text, analyzer):
    """V11.2 프롬프트로 단일 영상 분석"""
    prompt_template = load_prompt_v11_2()
    
    video_info = {
        'title': f'세상학개론 영상 {video_id}',
        'url': f'https://www.youtube.com/watch?v={video_id}',
        'duration': 'N/A',
        'upload_date': 'N/A'
    }
    
    # analyzer의 프롬프트를 V11.2로 교체
    original_prompt = analyzer.prompt_template
    analyzer.prompt_template = prompt_template
    
    try:
        result = analyzer.analyze_video_subtitle(
            channel_url=CHANNEL_INFO['url'],
            video_data=video_info,
            subtitle=subtitle_text
        )
    finally:
        analyzer.prompt_template = original_prompt  # 복구
    
    return result

def main():
    print("=" * 60)
    print("V11.2 프롬프트 세상학개론 테스트")
    print("목표: 10~15개 시그널")
    print("=" * 60)
    
    config = PipelineConfig()
    analyzer = SignalAnalyzer()
    
    # 자막 파일 목록 (10개)
    subtitle_files = get_subtitle_files(limit=10)
    print(f"자막 파일: {len(subtitle_files)}개 로드")
    
    all_signals = []
    results = []
    
    for i, sub_file in enumerate(subtitle_files, 1):
        video_id = os.path.basename(sub_file).replace('.json', '')
        print(f"\n[{i}/{len(subtitle_files)}] {video_id}")
        
        try:
            if sub_file.endswith('.vtt'):
                # VTT 파일 파싱
                import re
                with open(sub_file, 'r', encoding='utf-8') as f:
                    raw = f.read()
                # VTT 태그/타임코드 제거
                lines = raw.split('\n')
                text_lines = []
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('WEBVTT') or line.startswith('NOTE'):
                        continue
                    if '-->' in line:
                        continue
                    if re.match(r'^\d+$', line):
                        continue
                    # 인라인 태그 제거
                    clean = re.sub(r'<[^>]+>', '', line)
                    if clean:
                        text_lines.append(clean)
                full_text = ' '.join(text_lines).strip()
            else:
                with open(sub_file, 'r', encoding='utf-8') as f:
                    segments = json.load(f)
                full_text = " ".join(
                    seg['text'] for seg in segments
                    if isinstance(seg, dict) and 'text' in seg
                ).strip()
            
            if len(full_text) < 100:
                print(f"  [SKIP] 자막 너무 짧음 ({len(full_text)}자)")
                continue
            
            print(f"  자막: {len(full_text)}자")
            
            start_time = time.time()
            result = analyze_with_v11_2(video_id, full_text, analyzer)
            elapsed = time.time() - start_time
            
            if result:
                signals = result.get('signals', [])
                print(f"  시그널: {len(signals)}개 ({elapsed:.1f}초)")
                
                for sig in signals:
                    stype = sig.get('signal_type', '?')
                    stock = sig.get('stock', '?')
                    conf = sig.get('confidence', '?')
                    print(f"    [{stype}] {stock} (신뢰도: {conf})")
                    all_signals.append(sig)
                
                results.append({
                    'video_id': video_id,
                    'signals': signals,
                    'elapsed': elapsed
                })
            else:
                print(f"  [NO RESULT]")
            
            if i < len(subtitle_files):
                time.sleep(5)
                
        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 결과 요약")
    print("=" * 60)
    
    signal_counts = {}
    for sig in all_signals:
        stype = sig.get('signal_type', '?')
        signal_counts[stype] = signal_counts.get(stype, 0) + 1
    
    print(f"총 시그널: {len(all_signals)}개")
    for stype, cnt in sorted(signal_counts.items(), key=lambda x: -x[1]):
        print(f"  {stype}: {cnt}개")
    
    target_min, target_max = 10, 15
    if target_min <= len(all_signals) <= target_max:
        print(f"\n✅ 목표 범위 달성! ({target_min}~{target_max}개)")
    elif len(all_signals) < target_min:
        print(f"\n⚠️  과필터: {len(all_signals)}개 < {target_min}개 목표")
    else:
        print(f"\n⚠️  과추출: {len(all_signals)}개 > {target_max}개 목표")
    
    # 결과 저장
    output = {
        'test_date': datetime.now().isoformat(),
        'prompt_version': 'V11.2',
        'videos_analyzed': len(results),
        'total_signals': len(all_signals),
        'signal_distribution': signal_counts,
        'results': results
    }
    
    out_file = os.path.join(
        os.path.dirname(__file__), '..', 'test_v11_2_results.json'
    )
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n결과 저장: {out_file}")

if __name__ == "__main__":
    main()
