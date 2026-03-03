"""타임스탬프 교정 v2 - DB subtitle_text [M:SS] 형식 기반"""
import sys, io, os, re, json, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from dotenv import load_dotenv
load_dotenv('.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
HEADERS = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}', 'Content-Type': 'application/json'}

def parse_ts(ts):
    if not ts: return 0
    parts = ts.strip().split(':')
    try:
        if len(parts) == 3: return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
        elif len(parts) == 2: return int(parts[0])*60 + int(parts[1])
        return int(parts[0])
    except: return 0

def secs_to_ts(s):
    m, sec = divmod(s, 60)
    return f"{m}:{sec:02d}"

def find_in_subtitle(sub_text, key_quote):
    """Find key_quote in [M:SS] formatted subtitle, return seconds"""
    if not sub_text or not key_quote:
        return None
    
    kq = key_quote.strip().replace('"','').replace("'",'')
    
    # Try multiple match lengths
    for match_len in [40, 30, 20, 15, 10]:
        search = kq[:match_len]
        if not search:
            continue
        pos = sub_text.find(search)
        if pos == -1:
            # Try without spaces normalization
            search_norm = re.sub(r'\s+', ' ', search)
            sub_norm = re.sub(r'\s+', ' ', sub_text)
            pos_norm = sub_norm.find(search_norm)
            if pos_norm >= 0:
                # Map back approximate position
                pos = pos_norm
                sub_text_for_search = sub_norm
            else:
                continue
        else:
            sub_text_for_search = sub_text
        
        # Look backwards for [M:SS] or [MM:SS] timestamp
        before = sub_text_for_search[:pos]
        # Pattern: [0:00] or [12:34] or [1:23:45]
        ts_matches = re.findall(r'\[(\d+:\d{2}(?::\d{2})?)\]', before)
        if ts_matches:
            last_ts = ts_matches[-1]
            return parse_ts(last_ts)
    
    return None

def main():
    # Get all signals with video subtitle
    r = requests.get(
        SUPABASE_URL + '/rest/v1/influencer_signals?select=id,key_quote,timestamp,video_id,influencer_videos(video_id,subtitle_text,title)&order=created_at.asc&limit=200',
        headers=HEADERS
    )
    signals = r.json()
    print(f"Total signals: {len(signals)}")
    
    corrected = 0
    already_ok = 0
    no_subtitle = 0
    no_match = 0
    corrections = []
    
    for s in signals:
        vid_info = s.get('influencer_videos') or {}
        sub = vid_info.get('subtitle_text') or ''
        kq = s.get('key_quote') or ''
        current_ts = s.get('timestamp') or ''
        title = vid_info.get('title') or ''
        
        if not sub:
            no_subtitle += 1
            continue
        if not kq:
            no_match += 1
            continue
        
        found_secs = find_in_subtitle(sub, kq)
        if found_secs is None:
            no_match += 1
            continue
        
        current_secs = parse_ts(current_ts)
        diff = abs(found_secs - current_secs)
        new_ts = secs_to_ts(found_secs)
        
        if diff < 30:
            already_ok += 1
            continue
        
        # Correct it
        r2 = requests.patch(
            f'{SUPABASE_URL}/rest/v1/influencer_signals?id=eq.{s["id"]}',
            headers={**HEADERS, 'Prefer': 'return=minimal'},
            json={'timestamp': new_ts}
        )
        if r2.ok:
            corrected += 1
            corrections.append({'id': s['id'], 'title': title[:50], 'quote': kq[:50], 'old': current_ts, 'new': new_ts, 'diff': diff})
            print(f"  ✅ {current_ts} → {new_ts} (diff {diff}s) | {kq[:50]}")
        else:
            print(f"  ❌ {s['id']}: {r2.status_code}")
    
    print(f"\n=== 결과 ===")
    print(f"총: {len(signals)} | 교정: {corrected} | 정확: {already_ok} | 자막없음: {no_subtitle} | 매칭실패: {no_match}")
    
    with open('data/timestamp_correction_v2.json', 'w', encoding='utf-8') as f:
        json.dump({'corrected': corrected, 'already_ok': already_ok, 'no_subtitle': no_subtitle, 'no_match': no_match, 'corrections': corrections}, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
