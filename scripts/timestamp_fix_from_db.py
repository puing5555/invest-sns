"""
기존 시그널 타임스탬프 교정 - DB subtitle_text 기반
"""
import sys, io, os, re, json, requests, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv('.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

def get_all_signals():
    """Get all signals with video info"""
    r = requests.get(
        f'{SUPABASE_URL}/rest/v1/influencer_signals?select=id,key_quote,timestamp,video_id,influencer_videos(video_id,subtitle_text,title)&order=created_at.asc',
        headers=HEADERS
    )
    if not r.ok:
        print(f"Error fetching signals: {r.status_code} {r.text}")
        return []
    return r.json()

def parse_timestamp(ts_str):
    """Parse MM:SS or HH:MM:SS to seconds"""
    if not ts_str:
        return 0
    parts = ts_str.strip().split(':')
    try:
        if len(parts) == 3:
            return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0])*60 + int(parts[1])
        else:
            return int(parts[0])
    except:
        return 0

def seconds_to_mmss(secs):
    """Convert seconds to MM:SS"""
    m = secs // 60
    s = secs % 60
    return f"{m}:{s:02d}"

def find_quote_in_subtitle(subtitle_text, key_quote):
    """Find key_quote position in subtitle_text and extract timestamp"""
    if not subtitle_text or not key_quote:
        return None
    
    # subtitle_text is truncated to 5000 chars, but may have timestamps embedded
    # or it may be plain text. Check format first.
    
    # Try to find the quote (fuzzy match - first 20 chars)
    quote_clean = key_quote.strip().replace('"', '').replace("'", '')
    
    # Try exact substring match first
    if quote_clean[:30] in subtitle_text:
        # Found! But we need to find timestamp context
        # Check if subtitle has VTT-like timestamps
        # Pattern: 00:01:23.456 --> 00:01:25.789
        vtt_pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->'
        
        # Find position of quote in text
        pos = subtitle_text.find(quote_clean[:30])
        
        # Look backwards from pos for a timestamp
        before_text = subtitle_text[:pos]
        timestamps = re.findall(vtt_pattern, before_text)
        if timestamps:
            last_ts = timestamps[-1]  # closest timestamp before the quote
            parts = last_ts.split(':')
            secs = int(parts[0])*3600 + int(parts[1])*60 + float(parts[2])
            return int(secs)
    
    # Try with shorter match (first 15 chars)
    short_quote = quote_clean[:15]
    if short_quote in subtitle_text:
        pos = subtitle_text.find(short_quote)
        before_text = subtitle_text[:pos]
        vtt_pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->'
        timestamps = re.findall(vtt_pattern, before_text)
        if timestamps:
            last_ts = timestamps[-1]
            parts = last_ts.split(':')
            secs = int(parts[0])*3600 + int(parts[1])*60 + float(parts[2])
            return int(secs)
    
    # Try word-level fuzzy match
    words = quote_clean.split()[:5]  # first 5 words
    search = ' '.join(words)
    if search in subtitle_text:
        pos = subtitle_text.find(search)
        before_text = subtitle_text[:pos]
        vtt_pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->'
        timestamps = re.findall(vtt_pattern, before_text)
        if timestamps:
            last_ts = timestamps[-1]
            parts = last_ts.split(':')
            secs = int(parts[0])*3600 + int(parts[1])*60 + float(parts[2])
            return int(secs)
    
    return None

def update_signal_timestamp(signal_id, new_timestamp):
    """Update signal timestamp in DB"""
    r = requests.patch(
        f'{SUPABASE_URL}/rest/v1/influencer_signals?id=eq.{signal_id}',
        headers={**HEADERS, 'Prefer': 'return=minimal'},
        json={'timestamp': new_timestamp}
    )
    return r.ok

def main():
    signals = get_all_signals()
    print(f"Total signals: {len(signals)}")
    
    corrected = 0
    skipped_no_subtitle = 0
    skipped_no_match = 0
    skipped_ok = 0
    errors = 0
    
    results = []
    
    for s in signals:
        sig_id = s['id']
        key_quote = s.get('key_quote', '') or ''
        current_ts = s.get('timestamp', '') or ''
        video_info = s.get('influencer_videos', {}) or {}
        subtitle = video_info.get('subtitle_text', '') or ''
        title = video_info.get('title', '') or ''
        
        if not subtitle:
            skipped_no_subtitle += 1
            continue
        
        if not key_quote:
            skipped_no_match += 1
            continue
        
        # Find quote in subtitle
        found_secs = find_quote_in_subtitle(subtitle, key_quote)
        
        if found_secs is None:
            skipped_no_match += 1
            continue
        
        current_secs = parse_timestamp(current_ts)
        diff = abs(found_secs - current_secs)
        
        new_ts = seconds_to_mmss(found_secs)
        
        if diff < 30:
            skipped_ok += 1
            continue
        
        # Need correction
        results.append({
            'id': sig_id,
            'title': title[:40],
            'quote': key_quote[:40],
            'old': current_ts,
            'new': new_ts,
            'diff': diff
        })
        
        if update_signal_timestamp(sig_id, new_ts):
            corrected += 1
            print(f"  ✅ {current_ts} → {new_ts} (diff {diff}s) | {key_quote[:40]}...")
        else:
            errors += 1
            print(f"  ❌ Failed: {sig_id}")
    
    print(f"\n=== 결과 ===")
    print(f"총 시그널: {len(signals)}")
    print(f"교정됨: {corrected}")
    print(f"이미 정확: {skipped_ok}")
    print(f"자막 없음: {skipped_no_subtitle}")
    print(f"매칭 실패: {skipped_no_match}")
    print(f"에러: {errors}")
    
    # Save report
    with open('data/timestamp_correction_report.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(signals),
            'corrected': corrected,
            'already_ok': skipped_ok,
            'no_subtitle': skipped_no_subtitle,
            'no_match': skipped_no_match,
            'errors': errors,
            'corrections': results
        }, f, ensure_ascii=False, indent=2)
    print("Report saved to data/timestamp_correction_report.json")

if __name__ == '__main__':
    main()
