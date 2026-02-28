"""최후의 수단들"""
import subprocess, sys, os, time

VID = 'ksA4IT452_4'
SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

print("=== Method 4: Last Resort Attempts ===")

# Method 4a: yt-dlp with different format/extractor
print("\n--- 4a: yt-dlp different extractors ---")

extractors = [
    '',  # default
    '--extractor-args youtube:player_client=web',
    '--extractor-args youtube:player_client=android',
    '--extractor-args youtube:player_client=ios',
]

for i, extractor_arg in enumerate(extractors):
    print(f"\nTrying extractor {i+1}/{len(extractors)}...")
    
    cmd = [sys.executable, '-m', 'yt_dlp',
           '--write-auto-sub', '--sub-lang', 'ko', '--skip-download',
           '--sleep-interval', '30', '--max-sleep-interval', '60',
           '-o', f'{SUBS_DIR}/{VID}']
    
    if extractor_arg:
        cmd.append(extractor_arg)
    
    cmd.append(f'https://www.youtube.com/watch?v={VID}')
    
    try:
        print(f"  Running: {' '.join(cmd[-2:])}")  # Show last parts
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if os.path.exists(f'{SUBS_DIR}/{VID}.ko.srt') or os.path.exists(f'{SUBS_DIR}/{VID}.ko.vtt'):
            print(f"  ✅ SUCCESS with extractor {i+1}!")
            print(f"  stdout: {result.stdout[:200]}")
            break
        else:
            print(f"  ❌ Failed. Error: {result.stderr[:100]}")
            
    except subprocess.TimeoutExpired:
        print(f"  ❌ Timeout")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    time.sleep(10)  # Wait between attempts

# Method 4b: Try different YouTube domains
print("\n--- 4b: Different YouTube domains ---")

youtube_domains = [
    'https://www.youtube.com/watch?v=',
    'https://m.youtube.com/watch?v=',
    'https://youtube.com/watch?v=',
    'https://youtu.be/',
]

for domain in youtube_domains:
    print(f"\nTrying domain: {domain}")
    
    cmd = [sys.executable, '-m', 'yt_dlp',
           '--write-auto-sub', '--sub-lang', 'ko', '--skip-download',
           '--user-agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
           '-o', f'{SUBS_DIR}/{VID}',
           f'{domain}{VID}']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        
        if os.path.exists(f'{SUBS_DIR}/{VID}.ko.srt') or os.path.exists(f'{SUBS_DIR}/{VID}.ko.vtt'):
            print(f"  ✅ SUCCESS with domain: {domain}")
            break
        else:
            print(f"  ❌ Failed: {result.stderr[:100]}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    time.sleep(15)

# Method 4c: Try youtube-dl instead of yt-dlp
print("\n--- 4c: youtube-dl fallback ---")

try:
    cmd = [sys.executable, '-m', 'youtube_dl',
           '--write-auto-sub', '--sub-lang', 'ko', '--skip-download',
           '-o', f'{SUBS_DIR}/{VID}',
           f'https://www.youtube.com/watch?v={VID}']
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    if os.path.exists(f'{SUBS_DIR}/{VID}.ko.srt') or os.path.exists(f'{SUBS_DIR}/{VID}.ko.vtt'):
        print(f"  ✅ SUCCESS with youtube-dl!")
    else:
        print(f"  ❌ youtube-dl failed: {result.stderr[:100]}")
        
except Exception as e:
    print(f"  ❌ youtube-dl error: {e}")

# Final check
print(f"\n=== FINAL STATUS ===")
files = ['srt', 'vtt', 'json']
found = False

for ext in files:
    path = f'{SUBS_DIR}/{VID}.ko.{ext}'
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"  ✅ {VID}.ko.{ext}: {size} bytes")
        found = True

if not found:
    print(f"  ❌ No subtitle files created")
else:
    print(f"  🎉 SUBTITLE DOWNLOAD SUCCESSFUL!")