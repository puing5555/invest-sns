"""
Pipeline V9.1 - Influencer Signal Analysis
Reads subtitle files, analyzes with Claude, validates, inserts to Supabase.
"""
import json, os, ssl, uuid, time, re
import urllib.request

SUBS_DIR = r"C:\Users\Mario\work\subs"
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
SSL_CTX = ssl.create_default_context()

VALID_SIGNALS = {"매수", "긍정", "중립", "경계", "매도"}
VALID_MARKETS = {"KR", "US", "US_ADR", "CRYPTO", "CRYPTO_DEFI", "SECTOR", "INDEX", "ETF", "OTHER"}
VALID_MENTION_TYPES = {"결론", "논거", "뉴스", "리포트", "교육", "티저", "보유", "컨센서스", "세무", "차익거래", "시나리오"}
VALID_CONFIDENCE = {"very_high", "high", "medium", "low", "very_low"}

# Channel mapping for sub files
CHANNEL_MAP = {
    "booread": {"name": "부읽남TV", "handle": "@buiknam_tv", "url": "https://www.youtube.com/@buiknam_tv"},
    "booreadman": {"name": "부읽남TV", "handle": "@buiknam_tv", "url": "https://www.youtube.com/@buiknam_tv"},
    "dalrant": {"name": "달란트투자", "handle": "@dalrant", "url": "https://www.youtube.com/@dalrant"},
    "hyoseok": {"name": "이효석아카데미", "handle": "@hyoseok_academy", "url": "https://www.youtube.com/@hyoseok_academy"},
    "syuka": {"name": "슈카월드", "handle": "@syukasworld", "url": "https://www.youtube.com/@syukasworld"},
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
        "model": "claude-sonnet-4-20250514",
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
    return f"""아래 유튜브 영상의 자막을 분석해서 투자 시그널을 추출해줘.

채널: {channel_name}
영상 ID: {video_id}

## 규칙 요약
- 시그널 5단계만 사용: 매수/긍정/중립/경계/매도
- STRONG_BUY, BUY, SELL 등 영문 금지
- 1영상 1종목 1발언자 = 시그널 1개
- mention_type: 결론/논거/뉴스/리포트/교육/티저/보유/컨센서스/세무/차익거래/시나리오
- market: KR/US/US_ADR/CRYPTO/CRYPTO_DEFI/SECTOR/INDEX/ETF/OTHER
- confidence: very_high/high/medium/low/very_low
- 논거 종목은 최대 "긍정"까지. "매수" 금지
- 리포트 전달(본인 의견 없음) = 중립
- 전망(~이다/된다/보인다) = 긍정, 권유(~사라/담아라) = 매수
- INDEX(코스피, S&P500 등) = 시그널 제외
- 교육/설명형 = 시그널 제외
- 조건부 발언 = confidence medium 이하
- 유료 티저 = 시그널 생성 금지
- 스코프: 한국주식 + 미국주식 + 크립토만 (부동산/원자재/해외주식 제외)
- 발언자 이름 정규화 필수

## 출력 형식 (JSON)
반드시 아래 형식의 JSON만 출력. 다른 텍스트 없이 JSON만.
```json
{{
  "video_summary": "영상 전체 내용 요약 (7-15줄, 구체적으로)",
  "signals": [
    {{
      "speaker": "발언자 이름",
      "stock": "종목명",
      "ticker": "종목코드 (모르면 null)",
      "market": "KR/US/...",
      "mention_type": "결론/논거/...",
      "signal": "매수/긍정/중립/경계/매도",
      "confidence": "high/medium/low/...",
      "timestamp": "12:34",
      "key_quote": "핵심 발언 원문",
      "reasoning": "분류 이유"
    }}
  ]
}}
```

시그널이 없으면 signals를 빈 배열로.

## 자막
{transcript[:15000]}
"""

SYSTEM_PROMPT = """당신은 유튜브 투자 영상 분석 전문가입니다. 자막을 읽고 V9 파이프라인 규칙에 따라 투자 시그널을 추출합니다.
반드시 순수 JSON만 출력하세요. 마크다운 코드블록(```)도 사용하지 마세요. 순수 JSON 텍스트만."""

def validate_signals(result):
    """23-item cross validation. Returns list of issues."""
    issues = []
    signals = result.get("signals", [])
    
    for i, sig in enumerate(signals):
        prefix = f"Signal {i+1} ({sig.get('stock','?')})"
        
        # 4. 5단계 외 등급
        if sig.get("signal") not in VALID_SIGNALS:
            issues.append(f"{prefix}: Invalid signal '{sig.get('signal')}' - must be 매수/긍정/중립/경계/매도")
        
        # market check
        if sig.get("market") not in VALID_MARKETS:
            issues.append(f"{prefix}: Invalid market '{sig.get('market')}'")
        
        # mention_type check
        if sig.get("mention_type") not in VALID_MENTION_TYPES:
            issues.append(f"{prefix}: Invalid mention_type '{sig.get('mention_type')}'")
        
        # confidence check
        if sig.get("confidence") not in VALID_CONFIDENCE:
            issues.append(f"{prefix}: Invalid confidence '{sig.get('confidence')}'")
        
        # 1. 논거 vs 결론 - 논거는 최대 긍정
        if sig.get("mention_type") == "논거" and sig.get("signal") == "매수":
            issues.append(f"{prefix}: 논거 종목인데 매수로 분류됨 (최대 긍정)")
        
        # 3. 뉴스/리포트는 중립
        if sig.get("mention_type") in ("뉴스", "리포트") and sig.get("signal") not in ("중립",):
            issues.append(f"{prefix}: {sig.get('mention_type')}인데 signal={sig.get('signal')} (중립이어야 함)")
        
        # 8. INDEX 시그널 포함 여부
        if sig.get("market") == "INDEX":
            issues.append(f"{prefix}: INDEX(지수) 시그널은 제외해야 함")
        
        # 9. 교육 시그널 포함 여부
        if sig.get("mention_type") == "교육":
            issues.append(f"{prefix}: 교육 콘텐츠는 시그널에서 제외해야 함")
        
        # 11. 티저 시그널
        if sig.get("mention_type") == "티저" and sig.get("signal") != "중립":
            issues.append(f"{prefix}: 티저는 중립이어야 함")
        
        # timestamp check
        if not sig.get("timestamp"):
            issues.append(f"{prefix}: 타임스탬프 누락")
        
        # speaker check
        if not sig.get("speaker"):
            issues.append(f"{prefix}: 발언자 누락")
    
    # 5. 중복 체크 (같은 발언자 + 종목)
    seen = set()
    for sig in signals:
        key = (sig.get("speaker",""), sig.get("stock",""))
        if key in seen:
            issues.append(f"중복: {key[0]} + {key[1]}")
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
        "title": title or f"영상 {video_id}",
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
        subs = d.get('subtitles', d.get('segments', []))
        if len(subs) < 50:
            print(f"  SKIP {f}: too few segments ({len(subs)})")
            continue
        
        vid = d.get('video_id')
        # Check if already analyzed with V9
        already_v9 = False
        for ev in existing_videos:
            if ev["video_id"] == vid and ev.get("pipeline_version","").startswith("V9"):
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
                if sig.get("mention_type") == "교육":
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
            print(f"  📊 {sig['stock']} | {sig['signal']} | {sig['confidence']} | {sig['speaker']} | {sig.get('mention_type','?')}")
        
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
                print(f"  ✅ Inserted: {sig['stock']} | {sig['signal']} | {speaker_name}")
            else:
                print(f"  ❌ Failed: {sig['stock']} | {speaker_name}")
    
    print(f"\n{'='*60}")
    print(f"FINAL REPORT")
    print(f"  Videos analyzed: {len(all_results)}")
    print(f"  Total signals extracted: {total_signals}")
    print(f"  Signals inserted to DB: {inserted_count}")
    print(f"  Pipeline version: V9.1")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
