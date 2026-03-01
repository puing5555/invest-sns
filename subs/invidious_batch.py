"""Invidious API로 자막 추출"""
import sys, io, json, os, time, re
import urllib.request, ssl
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

SUBS_DIR = 'C:/Users/Mario/work/subs'
CTX = ssl.create_default_context()

VIDEOS = [
    ('syuka', 'ksA4IT452_4'),
    ('syuka', 'nm5zQxZSkbk'),
    ('syuka', 'XveVkr3JHs4'),
    ('syuka', 'N7xO-UWCM5w'),
    ('hyoseok', 'B5owNUs_DFw'),
    ('hyoseok', 'bmXgryWXNrw'),
    ('dalrant', '5mvn3PfKf9Y'),
]

INSTANCES = [
    'https://inv.nadeko.net',
    'https://invidious.nerdvpn.de',
    'https://inv.tux.pizza',
    'https://invidious.privacyredirect.com',
    'https://iv.datura.network',
]

def get_captions_list(inst, vid):
    url = f'{inst}/api/v1/captions/{vid}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=CTX, timeout=15) as r:
        data = json.loads(r.read().decode('utf-8'))
    return data.get('captions', [])

def download_caption(inst, vid, label):
    """여러 포맷으로 자막 다운로드 시도"""
    encoded_label = urllib.request.quote(label)
    
    # json3 시도
    for fmt in ['json3', 'vtt', 'srv3', '']:
        try:
            fmt_param = f'&fmt={fmt}' if fmt else ''
            url = f'{inst}/api/v1/captions/{vid}?label={encoded_label}{fmt_param}'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=CTX, timeout=20) as r:
                text = r.read().decode('utf-8')
            
            if not text or len(text) < 50:
                continue
            
            if fmt == 'json3':
                return parse_json3(text)
            elif fmt == 'vtt':
                return parse_vtt(text)
            elif fmt == 'srv3':
                return parse_srv3(text)
            else:
                # 자동 감지
                if text.strip().startswith('{'):
                    return parse_json3(text)
                elif 'WEBVTT' in text[:50]:
                    return parse_vtt(text)
                else:
                    return parse_vtt(text)  # fallback
        except Exception as e:
            continue
    
    return None

def parse_json3(text):
    data = json.loads(text)
    events = data.get('events', [])
    segments = []
    for evt in events:
        segs = evt.get('segs', [])
        t = ''.join(s.get('utf8', '') for s in segs).strip()
        if t and t != '\n':
            segments.append({
                'start': evt.get('tStartMs', 0) / 1000.0,
                'duration': evt.get('dDurationMs', 0) / 1000.0,
                'text': t
            })
    return segments

def parse_vtt(text):
    """VTT 파싱"""
    segments = []
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # 타임스탬프 라인: 00:00:01.000 --> 00:00:03.000
        if '-->' in line:
            parts = line.split('-->')
            start = vtt_time_to_sec(parts[0].strip())
            # 다음 줄들이 텍스트
            texts = []
            i += 1
            while i < len(lines) and lines[i].strip() and '-->' not in lines[i]:
                t = re.sub(r'<[^>]+>', '', lines[i].strip())
                if t:
                    texts.append(t)
                i += 1
            if texts:
                segments.append({'start': start, 'duration': 0, 'text': ' '.join(texts)})
            continue
        i += 1
    return segments if segments else None

def parse_srv3(text):
    """SRV3 (XML) 파싱"""
    segments = []
    for match in re.finditer(r'<text start="([^"]+)" dur="([^"]+)"[^>]*>(.*?)</text>', text, re.DOTALL):
        start = float(match.group(1))
        dur = float(match.group(2))
        t = re.sub(r'<[^>]+>', '', match.group(3)).strip()
        t = t.replace('&amp;', '&').replace('&#39;', "'").replace('&quot;', '"')
        if t:
            segments.append({'start': start, 'duration': dur, 'text': t})
    return segments if segments else None

def vtt_time_to_sec(ts):
    parts = ts.replace(',', '.').split(':')
    if len(parts) == 3:
        return float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
    elif len(parts) == 2:
        return float(parts[0])*60 + float(parts[1])
    return 0

def main():
    print("=== Invidious 자막 추출 ===\n")
    
    # 동작하는 인스턴스 찾기
    working_inst = None
    for inst in INSTANCES:
        try:
            caps = get_captions_list(inst, VIDEOS[0][1])
            if caps:
                print(f"Working instance: {inst}")
                working_inst = inst
                break
        except Exception as e:
            print(f"  {inst}: {e}")
    
    if not working_inst:
        print("No working Invidious instance found!")
        return
    
    results = []
    for prefix, vid in VIDEOS:
        out_path = f'{SUBS_DIR}/{prefix}_{vid}.json'
        
        # 이미 있는지 확인
        if os.path.exists(out_path):
            try:
                d = json.load(open(out_path, 'r', encoding='utf-8'))
                segs = d.get('segments', d.get('subtitles', []))
                if segs and len(segs) > 10:
                    print(f"SKIP {vid} ({prefix}): {len(segs)} segs exist")
                    results.append((vid, prefix, len(segs), 'skipped'))
                    continue
            except:
                pass
        
        print(f"EXTRACT {vid} ({prefix}):")
        try:
            # 자막 목록 조회
            caps = get_captions_list(working_inst, vid)
            if not caps:
                print(f"  No captions available")
                results.append((vid, prefix, 0, 'no-caps'))
                time.sleep(2)
                continue
            
            # 한국어 우선
            ko_cap = next((c for c in caps if 'ko' in c.get('languageCode', '').lower()), None)
            cap = ko_cap or caps[0]
            label = cap.get('label', '')
            print(f"  Using: {label}")
            
            segments = download_caption(working_inst, vid, label)
            if segments and len(segments) > 5:
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'video_id': vid,
                        'channel': prefix,
                        'subtitles': segments
                    }, f, ensure_ascii=False, indent=2)
                print(f"  OK: {len(segments)} segments")
                results.append((vid, prefix, len(segments), 'ok'))
            else:
                print(f"  FAIL: got {len(segments) if segments else 0} segments")
                results.append((vid, prefix, 0, 'fail'))
                
                # 다른 인스턴스 시도
                for alt in INSTANCES:
                    if alt == working_inst:
                        continue
                    try:
                        print(f"  Trying alt: {alt}")
                        caps2 = get_captions_list(alt, vid)
                        if caps2:
                            cap2 = next((c for c in caps2 if 'ko' in c.get('languageCode', '').lower()), caps2[0])
                            segs2 = download_caption(alt, vid, cap2.get('label', ''))
                            if segs2 and len(segs2) > 5:
                                with open(out_path, 'w', encoding='utf-8') as f:
                                    json.dump({
                                        'video_id': vid,
                                        'channel': prefix,
                                        'subtitles': segs2
                                    }, f, ensure_ascii=False, indent=2)
                                print(f"  OK (alt): {len(segs2)} segments")
                                results[-1] = (vid, prefix, len(segs2), 'ok')
                                break
                    except:
                        continue
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append((vid, prefix, 0, 'error'))
        
        time.sleep(3)
    
    print(f"\n=== 결과 ===")
    ok = sum(1 for _,_,_,s in results if s in ('ok','skipped'))
    print(f"성공: {ok}/{len(results)}")
    for vid, prefix, count, status in results:
        emoji = '\u2705' if status in ('ok','skipped') else '\u274c'
        print(f"  {emoji} {prefix}/{vid}: {status} ({count} segs)")

if __name__ == '__main__':
    main()
