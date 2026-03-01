# test_single_video.py - 단일 영상 테스트
from youtube_transcript_api import YouTubeTranscriptApi
import sys
import os

# 현재 디렉토리를 scripts에 추가
sys.path.append(os.path.dirname(__file__))

from signal_analyzer_rest import SignalAnalyzer
from db_inserter_rest import DatabaseInserter

def test_single_video():
    video_id = 'Ke7gQMbIFLI'  # Bitcoin 100 million 영상
    channel_url = 'https://www.youtube.com/@sesang101'
    
    try:
        # 1. 자막 수집
        print("=== 1. 자막 수집 ===")
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        
        ko_transcript = transcript_list.find_transcript(['ko'])
        transcript_data = ko_transcript.fetch()
        
        print(f"자막 수집 성공: {len(transcript_data)}개 세그먼트")
        
        # 자막을 텍스트로 변환
        text = ' '.join([item['text'] for item in transcript_data])
        print(f"자막 길이: {len(text)} 문자")
        
        # 2. 영상 데이터 준비
        print("\n=== 2. 영상 데이터 준비 ===")
        video_data = {
            'title': 'Bitcoin 100 million?! A comfortable investment has a higher chance of success',
            'video_id': video_id,
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'duration': 'Unknown',
            'upload_date': '20241201'
        }
        
        print(f"제목: {video_data['title']}")
        print(f"URL: {video_data['url']}")
        
        # 3. AI 분석
        print("\n=== 3. AI 시그널 분석 ===")
        analyzer = SignalAnalyzer()
        
        # 자막이 너무 길면 첫 10000자만 사용
        subtitle = text[:10000] if len(text) > 10000 else text
        print(f"분석할 자막 길이: {len(subtitle)} 문자")
        
        analysis_result = analyzer.analyze_video_subtitle(
            channel_url, 
            video_data, 
            subtitle
        )
        
        if analysis_result:
            print(f"[SUCCESS] AI 분석 완료!")
            print(f"분석 결과: {analysis_result}")
            
            # 4. 데이터베이스 형식 변환
            print("\n=== 4. 데이터베이스 형식 변환 ===")
            signals = analyzer.convert_to_database_format(
                analysis_result, 
                'test-video-uuid-12345'
            )
            
            print(f"변환된 시그널 수: {len(signals)}")
            for signal in signals:
                print(f"- {signal['stock_symbol']}: {signal['signal_type']} (신뢰도: {signal['confidence']})")
            
            return True
            
        else:
            print("[ERROR] AI 분석 실패")
            return False
            
    except Exception as e:
        print(f"[ERROR] 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_single_video()
    print(f"\n=== 테스트 결과: {'성공' if success else '실패'} ===")