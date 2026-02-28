"""최후의 수단들 (Unicode 수정)"""
import subprocess, sys, os, time, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

VID = 'ksA4IT452_4'
SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

print("=== Method 4: Last Resort Attempts ===")

# Method 4a: yt-dlp with different extractors
print("\n--- 4a: yt-dlp different extractors ---")

extractors = [
    '',  # default
    '--extractor-args youtube:player_client=web',
    '--extractor-args youtube:player_client=android',
]

for i, extractor_arg in enumerate(extractors):
    print(f"\nTrying extractor {i+1}/{len(extractors)}...")
    
    cmd = [sys.executable, '-m', 'yt_dlp',
           '--write-auto-sub', '--sub-lang', 'ko', '--skip-download',
           '--sleep-interval', '15', '--max-sleep-interval', '30',
           '-o', f'{SUBS_DIR}/{VID}']
    
    if extractor_arg:
        cmd.append(extractor_arg)
    
    cmd.append(f'https://www.youtube.com/watch?v={VID}')
    
    try:
        print(f"  Running yt-dlp...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90, encoding='utf-8', errors='ignore')
        
        if os.path.exists(f'{SUBS_DIR}/{VID}.ko.srt') or os.path.exists(f'{SUBS_DIR}/{VID}.ko.vtt'):
            print(f"  SUCCESS with extractor {i+1}!")
            break
        else:
            stderr_short = result.stderr[:100] if result.stderr else 'No error'
            print(f"  FAIL: {stderr_short}")
            
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT")
    except Exception as e:
        print(f"  ERROR: {str(e)[:50]}")
    
    print("  Waiting 10s...")
    time.sleep(10)

# Quick check if we got anything
print(f"\n=== QUICK CHECK ===")
found = False
for ext in ['srt', 'vtt']:
    path = f'{SUBS_DIR}/{VID}.ko.{ext}'
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"  FOUND: {VID}.ko.{ext} ({size} bytes)")
        found = True

if found:
    print(f"  SUCCESS! Subtitle downloaded")
else:
    print(f"  No subtitles found yet. Continuing...")
    
    # Method 4b: Try different approach - cookies
    print(f"\n--- 4b: yt-dlp with cookies simulation ---")
    
    cmd = [sys.executable, '-m', 'yt_dlp',
           '--write-auto-sub', '--sub-lang', 'ko', '--skip-download',
           '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
           '--add-header', 'Accept-Language:ko-KR,ko;q=0.9,en;q=0.8',
           '--sleep-interval', '20',
           '-o', f'{SUBS_DIR}/{VID}',
           f'https://www.youtube.com/watch?v={VID}']
    
    try:
        print(f"  Trying with headers...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, encoding='utf-8', errors='ignore')
        
        if os.path.exists(f'{SUBS_DIR}/{VID}.ko.srt') or os.path.exists(f'{SUBS_DIR}/{VID}.ko.vtt'):
            print(f"  SUCCESS with headers!")
            found = True
        else:
            print(f"  FAIL with headers")
            
    except Exception as e:
        print(f"  ERROR: {str(e)[:50]}")

# Final status
print(f"\n=== FINAL STATUS ===")
if found:
    print(f"SUBTITLE DOWNLOAD SUCCESSFUL!")
else:
    print(f"All methods failed. Rate limiting too strong.")