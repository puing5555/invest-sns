from youtube_transcript_api import YouTubeTranscriptApi
import sys
sys.stdout.reconfigure(encoding='utf-8')
t = YouTubeTranscriptApi.get_transcript('wf7MJrKGQIc', languages=['en','ko'])
text = ' '.join([x['text'] for x in t])
print(f'자막 {len(t)}개 | {len(text)}자')
print(text[:200])
