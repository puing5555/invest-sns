"""
Pipeline V9.1 - Influencer Signal Analysis
Reads subtitle files, analyzes with Claude, validates, inserts to Supabase.
"""
import json, os, sys, ssl, uuid, time, re
import urllib.request

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

SUBS_DIR = r"C:\Users\Mario\work\subs"
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
SSL_CTX = ssl.create_default_context()

VALID_SIGNALS = {"留ㅼ닔", "湲띿젙", "以묐┰", "寃쎄퀎", "留ㅻ룄"}
VALID_MARKETS = {"KR", "US", "US_ADR", "CRYPTO", "CRYPTO_DEFI", "SECTOR", "INDEX", "ETF", "OTHER"}
VALID_MENTION_TYPES = {"寃곕줎", "?쇨굅", "?댁뒪", "由ы룷??, "援먯쑁", "?곗?", "蹂댁쑀", "而⑥꽱?쒖뒪", "?몃Т", "李⑥씡嫄곕옒", "?쒕굹由ъ삤"}
VALID_CONFIDENCE = {"very_high", "high", "medium", "low", "very_low"}

# Channel mapping for sub files
CHANNEL_MAP = {
    "booread": {"name": "遺?쎈궓TV", "handle": "@buiknam_tv", "url": "https://www.youtube.com/@buiknam_tv"},
    "booreadman": {"name": "遺?쎈궓TV", "handle": "@buiknam_tv", "url": "https://www.youtube.com/@buiknam_tv"},
    "dalrant": {"name": "?щ??명닾??, "handle": "@dalrant", "url": "https://www.youtube.com/@dalrant"},
    "hyoseok": {"name": "?댄슚?앹븘移대뜲誘?, "handle": "@hyoseok_academy", "url": "https://www.youtube.com/@hyoseok_academy"},
    "syuka": {"name": "?덉뭅?붾뱶", "handle": "@syukasworld", "url": "https://www.youtube.com/@syukasworld"},
}

def supabase_request(method, table, data=None, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}" if params else f"{SUPABASE_URL}/rest/v1/{table}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method, headers={
        "apikey": ANON_KEY,
        "Authorization": f"Bearer {ANON_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    })
    try:
        resp = urllib.request.urlopen(req, context=SSL_CTX)
        return json.loads(resp.read()) if resp.read else []
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(f"  DB Error {e.code}: {err_body[:200]}")
        return None

def supabase_get(table, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}" if params else f"{SUPABASE_URL}/rest/v1/{table}"
    req = urllib.request.Request(url, headers={
        "apikey": ANON_KEY,
        "Authorization": f"Bearer {ANON_KEY}",
    })
    resp = urllib.request.urlopen(req, context=SSL_CTX)
    return json.loads(resp.read())

def call_claude(system_prompt, user_prompt, max_tokens=4096):
    """Call Claude API"""
    url = "https://api.anthropic.com/v1/messages"
    data = {
        "model": "claude-sonnet-4-6",
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    })
    resp = urllib.request.urlopen(req, context=SSL_CTX, timeout=120)
    result = json.loads(resp.read())
    return result["content"][0]["text"]

def load_subtitle(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        d = json.load(f)
    subs = d.get('subtitles', d.get('segments', []))
    # Build transcript text with timestamps
    lines = []
    for s in subs:
        start = s.get('start', 0)
        text = s.get('text', '')
        if not text.strip() or text.strip() == '[Music]':
            continue
        mm = int(start // 60)
        ss = int(start % 60)
        lines.append(f"[{mm}:{ss:02d}] {text}")
    return "\n".join(lines), d.get('video_id'), d.get('channel'), d.get('title', '')

def build_analysis_prompt(transcript, channel_name, video_id):
    return f"""?꾨옒 ?좏뒠釉??곸긽???먮쭑??遺꾩꽍?댁꽌 ?ъ옄 ?쒓렇?먯쓣 異붿텧?댁쨾.

梨꾨꼸: {channel_name}
?곸긽 ID: {video_id}

## 洹쒖튃 ?붿빟
- ?쒓렇??5?④퀎留??ъ슜: 留ㅼ닔/湲띿젙/以묐┰/寃쎄퀎/留ㅻ룄
- STRONG_BUY, BUY, SELL ???곷Ц 湲덉?
- 1?곸긽 1醫낅ぉ 1諛쒖뼵??= ?쒓렇??1媛?
- mention_type: 寃곕줎/?쇨굅/?댁뒪/由ы룷??援먯쑁/?곗?/蹂댁쑀/而⑥꽱?쒖뒪/?몃Т/李⑥씡嫄곕옒/?쒕굹由ъ삤
- market: KR/US/US_ADR/CRYPTO/CRYPTO_DEFI/SECTOR/INDEX/ETF/OTHER
- confidence: very_high/high/medium/low/very_low
- ?쇨굅 醫낅ぉ? 理쒕? "湲띿젙"源뚯?. "留ㅼ닔" 湲덉?
- 由ы룷???꾨떖(蹂몄씤 ?섍껄 ?놁쓬) = 以묐┰
- ?꾨쭩(~?대떎/?쒕떎/蹂댁씤?? = 湲띿젙, 沅뚯쑀(~?щ씪/?댁븘?? = 留ㅼ닔
- INDEX(肄붿뒪?? S&P500 ?? = ?쒓렇???쒖쇅
- 援먯쑁/?ㅻ챸??= ?쒓렇???쒖쇅
- 議곌굔遺 諛쒖뼵 = confidence medium ?댄븯
- ?좊즺 ?곗? = ?쒓렇???앹꽦 湲덉?
- 硫ㅻ쾭???뚯썝?꾩슜 ?곸긽 = 遺꾩꽍 ?쒖쇅 (?먮쭑 異붿텧 遺덇?)
- ?ㅼ퐫?? ?쒓뎅二쇱떇 + 誘멸뎅二쇱떇 + ?щ┰?좊쭔 (遺?숈궛/?먯옄???댁쇅二쇱떇 ?쒖쇅)
- 諛쒖뼵???대쫫 ?뺢퇋???꾩닔

## 異쒕젰 ?뺤떇 (JSON)
諛섎뱶???꾨옒 ?뺤떇??JSON留?異쒕젰. ?ㅻⅨ ?띿뒪???놁씠 JSON留?
```json
{{
  "video_summary": "?곸긽 ?꾩껜 ?댁슜 ?붿빟 (7-15以? 援ъ껜?곸쑝濡?",
  "signals": [
    {{
      "speaker": "諛쒖뼵???대쫫",
      "stock": "醫낅ぉ紐?,
      "ticker": "醫낅ぉ肄붾뱶 (紐⑤Ⅴ硫?null)",
      "market": "KR/US/...",
      "mention_type": "寃곕줎/?쇨굅/...",
      "signal": "留ㅼ닔/湲띿젙/以묐┰/寃쎄퀎/留ㅻ룄",
      "confidence": "high/medium/low/...",
      "timestamp": "12:34",
      "key_quote": "?듭떖 諛쒖뼵 ?먮Ц",
      "reasoning": "遺꾨쪟 ?댁쑀"
    }}
  ]
}}
```

?쒓렇?먯씠 ?놁쑝硫?signals瑜?鍮?諛곗뿴濡?

## ?먮쭑
{transcript[:15000]}
"""

SYSTEM_PROMPT = """?뱀떊? ?좏뒠釉??ъ옄 ?곸긽 遺꾩꽍 ?꾨Ц媛?낅땲?? ?먮쭑???쎄퀬 V9 ?뚯씠?꾨씪??洹쒖튃???곕씪 ?ъ옄 ?쒓렇?먯쓣 異붿텧?⑸땲??
諛섎뱶???쒖닔 JSON留?異쒕젰?섏꽭?? 留덊겕?ㅼ슫 肄붾뱶釉붾줉(```)???ъ슜?섏? 留덉꽭?? ?쒖닔 JSON ?띿뒪?몃쭔."""

def validate_signals(result):
    """23-item cross validation. Returns list of issues."""
    issues = []
    signals = result.get("signals", [])
    
    for i, sig in enumerate(signals):
        prefix = f"Signal {i+1} ({sig.get('stock','?')})"
        
        # 4. 5?④퀎 ???깃툒
        if sig.get("signal") not in VALID_SIGNALS:
            issues.append(f"{prefix}: Invalid signal '{sig.get('signal')}' - must be 留ㅼ닔/湲띿젙/以묐┰/寃쎄퀎/留ㅻ룄")
        
        # market check
        if sig.get("market") not in VALID_MARKETS:
            issues.append(f"{prefix}: Invalid market '{sig.get('market')}'")
        
        # mention_type check
        if sig.get("mention_type") not in VALID_MENTION_TYPES:
            issues.append(f"{prefix}: Invalid mention_type '{sig.get('mention_type')}'")
        
        # confidence check
        if sig.get("confidence") not in VALID_CONFIDENCE:
            issues.append(f"{prefix}: Invalid confidence '{sig.get('confidence')}'")
        
        # 1. ?쇨굅 vs 寃곕줎 - ?쇨굅??理쒕? 湲띿젙
        if sig.get("mention_type") == "?쇨굅" and sig.get("signal") == "留ㅼ닔":
            issues.append(f"{prefix}: ?쇨굅 醫낅ぉ?몃뜲 留ㅼ닔濡?遺꾨쪟??(理쒕? 湲띿젙)")
        
        # 3. ?댁뒪/由ы룷?몃뒗 以묐┰
        if sig.get("mention_type") in ("?댁뒪", "由ы룷??) and sig.get("signal") not in ("以묐┰",):
            issues.append(f"{prefix}: {sig.get('mention_type')}?몃뜲 signal={sig.get('signal')} (以묐┰?댁뼱????")
        
        # 8. INDEX ?쒓렇???ы븿 ?щ?
        if sig.get("market") == "INDEX":
            issues.append(f"{prefix}: INDEX(吏?? ?쒓렇?먯? ?쒖쇅?댁빞 ??)
        
        # 9. 援먯쑁 ?쒓렇???ы븿 ?щ?
        if sig.get("mention_type") == "援먯쑁":
            issues.append(f"{prefix}: 援먯쑁 肄섑뀗痢좊뒗 ?쒓렇?먯뿉???쒖쇅?댁빞 ??)
        
        # 11. ?곗? ?쒓렇??
        if sig.get("mention_type") == "?곗?" and sig.get("signal") != "以묐┰":
            issues.append(f"{prefix}: ?곗???以묐┰?댁뼱????)
        
        # timestamp check
        if not sig.get("timestamp"):
            issues.append(f"{prefix}: ??꾩뒪?ы봽 ?꾨씫")
        
        # speaker check
        if not sig.get("speaker"):
            issues.append(f"{prefix}: 諛쒖뼵???꾨씫")
    
    # 5. 以묐났 泥댄겕 (媛숈? 諛쒖뼵??+ 醫낅ぉ)
    seen = set()
    for sig in signals:
        key = (sig.get("speaker",""), sig.get("stock",""))
        if key in seen:
            issues.append(f"以묐났: {key[0]} + {key[1]}")
        seen.add(key)
    
    return issues

def get_or_create_channel(channel_info):
    """Get existing channel or create new one"""
    name = channel_info["name"]
    existing = supabase_get("influencer_channels", f"channel_name=eq.{urllib.parse.quote(name)}")
    if existing:
        return existing[0]["id"]
    
    new_ch = {
        "channel_name": name,
        "channel_handle": channel_info.get("handle", ""),
        "channel_url": channel_info.get("url", ""),
        "platform": "youtube",
    }
    result = supabase_request("POST", "influencer_channels", new_ch)
    if result:
        return result[0]["id"]
    return None

def get_or_create_video(video_id, title, channel_id, summary=""):
    """Get existing video or create new one"""
    existing = supabase_get("influencer_videos", f"video_id=eq.{video_id}")
    if existing:
        return existing[0]["id"]
    
    new_vid = {
        "video_id": video_id,
        "title": title or f"?곸긽 {video_id}",
        "channel_id": channel_id,
        "has_subtitle": True,
        "subtitle_language": "ko",
        "pipeline_version": "V9.1",
    }
    result = supabase_request("POST", "influencer_videos", new_vid)
    if result:
        return result[0]["id"]
    return None

def get_or_create_speaker(name):
    """Get existing speaker or create new one"""
    import urllib.parse
    existing = supabase_get("speakers", f"name=eq.{urllib.parse.quote(name)}")
    if existing:
        return existing[0]["id"]
    
    # Check aliases
    all_speakers = supabase_get("speakers")
    for sp in all_speakers:
        if name in (sp.get("aliases") or []):
            return sp["id"]
    
    new_sp = {
        "name": name,
        "aliases": [name],
    }
    result = supabase_request("POST", "speakers", new_sp)
    if result:
        return result[0]["id"]
    return None

def insert_signal(sig, video_db_id, speaker_db_id):
    """Insert a signal into DB"""
    new_sig = {
        "video_id": video_db_id,
        "speaker_id": speaker_db_id,
        "stock": sig["stock"],
        "ticker": sig.get("ticker"),
        "market": sig["market"],
        "mention_type": sig["mention_type"],
        "signal": sig["signal"],
        "confidence": sig["confidence"],
        "timestamp": sig["timestamp"],
        "key_quote": sig.get("key_quote", ""),
        "reasoning": sig.get("reasoning", ""),
        "review_status": "pending",
        "pipeline_version": "V9.1",
    }
    result = supabase_request("POST", "influencer_signals", new_sig)
    return result

def main():
    import urllib.parse
    
    print("=" * 60)
    print("Pipeline V9.1 - Influencer Signal Analysis")
    print("=" * 60)
    
    # Get existing videos in DB
    existing_videos = supabase_get("influencer_videos")
    existing_video_ids = {v["video_id"] for v in existing_videos}
    print(f"\nExisting videos in DB: {len(existing_video_ids)}")
    
    # Get existing signals
    existing_signals = supabase_get("influencer_signals")
    existing_signal_keys = set()
    for s in existing_signals:
        existing_signal_keys.add((s["video_id"], s["speaker_id"], s["stock"]))
    print(f"Existing signals in DB: {len(existing_signals)}")
    
    # Find subtitle files to process
    # Skip files with too few segments (< 50) as they're likely incomplete
    # Skip videos already analyzed with V9+
    files_to_process = []
    for f in sorted(os.listdir(SUBS_DIR)):
        if not f.endswith('.json'):
            continue
        filepath = os.path.join(SUBS_DIR, f)
        with open(filepath, 'r', encoding='utf-8') as fh:
            d = json.load(fh)
        
        # Handle different JSON formats
        if isinstance(d, list):
            subs = d
        elif isinstance(d, dict):
            subs = d.get('subtitles', d.get('segments', []))
        else:
            subs = []
        if len(subs) < 50:
            print(f"  SKIP {f}: too few segments ({len(subs)})")
            continue
        
        # Extract video_id
        if isinstance(d, dict) and 'video_id' in d:
            vid = d['video_id']
        else:
            # Extract from filename
            vid = f.replace('.json', '').split('_', 1)[-1] if '_' in f else f.replace('.json', '')
        # Check if already analyzed with V9
        already_v9 = False
        for ev in existing_videos:
            pipeline_version = ev.get("pipeline_version") or ""
            if ev["video_id"] == vid and pipeline_version.startswith("V9"):
                already_v9 = True
                break
        
        if already_v9:
            print(f"  SKIP {f}: already analyzed with V9")
            continue
        
        prefix = f.split('_')[0]
        ch_info = CHANNEL_MAP.get(prefix)
        if not ch_info:
            print(f"  SKIP {f}: unknown channel prefix '{prefix}'")
            continue
        
        files_to_process.append((f, filepath, vid, ch_info))
    
    print(f"\nFiles to process: {len(files_to_process)}")
    for f, _, vid, ch_info in files_to_process:
        print(f"  {f} -> {ch_info['name']}")
    
    # Process each file
    all_results = []
    total_signals = 0
    
    for f, filepath, vid, ch_info in files_to_process:
        print(f"\n{'='*50}")
        print(f"Processing: {f} (video_id={vid})")
        print(f"Channel: {ch_info['name']}")
        
        transcript, _, _, title = load_subtitle(filepath)
        print(f"  Transcript length: {len(transcript)} chars")
        
        # Call Claude for analysis
        prompt = build_analysis_prompt(transcript, ch_info['name'], vid)
        print(f"  Calling Claude API...")
        
        try:
            response = call_claude(SYSTEM_PROMPT, prompt, max_tokens=4096)
        except Exception as e:
            print(f"  ERROR calling Claude: {e}")
            continue
        
        # Parse JSON response
        try:
            # Strip markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
                cleaned = re.sub(r'\s*```$', '', cleaned)
            result = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"  ERROR parsing JSON: {e}")
            print(f"  Response preview: {response[:300]}")
            continue
        
        signals = result.get("signals", [])
        summary = result.get("video_summary", "")
        print(f"  Summary: {summary[:100]}...")
        print(f"  Signals found: {len(signals)}")
        
        # Validate
        issues = validate_signals(result)
        if issues:
            print(f"  VALIDATION ISSUES ({len(issues)}):")
            for iss in issues:
                print(f"    - {iss}")
            # Remove problematic signals
            clean_signals = []
            for sig in signals:
                has_issue = False
                if sig.get("signal") not in VALID_SIGNALS:
                    has_issue = True
                if sig.get("market") == "INDEX":
                    has_issue = True
                if sig.get("mention_type") == "援먯쑁":
                    has_issue = True
                if not has_issue:
                    clean_signals.append(sig)
            signals = clean_signals
            print(f"  After cleanup: {len(signals)} signals")
        else:
            print(f"  Validation: PASS (0 issues)")
        
        all_results.append({
            "file": f,
            "video_id": vid,
            "channel": ch_info,
            "title": title,
            "summary": summary,
            "signals": signals,
        })
        total_signals += len(signals)
        
        # Print signals
        for sig in signals:
            print(f"  [SIGNAL] {sig['stock']} | {sig['signal']} | {sig['confidence']} | {sig['speaker']} | {sig.get('mention_type','?')}")
        
        time.sleep(1)  # Rate limit
    
    print(f"\n{'='*60}")
    print(f"ANALYSIS COMPLETE")
    print(f"Videos analyzed: {len(all_results)}")
    print(f"Total signals: {total_signals}")
    
    # Save results to file before DB insert
    results_file = os.path.join(r"C:\Users\Mario\work\invest-sns", "pipeline_v9_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"Results saved to {results_file}")
    
    # STEP 3: Insert to Supabase
    print(f"\n{'='*60}")
    print("STEP 3: Supabase INSERT")
    
    inserted_count = 0
    for res in all_results:
        vid = res["video_id"]
        ch_info = res["channel"]
        
        # Get or create channel
        channel_db_id = get_or_create_channel(ch_info)
        if not channel_db_id:
            print(f"  ERROR: Could not get/create channel {ch_info['name']}")
            continue
        
        # Get or create video
        video_db_id = get_or_create_video(vid, res["title"] or res.get("summary","")[:50], channel_db_id, res["summary"])
        if not video_db_id:
            print(f"  ERROR: Could not get/create video {vid}")
            continue
        
        for sig in res["signals"]:
            speaker_name = sig["speaker"]
            speaker_db_id = get_or_create_speaker(speaker_name)
            if not speaker_db_id:
                print(f"  ERROR: Could not get/create speaker {speaker_name}")
                continue
            
            # Check duplicate
            dup_key = (video_db_id, speaker_db_id, sig["stock"])
            if dup_key in existing_signal_keys:
                print(f"  SKIP duplicate: {speaker_name} + {sig['stock']}")
                continue
            
            result = insert_signal(sig, video_db_id, speaker_db_id)
            if result:
                inserted_count += 1
                existing_signal_keys.add(dup_key)
                print(f"  ??Inserted: {sig['stock']} | {sig['signal']} | {speaker_name}")
            else:
                print(f"  ??Failed: {sig['stock']} | {speaker_name}")
    
    print(f"\n{'='*60}")
    print(f"FINAL REPORT")
    print(f"  Videos analyzed: {len(all_results)}")
    print(f"  Total signals extracted: {total_signals}")
    print(f"  Signals inserted to DB: {inserted_count}")
    print(f"  Pipeline version: V9.1")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

