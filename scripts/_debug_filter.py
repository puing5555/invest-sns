import sys
sys.path.insert(0, '.')
from title_filter import TitleFilter
import yt_dlp

tf = TitleFilter()
opts = {'quiet': True, 'no_warnings': True, 'extract_flat': 'in_playlist', 'ignoreerrors': True, 'playlistend': 20}
with yt_dlp.YoutubeDL(opts) as ydl:
    info = ydl.extract_info('https://www.youtube.com/@anyuhuatv/videos', download=False)
    entries = info.get('entries', []) if info else []
    for e in entries[:15]:
        if not e: continue
        title = e.get('title', '')
        skip = tf.should_skip(title)
        print(f"{'SKIP' if skip else 'OK  '} | {title[:60]}")
