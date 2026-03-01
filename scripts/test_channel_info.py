#!/usr/bin/env python3
# test_channel_info.py - 간단한 채널 정보 테스트

import yt_dlp
import sys

def test_sesang101():
    """세상101 채널 정보 확인"""
    channel_url = "https://www.youtube.com/@sesang101/videos"  # /videos 추가
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'playlistend': 20,  # 최대 20개 영상
    }
    
    try:
        print("=== 채널 정보 수집 중 ===")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 채널 정보 추출
            channel_info = ydl.extract_info(channel_url, download=False)
            
            print(f"채널명: {channel_info.get('title', 'Unknown')}")
            print(f"업로더: {channel_info.get('uploader', 'Unknown')}")
            print(f"채널 ID: {channel_info.get('channel_id', 'Unknown')}")
            subscriber_count = channel_info.get('subscriber_count', 0)
            video_count = channel_info.get('video_count', 0)
            print(f"구독자: {subscriber_count:,}" if isinstance(subscriber_count, int) else "구독자: N/A")
            print(f"총 영상: {video_count:,}" if isinstance(video_count, int) else "총 영상: N/A")
            print(f"설명: {channel_info.get('description', 'No description')[:100]}...")
            
            print(f"\n=== 최근 영상 목록 ===")
            
            if 'entries' in channel_info:
                videos = []
                for entry in channel_info['entries'][:10]:
                    if entry is None:
                        continue
                    
                    video_data = {
                        'title': entry.get('title', 'No Title'),
                        'url': entry.get('url', entry.get('webpage_url', '')),
                        'video_id': entry.get('id', ''),
                        'duration': entry.get('duration_string', entry.get('duration', 'Unknown')),
                        'view_count': entry.get('view_count', 0),
                        'upload_date': entry.get('upload_date', ''),
                    }
                    
                    videos.append(video_data)
                
                for i, video in enumerate(videos, 1):
                    print(f"{i}. {video['title']}")
                    view_count = video.get('view_count', 0)
                    view_str = f"{view_count:,}" if isinstance(view_count, int) else "N/A"
                    print(f"   길이: {video['duration']} | 조회수: {view_str}")
                    print(f"   업로드: {video.get('upload_date', 'Unknown')}")
                    print(f"   URL: {video['url']}")
                    print()
                
                print(f"총 {len(videos)}개 영상 정보 수집 완료")
                
                # 간단한 제목 필터링 테스트
                investment_keywords = [
                    # 한글 키워드
                    '전망', '시황', '매수', '매도', '추천', '종목', '주식', '투자', '시장',
                    '삼성전자', 'SK하이닉스', '현대차', 'NAVER', '카카오',
                    # 영어 키워드
                    'bitcoin', 'ethereum', 'coin', 'market', 'bubble', 'investment', 
                    'buy', 'palantir', 'iren', 'rocket lab', 'ai', 'trump',
                    # 종목/회사명
                    'AAPL', 'TSLA', 'NVDA', 'MSFT', 'BTC', 'ETH'
                ]
                
                print(f"\n=== 간단 필터링 테스트 ===")
                pass_count = 0
                skip_count = 0
                
                for video in videos:
                    title_lower = video['title'].lower()
                    
                    # 투자 관련 키워드 체크
                    has_investment_keyword = any(keyword.lower() in title_lower for keyword in investment_keywords)
                    
                    # skip 키워드 체크
                    skip_keywords = ['q&a', '질문', '일상', '공지', '영어']
                    has_skip_keyword = any(keyword in title_lower for keyword in skip_keywords)
                    
                    if has_skip_keyword:
                        print(f"[X] SKIP: {video['title']}")
                        skip_count += 1
                    elif has_investment_keyword:
                        print(f"[O] PASS: {video['title']}")
                        pass_count += 1
                    else:
                        print(f"[?] 애매: {video['title']}")
                        skip_count += 1
                
                print(f"\n필터링 결과: PASS {pass_count}개, SKIP {skip_count}개")
                
            else:
                print("[X] 영상 목록을 찾을 수 없습니다")
                
    except Exception as e:
        print(f"[X] 에러: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = test_sesang101()
    sys.exit(0 if success else 1)