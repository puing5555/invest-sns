"""직접 테스트 - 단일 영상으로 빠른 확인"""
import urllib.request, json, ssl, time

# 가장 중요한 영상 1개로 테스트
VID = 'ksA4IT452_4'
TITLE = '삼성전자 사야 돼요?'

# 이미 추출한 caption URL 사용
CAPTION_URL = "https://www.youtube.com/api/timedtext?v=ksA4IT452_4&ei=aluhabjMGKjq2roPu52Y2Aw&caps=asr&opi=112496729&exp=xpe&xoaf=5&xowf=1&xospf=1&hl=ko&ip=0.0.0.0&ipbits=0&expire=1772207578&sparams=ip,ipbits,expire,v,ei,caps,opi,exp,xoaf&signature=3F75601FD27AF796128048B445E5244770365E4E.986F013B9F50EA3EA9F16939BCA3E2321B55A0B8&key=yt8&kind=asr&lang=ko&fmt=json3"

# SSL 검증 비활성화
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers_sets = [
    # Android app
    {
        'User-Agent': 'com.google.android.youtube/18.48.39 (Linux; U; Android 13) gzip',
        'X-YouTube-Client-Name': '3',
        'X-YouTube-Client-Version': '18.48.39',
    },
    # iOS app
    {
        'User-Agent': 'com.google.ios.youtube/18.48.3 (iPhone14,2; U; CPU iOS 16_0 like Mac OS X)',
        'X-YouTube-Client-Name': '5',
        'X-YouTube-Client-Version': '18.48.3',
    },
    # TV app
    {
        'User-Agent': 'Mozilla/5.0 (SMART-TV; LINUX; Tizen 6.0) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/4.0 Chrome/76.0.3809.146 TV Safari/537.36',
        'X-YouTube-Client-Name': '7',
        'X-YouTube-Client-Version': '1.0',
    },
    # Minimal
    {
        'User-Agent': 'youtube-dl/2023.12.30',
    },
    # Fake bot
    {
        'User-Agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)',
    },
]

print(f"Testing direct access to: {VID} - {TITLE}")

for i, headers in enumerate(headers_sets, 1):
    print(f"\nMethod {i}: {headers.get('User-Agent', 'Unknown')[:50]}...")
    
    try:
        req = urllib.request.Request(CAPTION_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
        events = data.get('events', [])
        if events:
            segments = []
            for evt in events:
                start_ms = evt.get('tStartMs', 0)
                segs = evt.get('segs', [])
                text = ''.join(s.get('utf8', '') for s in segs).strip()
                if text and text != '\n':
                    segments.append({'start': start_ms / 1000.0, 'text': text})
            
            print(f"  ✅ SUCCESS! Got {len(segments)} segments")
            print(f"  Sample: {segments[0]['text'][:50]}..." if segments else "  (no segments)")
            
            # Save it
            output_path = f'C:/Users/Mario/work/invest-sns/subs/{VID}_transcript.json'
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'video_id': VID,
                    'title': TITLE,
                    'segments': segments,
                    'method': f'direct_headers_{i}',
                    'total_chars': sum(len(s['text']) for s in segments)
                }, f, ensure_ascii=False, indent=2)
            
            print(f"  💾 Saved to {output_path}")
            break
            
    except urllib.error.HTTPError as e:
        print(f"  ❌ HTTP {e.code}: {e.reason}")
        if e.code == 429:
            print(f"  💤 Rate limited, waiting 30s...")
            time.sleep(30)
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    time.sleep(5)
else:
    print("\n😞 All direct methods failed")
    
print("\nDone with direct test")