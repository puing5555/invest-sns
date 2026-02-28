"""youtube-transcript-api 라이브러리로 자막 다운로드 시도"""
import sys
import io
import json
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

VID = 'ksA4IT452_4'
SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

print("=== youtube-transcript-api 시도 ===")

try:
    # youtube-transcript-api 설치 시도
    import subprocess
    print("Installing youtube-transcript-api...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'youtube-transcript-api'], 
                   check=True, capture_output=True)
    print("✅ 설치 완료")
    
    # 모듈 import
    from youtube_transcript_api import YouTubeTranscriptApi
    print("✅ 모듈 로드 성공")
    
    # 자막 가져오기
    print(f"자막 다운로드 시도: {VID}")
    
    # 한국어 자막 시도
    try:
        transcript = YouTubeTranscriptApi.get_transcript(VID, languages=['ko'])
        print(f"✅ 한국어 자막 성공! {len(transcript)}개 세그먼트")
        
        # JSON 형식으로 저장
        segments = []
        for item in transcript:
            segments.append({
                'start': item['start'],
                'text': item['text']
            })
        
        json_path = f'{SUBS_DIR}/{VID}_transcript.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'video_id': VID,
                'title': '삼성전자 사야 돼요?',
                'segments': segments
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 저장 완료: {json_path}")
        print(f"첫 번째 세그먼트: {segments[0]['text'][:50]}..." if segments else "세그먼트 없음")
        
    except Exception as e:
        print(f"❌ 한국어 자막 실패: {e}")
        
        # 자동 생성 자막 시도
        try:
            transcript = YouTubeTranscriptApi.get_transcript(VID, languages=['ko-KR', 'ko'])
            print(f"✅ 자동 생성 자막 성공! {len(transcript)}개 세그먼트")
            
        except Exception as e2:
            print(f"❌ 자동 생성 자막도 실패: {e2}")
            
            # 사용 가능한 언어 확인
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(VID)
                available = []
                for transcript in transcript_list:
                    available.append(f"{transcript.language} ({transcript.language_code})")
                
                print(f"사용 가능한 자막: {', '.join(available)}")
                
                # 첫 번째 사용 가능한 자막으로 시도
                if available:
                    first_transcript = list(transcript_list)[0]
                    transcript = first_transcript.fetch()
                    print(f"✅ {first_transcript.language} 자막 다운로드 성공!")
                    
                else:
                    print("❌ 사용 가능한 자막 없음")
                    
            except Exception as e3:
                print(f"❌ 자막 목록 조회 실패: {e3}")

except ImportError as e:
    print(f"❌ youtube-transcript-api 설치/로드 실패: {e}")
except Exception as e:
    print(f"❌ 전체 프로세스 실패: {e}")

# 결과 확인
json_path = f'{SUBS_DIR}/{VID}_transcript.json'
if os.path.exists(json_path):
    print(f"\n🎉 SUCCESS! 자막 파일 생성됨: {json_path}")
    size = os.path.getsize(json_path)
    print(f"파일 크기: {size} bytes")
else:
    print(f"\n❌ 자막 파일 생성 실패")