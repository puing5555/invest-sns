import sys, youtube_transcript_api
sys.stdout.reconfigure(encoding='utf-8')
print(dir(youtube_transcript_api))
api = youtube_transcript_api.YouTubeTranscriptApi()
print(dir(api))
