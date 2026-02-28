"""온라인 자막 서비스로 다운로드 시도"""
import urllib.request, urllib.parse, json, io, sys, os, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

VID = 'ksA4IT452_4'
SUBS_DIR = 'C:/Users/Mario/work/invest-sns/subs'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def try_downsub():
    """downsub.com 시도"""
    print("=== Method 3a: downsub.com ===")
    
    try:
        # Step 1: Get downsub main page
        url = 'https://downsub.com/'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8')
        
        print(f"  ✅ Main page loaded ({len(html)} bytes)")
        
        # Step 2: Submit video URL
        youtube_url = f'https://www.youtube.com/watch?v={VID}'
        
        # Find form action and any hidden fields
        csrf_match = re.search(r'name=["\']_token["\'] value=["\']([^"\']+)', html)
        action_match = re.search(r'<form[^>]*action=["\']([^"\']*)', html)
        
        csrf_token = csrf_match.group(1) if csrf_match else ''
        form_action = action_match.group(1) if action_match else '/download'
        
        if not form_action.startswith('http'):
            form_action = 'https://downsub.com' + form_action
        
        print(f"  Form action: {form_action}")
        
        # Submit form
        form_data = {
            'url': youtube_url,
        }
        if csrf_token:
            form_data['_token'] = csrf_token
            
        data = urllib.parse.urlencode(form_data).encode()
        req = urllib.request.Request(form_action, data=data, headers=headers)
        
        with urllib.request.urlopen(req, timeout=20) as resp:
            result_html = resp.read().decode('utf-8')
        
        print(f"  ✅ Form submitted ({len(result_html)} bytes)")
        
        # Step 3: Look for Korean subtitle download link
        ko_links = re.findall(r'href=["\']([^"\']*)["\'][^>]*>.*?(?:Korean|한국어|ko).*?</a>', result_html, re.IGNORECASE)
        
        if not ko_links:
            # Try broader search
            download_links = re.findall(r'href=["\']([^"\']*\.(?:srt|vtt|txt))["\']', result_html)
            ko_links = [link for link in download_links if 'ko' in link.lower()]
        
        print(f"  Found {len(ko_links)} potential Korean links")
        
        if ko_links:
            download_url = ko_links[0]
            if not download_url.startswith('http'):
                download_url = 'https://downsub.com' + download_url
                
            print(f"  Downloading: {download_url}")
            
            req = urllib.request.Request(download_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                subtitle_content = resp.read().decode('utf-8')
            
            # Save as SRT
            srt_path = f'{SUBS_DIR}/{VID}.ko.srt'
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(subtitle_content)
                
            print(f"  ✅ SUCCESS! Saved {len(subtitle_content)} chars to SRT")
            return True
        else:
            print(f"  ❌ No Korean subtitles found")
            return False
            
    except Exception as e:
        print(f"  ❌ downsub.com failed: {e}")
        return False

def try_savesubs():
    """savesubs.com 시도"""
    print("\n=== Method 3b: savesubs.com ===")
    
    try:
        # Step 1: Get main page
        url = 'https://savesubs.com/'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8')
        
        print(f"  ✅ Main page loaded ({len(html)} bytes)")
        
        # Step 2: Submit video URL
        youtube_url = f'https://www.youtube.com/watch?v={VID}'
        
        # Look for form
        form_data = {
            'url': youtube_url,
        }
        
        data = urllib.parse.urlencode(form_data).encode()
        
        # Try common endpoints
        endpoints = ['/download', '/api/download', '/submit']
        
        for endpoint in endpoints:
            try:
                submit_url = 'https://savesubs.com' + endpoint
                req = urllib.request.Request(submit_url, data=data, headers=headers)
                
                with urllib.request.urlopen(req, timeout=20) as resp:
                    result = resp.read().decode('utf-8')
                
                print(f"  ✅ {endpoint} responded ({len(result)} bytes)")
                
                # Look for download links
                if '.srt' in result or '.vtt' in result:
                    ko_links = re.findall(r'href=["\']([^"\']*(?:ko|korean)[^"\']*\.(?:srt|vtt))["\']', result, re.IGNORECASE)
                    
                    if ko_links:
                        download_url = ko_links[0]
                        if not download_url.startswith('http'):
                            download_url = 'https://savesubs.com' + download_url
                            
                        req = urllib.request.Request(download_url, headers=headers)
                        with urllib.request.urlopen(req, timeout=15) as resp:
                            subtitle_content = resp.read().decode('utf-8')
                        
                        srt_path = f'{SUBS_DIR}/{VID}.ko.srt'
                        with open(srt_path, 'w', encoding='utf-8') as f:
                            f.write(subtitle_content)
                            
                        print(f"  ✅ SUCCESS! Saved {len(subtitle_content)} chars")
                        return True
                        
            except Exception as e:
                print(f"  ❌ {endpoint}: {e}")
                continue
                
        print(f"  ❌ All endpoints failed")
        return False
        
    except Exception as e:
        print(f"  ❌ savesubs.com failed: {e}")
        return False

# Try both services
success = try_downsub()
if not success:
    success = try_savesubs()

if success:
    print(f"\n🎉 SUCCESS! Subtitle downloaded")
else:
    print(f"\n❌ All online services failed")