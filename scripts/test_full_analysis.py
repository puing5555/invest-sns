import sys, time, json, os
sys.path.append('.')
from signal_analyzer_rest import SignalAnalyzer

analyzer = SignalAnalyzer()

# 테스트용 자막 로드
sub_file = os.path.join('..', '..', 'subs', 'sesang101', 'BdNikaqw238.json')
with open(sub_file, 'r', encoding='utf-8') as f:
    segments = json.load(f)
subtitle = " ".join(s.get('text', '') for s in segments if isinstance(s, dict)).strip()

print(f'Subtitle length: {len(subtitle)} chars')

video_data = {
    'title': 'A video to watch when you still dont know much about Ethereum',
    'url': 'https://www.youtube.com/watch?v=BdNikaqw238',
    'duration': 'N/A',
    'upload_date': 'N/A'
}

print(f'Starting analysis at {time.strftime("%H:%M:%S")}...')
start = time.time()
result = analyzer.analyze_video_subtitle(
    channel_url='https://www.youtube.com/@sesang101',
    video_data=video_data,
    subtitle=subtitle
)
elapsed = time.time() - start
print(f'Finished in {elapsed:.1f}s')

if result:
    signals = result.get('signals', [])
    print(f'Signals found: {len(signals)}')
    for s in signals:
        print(f'  - {s.get("stock","?")} | {s.get("signal","?")}')
else:
    print('No result')
