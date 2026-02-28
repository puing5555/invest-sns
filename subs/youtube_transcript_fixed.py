"""youtube-transcript-api 수정된 버전"""
import sys
import io
import json
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

VID = 'ksA4IT452_4'
SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

print("=== youtube-transcript-api 수정된 시도 ===")

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    print("✅ 모듈 로드 성공")
    
    # 올바른 사용법으로 시도
    print(f"자막 다운로드 시도: {VID}")
    
    # 방법 1: 직접 함수 호출
    try:
        transcript = YouTubeTranscriptApi.get_transcript(VID)
        print(f"✅ 기본 자막 성공! {len(transcript)}개 세그먼트")
        
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
        print(f"❌ 기본 자막 실패: {e}")
        
        # 방법 2: 언어 코드 지정
        try:
            transcript = YouTubeTranscriptApi.get_transcript(VID, languages=['ko'])
            print(f"✅ 한국어 자막 성공!")
            
        except Exception as e2:
            print(f"❌ 한국어 지정 실패: {e2}")
            
            # 방법 3: 사용 가능한 자막 확인
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(VID)
                print("사용 가능한 자막:")
                
                for transcript in transcript_list:
                    print(f"  - {transcript.language} ({transcript.language_code})")
                    
                # 첫 번째 자막 다운로드
                for transcript in transcript_list:
                    try:
                        data = transcript.fetch()
                        print(f"✅ {transcript.language} 자막 다운로드 성공! {len(data)}개 세그먼트")
                        
                        # 저장
                        segments = []
                        for item in data:
                            segments.append({
                                'start': item['start'],
                                'text': item['text']
                            })
                        
                        json_path = f'{SUBS_DIR}/{VID}_transcript.json'
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump({
                                'video_id': VID,
                                'title': '삼성전자 사야 돼요?',
                                'language': transcript.language,
                                'segments': segments
                            }, f, ensure_ascii=False, indent=2)
                        
                        print(f"✅ 저장 완료: {json_path}")
                        break
                        
                    except Exception as e4:
                        print(f"❌ {transcript.language} 다운로드 실패: {e4}")
                        continue
                        
            except Exception as e3:
                print(f"❌ 자막 목록 조회 실패: {e3}")

except Exception as e:
    print(f"❌ 전체 오류: {e}")
    import traceback
    traceback.print_exc()

# 결과 확인
json_path = f'{SUBS_DIR}/{VID}_transcript.json'
if os.path.exists(json_path):
    print(f"\n🎉 SUCCESS! 자막 파일 생성됨")
    size = os.path.getsize(json_path)
    print(f"파일 크기: {size} bytes")
else:
    print(f"\n❌ 자막 파일 생성 실패")