"""833개 시그널 2단계 품질 검증: Haiku → Sonnet"""
import os, json, time, requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))
SB_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SB_KEY = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
ANTH_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTH_KEY:
    # Try system env
    ANTH_KEY = os.environ.get('ANTHROPIC_API_KEY')

SB_HEADERS = {'apikey': SB_KEY, 'Authorization': f'Bearer {SB_KEY}'}

def get_signals():
    resp = requests.get(f'{SB_URL}/rest/v1/influencer_signals?select=id,video_id,stock,ticker,signal,key_quote,reasoning,confidence&limit=1000', headers=SB_HEADERS)
    return resp.json()

def get_videos():
    resp = requests.get(f'{SB_URL}/rest/v1/influencer_videos?select=id,title&limit=1000', headers=SB_HEADERS)
    vids = resp.json()
    return {v['id']: v['title'] for v in vids}

def call_claude(model, prompt):
    resp = requests.post('https://api.anthropic.com/v1/messages', 
        headers={'x-api-key': ANTH_KEY, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'},
        json={'model': model, 'max_tokens': 200, 'messages': [{'role': 'user', 'content': prompt}]}
    )
    if resp.status_code == 429:
        print("Rate limited, waiting 30s...")
        time.sleep(30)
        return call_claude(model, prompt)
    data = resp.json()
    if 'content' in data:
        return data['content'][0]['text']
    print(f"API error: {data}")
    return None

def validate_signal(title, sig, model):
    prompt = f"""다음 시그널의 품질을 검증하세요.

영상 제목: {title}
시그널 종목: {sig['stock']} ({sig.get('ticker','?')})
시그널 타입: {sig.get('signal','?')}
핵심 발언: {sig.get('key_quote','')}
근거: {sig.get('reasoning','')}
confidence: {sig.get('confidence','?')}

판정: 정상/의심/불량. JSON으로만:
{{"verdict": "정상", "reason": "한줄"}}"""
    
    text = call_claude(model, prompt)
    if not text:
        return {"verdict": "error", "reason": "API error"}
    try:
        # Extract JSON from response
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except:
        pass
    return {"verdict": "error", "reason": text[:100]}

def main():
    print("Loading signals...")
    signals = get_signals()
    videos = get_videos()
    print(f"Signals: {len(signals)}, Videos: {len(videos)}")
    
    results = []
    haiku_model = "claude-3-haiku-20240307"
    sonnet_model = "claude-sonnet-4-20250514"
    
    # Phase 1: Haiku
    print("\n=== Phase 1: Haiku Validation ===")
    for i, sig in enumerate(signals):
        title = videos.get(sig.get('video_id'), 'Unknown')
        result = validate_signal(title, sig, haiku_model)
        
        entry = {
            'id': sig['id'],
            'stock': sig['stock'],
            'ticker': sig.get('ticker'),
            'title': title[:80],
            'haiku_verdict': result.get('verdict', 'error'),
            'haiku_reason': result.get('reason', ''),
            'sonnet_verdict': None,
            'sonnet_reason': None,
            'final_verdict': result.get('verdict', 'error')
        }
        results.append(entry)
        
        if (i+1) % 50 == 0:
            verdicts = [r['haiku_verdict'] for r in results]
            print(f"  {i+1}/{len(signals)} | 정상:{verdicts.count('정상')} 의심:{verdicts.count('의심')} 불량:{verdicts.count('불량')} 에러:{verdicts.count('error')}")
        
        time.sleep(2)
    
    # Phase 1 stats
    verdicts = [r['haiku_verdict'] for r in results]
    print(f"\nPhase 1 결과: 정상:{verdicts.count('정상')} 의심:{verdicts.count('의심')} 불량:{verdicts.count('불량')}")
    
    # Phase 2: Sonnet for 의심/불량
    need_sonnet = [r for r in results if r['haiku_verdict'] in ('의심', '불량')]
    print(f"\n=== Phase 2: Sonnet Re-validation ({len(need_sonnet)} signals) ===")
    
    for i, entry in enumerate(need_sonnet):
        sig = next((s for s in signals if s['id'] == entry['id']), None)
        if not sig:
            continue
        title = videos.get(sig.get('video_id'), 'Unknown')
        result = validate_signal(title, sig, sonnet_model)
        
        entry['sonnet_verdict'] = result.get('verdict', 'error')
        entry['sonnet_reason'] = result.get('reason', '')
        entry['final_verdict'] = entry['sonnet_verdict']
        
        if (i+1) % 20 == 0:
            print(f"  {i+1}/{len(need_sonnet)}")
        time.sleep(0.5)
    
    # Save results
    outpath = os.path.join(os.path.dirname(__file__), '..', 'data', 'signal_quality_full_audit.json')
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Generate defects report
    defects = [r for r in results if r['final_verdict'] in ('불량', '의심')]
    reportpath = os.path.join(os.path.dirname(__file__), '..', 'data', 'signal_defects.md')
    with open(reportpath, 'w', encoding='utf-8') as f:
        f.write("# 시그널 불량 리스트\n\n")
        final_verdicts = [r['final_verdict'] for r in results]
        f.write(f"## 통계\n- 정상: {final_verdicts.count('정상')}\n- 의심: {final_verdicts.count('의심')}\n- 불량: {final_verdicts.count('불량')}\n- 에러: {final_verdicts.count('error')}\n\n")
        f.write("## 불량 시그널\n\n")
        for r in defects:
            if r['final_verdict'] == '불량':
                f.write(f"### {r['stock']} ({r.get('ticker','?')})\n")
                f.write(f"- ID: {r['id']}\n- 영상: {r['title']}\n- Haiku: {r['haiku_verdict']} ({r['haiku_reason']})\n")
                if r['sonnet_verdict']:
                    f.write(f"- Sonnet: {r['sonnet_verdict']} ({r['sonnet_reason']})\n")
                f.write("\n")
        f.write("## 의심 시그널\n\n")
        for r in defects:
            if r['final_verdict'] == '의심':
                f.write(f"- **{r['stock']}** | {r['title'][:50]} | {r.get('sonnet_reason') or r['haiku_reason']}\n")
    
    print(f"\n=== 완료 ===")
    print(f"정상: {final_verdicts.count('정상')}")
    print(f"의심: {final_verdicts.count('의심')}")
    print(f"불량: {final_verdicts.count('불량')}")
    print(f"에러: {final_verdicts.count('error')}")
    print(f"결과: {outpath}")
    print(f"리포트: {reportpath}")

if __name__ == '__main__':
    main()
