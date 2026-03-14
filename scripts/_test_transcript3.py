import sys
sys.stdout.reconfigure(encoding='utf-8')
from youtube_transcript_api import YouTubeTranscriptApi

api = YouTubeTranscriptApi()
# fetch 메서드 사용
transcript = api.fetch('wf7MJrKGQIc')
print(type(transcript))
print(dir(transcript))
