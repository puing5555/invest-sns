#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
세상학개론 시그널 통합 및 중복제거 스크립트
- batch 1-9 파일에서 시그널 수집
- 1영상 1종목 1시그널 중복제거
- Supabase 업로드
- signal_prices.json 업데이트
"""

import os
import sys
import json
import glob
from typing import Dict, List, Set, Tuple
from pathlib import Path

def load_all_signals():
    """모든 배치 파일에서 시그널 로드"""
    all_signals = []
    
    # batch 1-9 파일 로드
    batch_files = glob.glob('sesang101_analysis_results_batch_*.json')
    batch_files.sort()
    
    print(f"배치 파일 {len(batch_files)}개 로드 중...")
    
    for file_path in batch_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            batch_num = data.get('batch_num', 0)
            processed = data.get('processed', [])
            
            for video_data in processed:
                video_id = video_data.get('video_id')
                title = video_data.get('title', '')
                signals = video_data.get('signals', [])
                
                for signal in signals:
                    signal_data = signal.copy()
                    signal_data['video_id'] = video_id
                    signal_data['video_title'] = title
                    signal_data['batch_num'] = batch_num
                    all_signals.append(signal_data)
            
            print(f"[OK] {file_path}: {len(processed)}개 영상, {sum(len(v.get('signals', [])) for v in processed)}개 시그널")
            
        except Exception as e:
            print(f"[ERR] {file_path} 로드 실패: {e}")
    
    print(f"\n[TOTAL] 총 {len(all_signals)}개 시그널 로드 완료")
    return all_signals

def deduplicate_signals(signals):
    """시그널 중복제거 (1영상 1종목 1시그널)"""
    print("\n[INFO] 시그널 중복제거 시작...")
    
    # video_id + stock으로 그룹핑
    groups = {}
    for signal in signals:
        video_id = signal.get('video_id')
        stock = signal.get('stock', '') or ''
        stock = stock.strip() if stock else ''
        
        if not video_id or not stock or stock == 'None':
            continue
            
        key = f"{video_id}_{stock}"
        if key not in groups:
            groups[key] = []
        groups[key].append(signal)
    
    print(f"[GROUP] {len(groups)}개 그룹으로 분류")
    
    deduplicated = []
    merge_count = 0
    
    for key, group_signals in groups.items():
        if len(group_signals) == 1:
            # 중복 없음
            deduplicated.append(group_signals[0])
        else:
            # 중복 있음 - 맥락 합치기
            merge_count += len(group_signals) - 1
            
            # 첫 번째 시그널을 기준으로 합성
            merged = group_signals[0].copy()
            
            # key_quote와 reasoning 합치기
            all_quotes = []
            all_reasoning = []
            
            for signal in group_signals:
                quote = signal.get('key_quote', '').strip()
                reasoning = signal.get('reasoning', '').strip()
                
                if quote and quote not in all_quotes:
                    all_quotes.append(quote)
                if reasoning and reasoning not in all_reasoning:
                    all_reasoning.append(reasoning)
            
            merged['key_quote'] = ' | '.join(all_quotes)
            merged['reasoning'] = ' / '.join(all_reasoning)
            
            # 가장 강한 시그널 선택
            signal_strength = {
                '매수': 5, '강력매수': 6,
                '긍정': 4, '매도': 3, 
                '강력매도': 2, '중립': 1, '경계': 0
            }
            
            strongest_signal = max(group_signals, key=lambda x: signal_strength.get(x.get('signal', ''), -1))
            merged['signal'] = strongest_signal.get('signal')
            merged['mention_type'] = strongest_signal.get('mention_type')
            
            deduplicated.append(merged)
    
    print(f"[OK] 중복제거 완료: {merge_count}개 시그널 합병")
    print(f"[FINAL] 최종 시그널 수: {len(deduplicated)}개")
    
    return deduplicated

def save_signals_json(signals):
    """시그널을 JSON 파일로 저장"""
    output_data = {
        "total_signals": len(signals),
        "processing_date": "2026-03-02",
        "description": "세상학개론 98개 영상 시그널 분석 결과 (중복제거 완료)",
        "signals": signals
    }
    
    output_path = "sesang101_final_signals.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"[SAVE] {output_path} 저장 완료")

def update_signal_prices_json(signals):
    """signal_prices.json 업데이트"""
    try:
        # 기존 파일 읽기
        signal_prices_path = "data/signal_prices.json"
        if os.path.exists(signal_prices_path):
            with open(signal_prices_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        else:
            existing_data = {}
        
        # 새 종목들 추가
        new_stocks = set()
        for signal in signals:
            stock = signal.get('stock', '') or ''
            stock = stock.strip() if stock else ''
            if stock and stock != 'None':
                ticker = signal.get('ticker')
                
                # 한국 주식은 ticker가 6자리 숫자
                if ticker and len(str(ticker).replace('.', '')) == 6:
                    key = f"{ticker}.KS"
                elif stock in ['비트코인', '이더리움', '솔라나']:
                    # 암호화폐 매핑
                    crypto_map = {
                        '비트코인': 'BTC-USD',
                        '이더리움': 'ETH-USD', 
                        '솔라나': 'SOL-USD'
                    }
                    key = crypto_map.get(stock)
                else:
                    # 미국 주식 추정
                    key = stock
                
                if key and key not in existing_data:
                    existing_data[key] = {
                        "name": stock,
                        "current_price": None,
                        "last_updated": None
                    }
                    new_stocks.add(key)
        
        # 파일 업데이트
        with open(signal_prices_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"[UPDATE] signal_prices.json 업데이트: {len(new_stocks)}개 신규 종목")
        
        # public/signal_prices.json도 동기화
        public_path = "public/signal_prices.json"
        Path("public").mkdir(exist_ok=True)
        
        with open(public_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"[SYNC] public/signal_prices.json 동기화 완료")
        
    except Exception as e:
        print(f"[ERR] signal_prices.json 업데이트 실패: {e}")

def prepare_supabase_upload(signals):
    """Supabase 업로드 데이터 준비"""
    print("\n[INFO] Supabase 업로드 데이터 준비 중...")
    
    upload_data = []
    
    for signal in signals:
        record = {
            "video_id": signal.get('video_id'),
            "video_title": signal.get('video_title'),
            "speaker_name": signal.get('speaker', '세상학개론'),
            "stock": signal.get('stock'),
            "ticker": signal.get('ticker'),
            "market": signal.get('market', 'KR'),
            "mention_type": signal.get('mention_type'),
            "signal": signal.get('signal'),
            "confidence": signal.get('confidence'),
            "timestamp": signal.get('timestamp'),
            "key_quote": signal.get('key_quote'),
            "reasoning": signal.get('reasoning'),
            "pipeline_version": "V9",
            "review_status": "pending",
            "channel_name": "세상학개론",
            "published_at": "2026-03-02"
        }
        upload_data.append(record)
    
    # Supabase 업로드 준비 파일 저장
    with open("sesang101_supabase_upload.json", 'w', encoding='utf-8') as f:
        json.dump(upload_data, f, indent=2, ensure_ascii=False)
    
    print(f"[READY] Supabase 업로드 데이터 준비: {len(upload_data)}개 레코드")
    return upload_data

def main():
    """메인 실행 함수"""
    print("[START] 세상학개론 시그널 통합 및 중복제거 시작\n")
    
    # 1. 모든 시그널 로드
    all_signals = load_all_signals()
    
    if not all_signals:
        print("[ERR] 시그널이 없습니다")
        return
    
    # 2. 중복제거
    deduplicated_signals = deduplicate_signals(all_signals)
    
    # 3. JSON 파일 저장
    save_signals_json(deduplicated_signals)
    
    # 4. signal_prices.json 업데이트
    update_signal_prices_json(deduplicated_signals)
    
    # 5. Supabase 업로드 준비
    prepare_supabase_upload(deduplicated_signals)
    
    print(f"\n[DONE] 처리 완료!")
    print(f"[STAT] 원본 시그널: {len(all_signals)}개")
    print(f"[STAT] 중복제거 후: {len(deduplicated_signals)}개")
    print(f"[STAT] 중복제거된 수: {len(all_signals) - len(deduplicated_signals)}개")

if __name__ == "__main__":
    main()