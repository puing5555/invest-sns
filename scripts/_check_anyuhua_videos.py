import yt_dlp
# /videos 탭으로 직접 접근
opts = {'quiet': True, 'no_warnings': True, 'extract_flat': 'in_playlist', 'ignoreerrors': True, 'playlistend': 20}
url = 'https://www.youtube.com/@anyuhuatv/videos'
with yt_dlp.YoutubeDL(opts) as ydl:
    info = ydl.extract_info(url, download=False)
    if info:
        entries = info.get('entries', [])
        print(f'총 entries: {len(entries)}')
        for e in (entries or [])[:10]:
            if e:
                avail = e.get('availability', '')
                print(f"  {e.get('id')} | avail={avail} | {e.get('title','')[:50]}")
