"""시간차 공격 - 1개씩 긴 간격으로 자막 다운로드"""
import subprocess, sys, time, os, random

SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

# 가장 중요한 영상 3개만 먼저
PRIORITY_VIDEOS = [
    ('ksA4IT452_4', '삼성전자 사야 돼요?'),
    ('Xv-wNA91EPE', '삼성전자 절대 팔지마 조진표'),
    ('fDZnPoK5lyc', '반도체 다음 4종목 이효석'),
]

# 다양한 User-Agent 로테이션
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
]

def try_method_1(vid, title, ua):
    """Method 1: yt-dlp with User-Agent rotation"""
    print(f"  Method 1: yt-dlp with rotating UA")
    cmd = [sys.executable, '-m', 'yt_dlp', 
           '--write-auto-sub', '--sub-lang', 'ko',
           '--skip-download', '--convert-subs', 'srt',
           '--user-agent', ua,
           '--sleep-interval', '5',
           '--max-sleep-interval', '10',
           '-o', f'{SUBS_DIR}/{vid}',
           f'https://www.youtube.com/watch?v={vid}']
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        if os.path.exists(f'{SUBS_DIR}/{vid}.ko.srt'):
            return True
    except:
        pass
    return False

def try_method_2(vid, title, ua):
    """Method 2: Different subdomain (music.youtube.com)"""
    print(f"  Method 2: music.youtube.com")
    cmd = [sys.executable, '-m', 'yt_dlp', 
           '--write-auto-sub', '--sub-lang', 'ko',
           '--skip-download', '--convert-subs', 'srt',
           '--user-agent', ua,
           '-o', f'{SUBS_DIR}/{vid}',
           f'https://music.youtube.com/watch?v={vid}']
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=45)
        if os.path.exists(f'{SUBS_DIR}/{vid}.ko.srt'):
            return True
    except:
        pass
    return False

def try_method_3(vid, title, ua):
    """Method 3: Mobile endpoint (m.youtube.com)"""
    print(f"  Method 3: m.youtube.com")
    cmd = [sys.executable, '-m', 'yt_dlp', 
           '--write-auto-sub', '--sub-lang', 'ko',
           '--skip-download', '--convert-subs', 'srt',
           '--user-agent', ua,
           '-o', f'{SUBS_DIR}/{vid}',
           f'https://m.youtube.com/watch?v={vid}']
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=45)
        if os.path.exists(f'{SUBS_DIR}/{vid}.ko.srt'):
            return True
    except:
        pass
    return False

for i, (vid, title) in enumerate(PRIORITY_VIDEOS):
    json_path = f'{SUBS_DIR}/{vid}_transcript.json'
    srt_path = f'{SUBS_DIR}/{vid}.ko.srt'
    
    if os.path.exists(json_path) or os.path.exists(srt_path):
        print(f"[SKIP] {vid} - already exists")
        continue
    
    print(f"\n[{i+1}/3] {vid} - {title}")
    ua = random.choice(USER_AGENTS)
    print(f"  Using UA: {ua[:50]}...")
    
    # Try 3 different methods
    methods = [try_method_1, try_method_2, try_method_3]
    
    for method in methods:
        try:
            if method(vid, title, ua):
                print(f"  ✅ SUCCESS with {method.__name__}")
                break
            else:
                print(f"  ❌ {method.__name__} failed")
                time.sleep(15)  # Wait between method attempts
        except Exception as e:
            print(f"  ❌ {method.__name__} error: {e}")
            time.sleep(15)
    else:
        print(f"  ❌ ALL METHODS FAILED for {vid}")
    
    # Long wait between videos
    if i < len(PRIORITY_VIDEOS) - 1:
        wait_time = random.randint(90, 120)  # 1.5-2 minutes
        print(f"  💤 Waiting {wait_time}s before next video...")
        time.sleep(wait_time)

print("\n=== Final Status ===")
success = 0
for vid, title in PRIORITY_VIDEOS:
    srt = os.path.exists(f'{SUBS_DIR}/{vid}.ko.srt')
    vtt = os.path.exists(f'{SUBS_DIR}/{vid}.ko.vtt')
    jsn = os.path.exists(f'{SUBS_DIR}/{vid}_transcript.json')
    status = "✅ OK" if (srt or vtt or jsn) else "❌ FAILED"
    if srt or vtt or jsn:
        success += 1
    print(f"  {vid}: {status}")

print(f"\nTotal success: {success}/{len(PRIORITY_VIDEOS)}")

if success > 0:
    print("\n🎉 Got some subtitles! Starting V9 analysis...")
    # TODO: Start V9 analysis on successful downloads
else:
    print("\n😞 No subtitles obtained. Need different approach.")