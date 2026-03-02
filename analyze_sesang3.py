"""세상학개론 3개 영상 시그널 분석 및 DB INSERT"""
import sys, os, json, requests, time
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / '.env.local')

SUPABASE_URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
SB_HEADERS = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}', 'Content-Type': 'application/json'}

# Load prompt
with open('prompts/pipeline_v10.md', 'r', encoding='utf-8') as f:
    PROMPT_TEMPLATE = f.read()

# Target videos
TARGETS = [
    {'video_id': 'Ke7gQMbIFLI', 'title': '트럼프의 선택에 시장이 패닉하는 이유, 우리도 패닉해야 하나요?'},
    {'video_id': '4wCO1fdl9iU', 'title': '언제 터질지 모르는 버블에 올라타는 심리'},
    {'video_id': '4cCGQFHrbK4', 'title': '제2의 팔란티어, 알고도 10배 못 먹는 이유'},
]

CHANNEL_URL = 'https://www.youtube.com/@sesang101'
CHANNEL_ID = 'd68f8efd-64c8-4c07-9d34-e98c2954f4e1'

def get_speaker_id():
    """세상학개론 speaker_id"""
    return 'b9496a5f-06fa-47eb-bc2d-47060b095534'

def get_subtitle(video_id):
    """DB에서 자막 가져오기"""
    r = requests.get(f'{SUPABASE_URL}/rest/v1/influencer_videos?video_id=eq.{video_id}&select=id,subtitle_text', headers=SB_HEADERS)
    data = r.json()
    if data:
        return data[0]['id'], data[0].get('subtitle_text', '')
    return None, ''

def analyze_with_claude(video_title, video_id, subtitle):
    """Claude Sonnet으로 시그널 분석"""
    prompt = PROMPT_TEMPLATE + f"""

=== 분석 대상 영상 ===
채널: 세상학개론 (@sesang101)
제목: {video_title}
URL: https://www.youtube.com/watch?v={video_id}

=== 자막 내용 ===
{subtitle[:8000]}

위 영상의 자막을 분석하고 시그널을 추출해주세요. JSON 형식으로만 응답하세요.
"""
    
    resp = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers={
            'Content-Type': 'application/json',
            'x-api-key': ANTHROPIC_KEY,
            'anthropic-version': '2023-06-01'
        },
        json={
            'model': 'claude-sonnet-4-20250514',
            'max_tokens': 4096,
            'messages': [{'role': 'user', 'content': prompt}]
        },
        timeout=120
    )
    
    if resp.status_code != 200:
        print(f"  ERROR: {resp.status_code} {resp.text[:200]}")
        return None
    
    text = resp.json()['content'][0]['text']
    
    # Parse JSON
    try:
        if '```json' in text:
            start = text.find('```json') + 7
            end = text.find('```', start)
            return json.loads(text[start:end].strip())
        elif '{' in text:
            start = text.find('{')
            end = text.rfind('}') + 1
            return json.loads(text[start:end])
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        print(f"  Raw: {text[:300]}")
    return None

def validate_signal(s):
    """시그널 기본 검증"""
    valid_types = ['매수', '긍정', '중립', '경계', '매도']
    if s.get('signal_type') not in valid_types:
        return False, f"invalid signal_type: {s.get('signal_type')}"
    if not isinstance(s.get('confidence'), (int, float)) or not (1 <= s['confidence'] <= 10):
        return False, f"invalid confidence: {s.get('confidence')}"
    if not s.get('key_quote') or len(s['key_quote']) < 15:
        return False, f"key_quote too short: {len(s.get('key_quote', ''))}"
    if not s.get('timestamp') or s['timestamp'] in ('0:00', '00:00'):
        return False, f"invalid timestamp: {s.get('timestamp')}"
    return True, "ok"

def main():
    speaker_id = get_speaker_id()
    all_signals = []
    
    for target in TARGETS:
        vid = target['video_id']
        title = target['title']
        print(f"\n{'='*60}")
        print(f"Analyzing: {title}")
        print(f"Video ID: {vid}")
        
        db_uuid, subtitle = get_subtitle(vid)
        if not subtitle or len(subtitle) < 100:
            print(f"  SKIP: subtitle too short ({len(subtitle)} chars)")
            continue
        
        print(f"  Subtitle: {len(subtitle)} chars")
        print(f"  DB UUID: {db_uuid}")
        
        result = analyze_with_claude(title, vid, subtitle)
        if not result:
            print("  FAIL: no result from Claude")
            continue
        
        signals = result.get('signals', [])
        print(f"  Extracted: {len(signals)} signals")
        
        for s in signals:
            valid, reason = validate_signal(s)
            if not valid:
                print(f"  INVALID: {reason}")
                continue
            
            s['_video_uuid'] = db_uuid
            s['_video_id'] = vid
            s['_title'] = title
            all_signals.append(s)
            print(f"  ✅ {s['signal_type']} | {s.get('stock')} ({s.get('ticker')}) | conf:{s['confidence']} | {s['timestamp']}")
        
        time.sleep(2)  # rate limit
    
    # Summary
    print(f"\n{'='*60}")
    print(f"TOTAL SIGNALS: {len(all_signals)}")
    print(f"\n=== APPROVAL LIST ===")
    for i, s in enumerate(all_signals):
        print(f"{i+1}. [{s['_title'][:30]}] {s['signal_type']} | {s.get('stock')} ({s.get('ticker')}) | conf:{s['confidence']} | ts:{s['timestamp']}")
        print(f"   quote: {s['key_quote'][:80]}")
        print(f"   reason: {s.get('reasoning', '')[:80]}")
    
    # Save for review (don't auto-insert)
    with open('sesang3_signals.json', 'w', encoding='utf-8') as f:
        json.dump(all_signals, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to sesang3_signals.json for review")
    print("Run with --insert flag to INSERT into DB")
    
    # INSERT mode
    if '--insert' in sys.argv and speaker_id:
        print(f"\n=== INSERTING {len(all_signals)} signals ===")
        for s in all_signals:
            # Map confidence number to text
            conf_num = int(s['confidence'])
            conf_text = 'high' if conf_num >= 7 else 'medium' if conf_num >= 4 else 'low'
            row = {
                'video_id': s['_video_uuid'],
                'speaker_id': speaker_id,
                'stock': s.get('stock', ''),
                'ticker': s.get('ticker'),
                'signal': s['signal_type'],
                'confidence': conf_text,
                'key_quote': s['key_quote'],
                'reasoning': s.get('reasoning', ''),
                'timestamp': s['timestamp'],
                'review_status': 'pending',
                'pipeline_version': 'V10.7'
            }
            r = requests.post(
                f'{SUPABASE_URL}/rest/v1/influencer_signals',
                headers={**SB_HEADERS, 'Prefer': 'return=representation'},
                json=row
            )
            if r.status_code in (200, 201):
                print(f"  ✅ Inserted: {s.get('stock')} ({s['signal_type']})")
            else:
                print(f"  ❌ Failed: {r.status_code} {r.text[:100]}")

if __name__ == '__main__':
    main()
