#!/usr/bin/env python3
"""
sesang101 채널 전용 파이프라인
YouTube IP 차단 우회를 위해 Invidious API 사용
"""

import os
import sys
import json
import time
import random
import uuid
import requests
from datetime import datetime

sys.path.append(os.path.dirname(__file__))
from signal_analyzer_rest import SignalAnalyzer
from db_inserter_rest import DatabaseInserter
from pipeline_config import PipelineConfig

# Invidious 인스턴스 목록
INVIDIOUS_INSTANCES = [
    "https://vid.puffyan.us",
    "https://invidious.fdn.fr",
    "https://inv.nadeko.net",
    "https://invidious.nerdvpn.de",
    "https://invidious.jing.rocks",
    "https://invidious.privacyredirect.com",
    "https://yt.artemislena.eu",
]

CHANNEL_URL = "https://www.youtube.com/@sesang101"
CHANNEL_ID = None  # Will be resolved

def get_invidious_api(path, params=None):
    """Invidious API 호출 (여러 인스턴스 시도)"""
    for instance in INVIDIOUS_INSTANCES:
        try:
            url = f"{instance}/api/v1{path}"
            r = requests.get(url, params=params, timeout=15)
            if r.status_code == 200:
                return r.json()
        except Exception:
            continue
    return None

def get_channel_videos():
    """Invidious로 세상학개론 채널 영상 목록 수집"""
    # 먼저 채널 검색
    data = get_invidious_api("/search", {"q": "세상학개론", "type": "channel"})
    if not data:
        print("[ERROR] Invidious 채널 검색 실패")
        return None, []
    
    channel_id = None
    for item in data:
        if item.get("type") == "channel" and "sesang" in item.get("authorUrl", "").lower():
            channel_id = item["authorId"]
            break
    
    if not channel_id:
        # 직접 알려진 ID 사용
        channel_id = "UCsJ6RuBiTVWRX156FVbeaGg"  # 세상학개론 채널 ID
    
    print(f"[OK] 채널 ID: {channel_id}")
    
    # 채널 영상 목록
    all_videos = []
    page = 1
    while len(all_videos) < 100:
        data = get_invidious_api(f"/channels/{channel_id}/videos", {"page": str(page)})
        if not data or len(data) == 0:
            break
        all_videos.extend(data)
        page += 1
        time.sleep(1)
    
    print(f"[OK] 총 {len(all_videos)}개 영상 수집")
    return channel_id, all_videos

def get_transcript_invidious(video_id):
    """Invidious로 자막 추출"""
    data = get_invidious_api(f"/captions/{video_id}")
    if not data or not data.get("captions"):
        return None
    
    # 한국어 자막 찾기
    ko_caption = None
    for cap in data["captions"]:
        if cap.get("language_code", "").startswith("ko"):
            ko_caption = cap
            break
    
    if not ko_caption:
        # 자동 생성 한국어 자막
        for cap in data["captions"]:
            if "auto" in cap.get("label", "").lower() and "ko" in cap.get("language_code", ""):
                ko_caption = cap
                break
    
    if not ko_caption:
        return None
    
    # 자막 URL로 다운로드
    for instance in INVIDIOUS_INSTANCES:
        try:
            url = f"{instance}{ko_caption['url']}"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                return r.text
        except:
            continue
    
    return None

def get_transcript_direct(video_id):
    """YouTube Transcript API 직접 호출 (IP 차단 우회용 대안)"""
    # timedtext API 직접 호출
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            return None
        
        # 페이지에서 자막 URL 추출
        import re
        match = re.search(r'"captionTracks":\[.*?"baseUrl":"(.*?)"', r.text)
        if match:
            caption_url = match.group(1).replace('\\u0026', '&')
            # 한국어 자막 URL로 변환
            if 'lang=ko' not in caption_url:
                caption_url += '&lang=ko&fmt=srv3'
            r2 = requests.get(caption_url, headers=headers, timeout=15)
            if r2.status_code == 200:
                # XML에서 텍스트 추출
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(r2.text, 'lxml')
                texts = [t.text for t in soup.find_all('text')]
                return ' '.join(texts)
    except Exception as e:
        pass
    
    return None

def filter_investment_videos(videos):
    """투자 관련 영상 필터링"""
    investment_keywords = [
        'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'blockchain',
        'palantir', 'pltr', 'tesla', 'tsla', 'nvidia', 'nvda', 'apple', 'aapl',
        'investment', 'investing', 'stock', 'stocks', 'market', 'bubble',
        'portfolio', 'asset', 'wealth', 'economy', 'economic', 'trump',
        'buy', 'sell', 'crash', 'rally', 'bull', 'bear', 'dividend',
        'finance', 'financial', 'coin', 'nft',
        # 한글
        '투자', '주식', '코인', '비트코인', '이더리움', '팔란티어', '테슬라',
        '엔비디아', '시장', '경제', '매수', '매도', '종목', '증시', '나스닥',
        '금리', '포트폴리오', '자산', '배당', '버블', '전망', '실적',
        '투자학', '세상학개론',
    ]
    
    skip_keywords = [
        '멤버십', '멤버쉽', 'members only', '회원전용',
        '쇼츠', 'shorts', '#shorts',
        '와인', '향수', '음주', '술',
    ]
    
    passed = []
    for v in videos:
        title = v.get('title', '').lower()
        
        # 스킵 키워드 체크
        should_skip = False
        for kw in skip_keywords:
            if kw.lower() in title:
                should_skip = True
                break
        if should_skip:
            continue
        
        # 투자 관련 키워드 체크
        for kw in investment_keywords:
            if kw.lower() in title:
                passed.append(v)
                break
    
    return passed

def run_pipeline():
    """메인 파이프라인 실행"""
    config = PipelineConfig()
    analyzer = SignalAnalyzer()
    db = DatabaseInserter()
    
    print("=" * 60)
    print("sesang101 채널 시그널 추출 파이프라인")
    print("=" * 60)
    
    # 1. 채널 영상 목록 수집
    print("\n[STEP 1] 채널 영상 목록 수집...")
    channel_id, all_videos = get_channel_videos()
    
    if not all_videos:
        print("[ERROR] 영상 목록 수집 실패. yt-dlp flat-playlist 대안 시도...")
        # yt-dlp로 영상 ID 목록만 추출 (flat playlist는 IP 차단에 덜 민감)
        import subprocess
        try:
            result = subprocess.run(
                ['python', '-m', 'yt_dlp', '--flat-playlist', '--print', '%(id)s\t%(title)s\t%(upload_date)s',
                 'https://www.youtube.com/@sesang101/videos'],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                all_videos = []
                for line in lines:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        all_videos.append({
                            'videoId': parts[0],
                            'title': parts[1],
                            'publishedText': parts[2] if len(parts) > 2 else ''
                        })
                print(f"[OK] yt-dlp로 {len(all_videos)}개 영상 수집")
        except Exception as e:
            print(f"[ERROR] yt-dlp도 실패: {e}")
            return
    
    if not all_videos:
        print("[ERROR] 영상 목록을 전혀 수집할 수 없습니다.")
        return
    
    # 2. 투자 관련 영상 필터링
    print("\n[STEP 2] 투자 관련 영상 필터링...")
    investment_videos = filter_investment_videos(all_videos)
    print(f"[OK] {len(all_videos)}개 중 {len(investment_videos)}개 투자 관련 영상 선별")
    
    # 3. 기존 DB 영상 확인 (중복 방지)
    print("\n[STEP 3] 기존 DB 확인...")
    existing_videos = []
    try:
        response = requests.get(
            f"{db.base_url}/influencer_videos",
            headers=db.headers,
            params={'select': 'video_id', 'channel_id': f'not.is.null'}
        )
        if response.status_code == 200:
            existing_videos = [v['video_id'] for v in response.json()]
            print(f"[OK] DB에 기존 {len(existing_videos)}개 영상 존재")
    except Exception as e:
        print(f"[WARNING] 기존 DB 확인 실패: {e}")
    
    # 새로운 영상만 필터링
    new_videos = [v for v in investment_videos if v.get('videoId', '') not in existing_videos]
    print(f"[OK] 새로운 영상: {len(new_videos)}개")
    
    if not new_videos:
        print("[OK] 새로운 투자 영상이 없습니다.")
        return
    
    # 4. 자막 추출 + AI 분석
    print(f"\n[STEP 4] 자막 추출 + AI 분석 ({len(new_videos)}개 영상)...")
    
    total_signals = 0
    success_count = 0
    fail_count = 0
    all_signals = []
    
    for i, video in enumerate(new_videos):
        video_id = video.get('videoId', '')
        title = video.get('title', 'Unknown')
        
        print(f"\n--- [{i+1}/{len(new_videos)}] {title[:60]} ---")
        
        # 레이트 리밋 규칙: 20개마다 5분 휴식
        if i > 0 and i % 20 == 0:
            print(f"[SLEEP] 20개 처리 완료, 5분 휴식...")
            time.sleep(300)
        
        # 자막 추출 (여러 방법 시도)
        subtitle = None
        
        # 방법 1: Invidious
        subtitle = get_transcript_invidious(video_id)
        if subtitle:
            print(f"  [OK] Invidious 자막 수집 성공 ({len(subtitle)} chars)")
        else:
            # 방법 2: 직접 YouTube 페이지 파싱
            subtitle = get_transcript_direct(video_id)
            if subtitle:
                print(f"  [OK] Direct 자막 수집 성공 ({len(subtitle)} chars)")
            else:
                print(f"  [SKIP] 자막 추출 실패")
                fail_count += 1
                time.sleep(random.uniform(2, 3))
                continue
        
        # 자막이 너무 짧으면 스킵
        if len(subtitle.strip()) < 100:
            print(f"  [SKIP] 자막 너무 짧음 ({len(subtitle)} chars)")
            fail_count += 1
            continue
        
        # AI 분석
        video_data = {
            'title': title,
            'video_id': video_id,
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'duration': str(video.get('lengthSeconds', 'Unknown')),
            'upload_date': video.get('publishedText', '')
        }
        
        analysis = analyzer.analyze_video_subtitle(CHANNEL_URL, video_data, subtitle[:15000])
        
        if analysis:
            # DB용 채널/영상 생성
            try:
                channel_db_id = db.get_or_create_channel({
                    'url': CHANNEL_URL,
                    'name': '세상학개론',
                    'subscriber_count': 0,
                    'video_count': 0,
                    'description': '세상학개론 (sesang101) 투자 유튜브 채널'
                })
                
                video_uuid = db.get_or_create_video(video_data, channel_db_id)
                
                signals = analyzer.convert_to_database_format(analysis, video_uuid)
                
                if signals:
                    result = db.batch_insert_signals(signals)
                    total_signals += result['success']
                    all_signals.extend(signals)
                    print(f"  [SUCCESS] {result['success']}개 시그널 DB 삽입")
                    success_count += 1
                else:
                    print(f"  [WARNING] 시그널 변환 결과 없음")
                    
            except Exception as e:
                print(f"  [ERROR] DB 처리 실패: {e}")
                fail_count += 1
        else:
            print(f"  [ERROR] AI 분석 실패")
            fail_count += 1
        
        # 요청 간 2-3초 딜레이
        time.sleep(random.uniform(2, 3))
    
    # 5. 결과 보고
    print("\n" + "=" * 60)
    print("파이프라인 실행 완료!")
    print("=" * 60)
    print(f"총 영상 수: {len(all_videos)}")
    print(f"투자 관련 영상: {len(investment_videos)}")
    print(f"새 영상: {len(new_videos)}")
    print(f"분석 성공: {success_count}")
    print(f"분석 실패: {fail_count}")
    print(f"추출 시그널: {total_signals}개")
    
    # 결과 JSON 저장
    result_data = {
        'timestamp': datetime.now().isoformat(),
        'channel': 'sesang101',
        'total_videos': len(all_videos),
        'investment_videos': len(investment_videos),
        'new_videos': len(new_videos),
        'success': success_count,
        'failed': fail_count,
        'signals_extracted': total_signals,
        'signals': [
            {
                'stock': s['stock_symbol'],
                'signal': s['signal_type'],
                'confidence': s['confidence']
            } for s in all_signals
        ]
    }
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'sesang101_results.json'), 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n결과 저장: sesang101_results.json")
    return result_data

if __name__ == "__main__":
    run_pipeline()
