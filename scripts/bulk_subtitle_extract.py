"""
Webshare Proxy + YouTubeTranscriptApi 대량 자막 추출 스크립트
- DB에서 subtitle_text NULL인 영상 추출
- 프록시 통해 자막 다운로드
- Supabase UPDATE
"""
import json, os, sys, time, random, ssl, urllib.request, urllib.parse

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

# === CONFIG ===
WEBSHARE_USER = "pvljrgkf"
WEBSHARE_PASS = "0e0eqk9rbwzq"
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
SUBS_DIR = r"C:\Users\Mario\work\subs"
BATCH_SIZE = 10  # 한 번에 추출할 영상 수
DELAY_MIN = 1    # 영상 간 최소 딜레이 (초)
DELAY_MAX = 3    # 영상 간 최대 딜레이 (초)
SSL_CTX = ssl.create_default_context()

# === SUPABASE HELPERS ===
def supabase_get(table, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}" if params else f"{SUPABASE_URL}/rest/v1/{table}"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    })
    resp = urllib.request.urlopen(req, context=SSL_CTX)
    return json.loads(resp.read())

def supabase_update(table, id_val, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{id_val}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="PATCH", headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    })
    try:
        resp = urllib.request.urlopen(req, context=SSL_CTX)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  DB Error {e.code}: {e.read().decode()[:200]}")
        return None

def main():
    print("=" * 60)
    print("Webshare Proxy 자막 대량 추출")
    print("=" * 60)

    # Init API with proxy
    api = YouTubeTranscriptApi(
        proxy_config=WebshareProxyConfig(
            proxy_username=WEBSHARE_USER,
            proxy_password=WEBSHARE_PASS,
        )
    )
    print("Proxy API initialized\n")

    # Get videos without subtitles
    videos = supabase_get("influencer_videos", "subtitle_text=is.null&select=id,video_id,title,channel_id")
    print(f"Videos without subtitles: {len(videos)}")

    if not videos:
        print("All videos have subtitles!")
        return

    # Process in batches
    success = 0
    fail = 0
    total = min(len(videos), BATCH_SIZE) if BATCH_SIZE > 0 else len(videos)

    for i, vid in enumerate(videos[:total]):
        yt_id = vid["video_id"]
        db_id = vid["id"]
        title = (vid.get("title") or "")[:50]
        print(f"\n[{i+1}/{total}] {yt_id} - {title}")

        try:
            # Fetch transcript
            transcript = api.fetch(yt_id, languages=['ko', 'en'])
            raw = transcript.to_raw_data()

            # Build fulltext
            lines = []
            for seg in raw:
                start = seg.get('start', 0)
                text = seg.get('text', '').strip()
                if text and text != '[Music]':
                    mm = int(start // 60)
                    ss = int(start % 60)
                    lines.append(f"[{mm}:{ss:02d}] {text}")

            fulltext = "\n".join(lines)
            subtitle_text = fulltext[:5000]  # DB 컬럼 길이 제한

            print(f"  OK: {len(raw)} segments, {len(fulltext)} chars")

            # Save to local file
            os.makedirs(SUBS_DIR, exist_ok=True)
            json_path = os.path.join(SUBS_DIR, f"{yt_id}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "video_id": yt_id,
                    "subtitles": raw,
                }, f, ensure_ascii=False, indent=2)

            txt_path = os.path.join(SUBS_DIR, f"{yt_id}_fulltext.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(fulltext)

            # Update DB
            result = supabase_update("influencer_videos", db_id, {
                "subtitle_text": subtitle_text,
                "has_subtitle": True,
                "subtitle_language": "ko",
            })
            if result:
                print(f"  DB updated")
                success += 1
            else:
                print(f"  DB update failed")
                fail += 1

        except Exception as e:
            err = str(e)[:150]
            print(f"  FAIL: {err}")
            fail += 1

            # Rate limit handling
            if '429' in err or 'Too Many' in err:
                print("  Rate limited! Waiting 60s...")
                time.sleep(60)

        # Random delay between videos
        delay = random.uniform(DELAY_MIN, DELAY_MAX)
        print(f"  Waiting {delay:.1f}s...")
        time.sleep(delay)

    print(f"\n{'=' * 60}")
    print(f"DONE: {success} success, {fail} fail, {total} total")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    # Override batch size from command line
    if len(sys.argv) > 1:
        BATCH_SIZE = int(sys.argv[1])
    main()
