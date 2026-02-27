"""YouTube 자막 추출 - youtube_transcript_api 사용"""
import subprocess, sys

# Install if needed
subprocess.run([sys.executable, '-m', 'pip', 'install', 'youtube-transcript-api', '-q'])

from youtube_transcript_api import YouTubeTranscriptApi
import json, os

SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

VIDEOS = {
    # 슈카월드
    'ksA4IT452_4': '삼성전자 사야 돼요?',
    'nm5zQxZSkbk': '스트래티지는 어떻게 비트코인을 계속 살 수 있을까?',
    'XveVkr3JHs4': '연초 이후 +24% 코스피는 왜 강한가',
    'N7xO-UWCM5w': '삼성전자 시총 1000조 돌파',
    # 부읽남TV
    'Xv-wNA91EPE': '삼성전자 절대 팔지 마세요 [조진표]',
    'BVRoApF0c8k': '전세계 돈 다 빨아들일 겁니다 [배재규]',
    # 이효석
    'fDZnPoK5lyc': '반도체 다음 4종목',
    'ZXuQCpuVCYc': '코스피 ETF 이거 사세요',
    'tSXkj2Omz34': '코스피 6000 7900 논리',
    'B5owNUs_DFw': '소프트웨어 주식 사면 망합니다',
    'bmXgryWXNrw': '하이닉스 추가 매수',
}

for vid, title in VIDEOS.items():
    outfile = f'{SUBS_DIR}/{vid}_transcript.json'
    if os.path.exists(outfile):
        print(f"[SKIP] {vid}")
        continue
    
    try:
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(vid, languages=['ko'])
        
        # Convert to simple text
        segments = []
        for snippet in transcript.snippets:
            segments.append({
                'start': snippet.start,
                'text': snippet.text
            })
        
        with open(outfile, 'w', encoding='utf-8') as f:
            json.dump({'video_id': vid, 'title': title, 'segments': segments}, f, ensure_ascii=False, indent=2)
        
        total_text = ' '.join(s['text'] for s in segments)
        print(f"[OK] {vid} - {title} ({len(segments)} segments, {len(total_text)} chars)")
        
    except Exception as e:
        print(f"[FAIL] {vid} - {title}: {e}")

print("\n=== Done ===")
