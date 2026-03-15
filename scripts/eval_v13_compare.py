"""
V11.5 vs V12.3 vs V13.0 프롬프트 Eval 비교 (69건 전체)

- V12.3: 이미 결과 있음 (엑셀에서 로드)
- V11.5 + V13.0: Claude Sonnet으로 새로 분류
- 비용: ~$1 (69건 × 2버전 × Sonnet)
- 소요: ~5분

사용법: 
  cd invest-sns
  PYTHONIOENCODING=utf-8 python scripts/eval_v13_compare.py
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

try:
    import anthropic
except ImportError:
    print("pip install anthropic --break-system-packages")
    sys.exit(1)

env_path = Path(__file__).parent.parent / '.env.local'
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line.startswith('ANTHROPIC_API_KEY='):
            os.environ['ANTHROPIC_API_KEY'] = line.split('=', 1)[1].strip()

API_KEY = os.environ.get('ANTHROPIC_API_KEY')
if not API_KEY:
    print("ANTHROPIC_API_KEY not found")
    sys.exit(1)

client = anthropic.Anthropic(api_key=API_KEY)

PROMPT_V11_5 = """투자 인플루언서의 발언을 분석하여 시그널을 분류하세요.
시그널 타입: 매수/긍정/중립/부정/매도

■ 매수 = 발언자가 직접적으로 매수 행동을 권유한 경우만.
  "사라", "매수 추천", "지금 들어가야", "담으세요", 본인 매매 공개 + 추천 맥락.
  핵심: "발언자가 직접 '사라'고 했는가?" → No이면 매수 아님

■ 긍정 = 호의적이지만 직접 매수 권유 없음.
  "좋은 종목", "전망 밝다", "관심 가져볼 만하다"

■ 중립 = 단순 소개, 실적 분석, 방향성 없음.
  뉴스/리포트 전달, 교육적 설명, "지켜보자"

■ 부정 = 명시적 매도 추천 / 하락 전망 선언 / 투자 회피 권고.
  단순 우려/경고/리스크 언급 = 중립

■ 매도 = 직접적 매도 권유

⚠️ 타인 의견 소개 = 중립 (발언자 본인 동의 명시 시만 해당 시그널)
⚠️ 가정형 = 시그널 아님

반드시 JSON으로만 응답: {"signal_type": "매수|긍정|중립|부정|매도"}"""


PROMPT_V13_0 = """투자 인플루언서의 발언을 분석하여 시그널을 분류하세요.
시그널 타입: 매수/긍정/중립/부정/매도

■ 매수 = 강한 확신 + 투자 권유. "사라", "매수 추천", "지금 들어가야", 본인 매매 공개.
  "이건 꼭 가져가야 한다", "핵심 종목이다" (강한 확신 + 행동 유도)
  ❌ "~해 보시면 좋을 것 같다", "담아보시면" → 긍정 (호의적 제안일 뿐)

■ 긍정 = 호의적이지만 직접 매수 권유 없음.
  "좋은 종목", "전망 밝다", "관심 가져볼 만하다"
  "~하면 좋겠다", "생각해 주시면", "포트폴리오에 편입 검토해볼 만하다" → 긍정

■ 중립 = 단순 소개, 실적 분석, 방향성 없음. 반드시 중립인 경우:
  - 단순 사례 인용: 종목이 다른 논점의 보조 예시로만 사용
  - 산업/기술의 객관적 설명 (투자 의견 없음)
  - 비교 대상(대조군)으로만 사용
  - 교육/강의 홍보 맥락
  - 인터뷰 도입부 질문
  핵심: "이 종목에 대한 직접 투자 의견인가, 다른 얘기의 보조 도구인가?"

■ 부정 = 확정적 하락 전망 / 투자 회피 권고만.
  ❌ 리스크 언급, 우려, 경고, 가능성 제기 → 중립
  ❌ 과거 사례로 리스크 경고 = 중립
  ✅ "이 종목은 빠질 것이다, 팔아라" = 부정

■ 매도 = 직접적 매도 권유

반드시 JSON으로만 응답: {"signal_type": "매수|긍정|중립|부정|매도"}"""


def classify(system_prompt, stock, key_quote, video_title, retries=2):
    user_msg = f'종목: {stock}\n영상 제목: {video_title}\n발언: "{key_quote}"\n\n이 발언의 시그널 타입을 분류하세요.'
    for attempt in range(retries + 1):
        try:
            r = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100,
                system=system_prompt,
                messages=[{"role": "user", "content": user_msg}]
            )
            text = r.content[0].text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(text).get("signal_type", "중립")
        except Exception as e:
            if attempt < retries:
                time.sleep(2)
            else:
                return "중립"


def main():
    gt_path = Path(__file__).parent.parent / "data" / "eval_ground_truth_69.json"
    cases = json.load(open(gt_path, encoding="utf-8"))
    total = len(cases)
    
    print("=" * 65)
    print(f"  V11.5 vs V12.3 vs V13.0 Eval ({total}건)")
    print("=" * 65)
    
    v11_results = []
    v13_results = []
    
    for i, c in enumerate(cases):
        print(f"[{i+1:2d}/{total}] {c['stock'][:8]:8s}", end=" ")
        
        v11 = classify(PROMPT_V11_5, c["stock"], c["key_quote"], c["video_title"])
        v13 = classify(PROMPT_V13_0, c["stock"], c["key_quote"], c["video_title"])
        
        correct = c["correct"]
        v12 = c["v12_result"]
        
        def mark(r): return "O" if r == correct else "X"
        print(f"정답={correct:3s} V11.5={v11:3s}({mark(v11)}) V12.3={v12:3s}({mark(v12)}) V13.0={v13:3s}({mark(v13)})")
        
        v11_results.append(v11)
        v13_results.append(v13)
        time.sleep(0.3)
    
    v11_ok = sum(1 for i in range(total) if v11_results[i] == cases[i]["correct"])
    v12_ok = sum(1 for c in cases if c["v12_result"] == c["correct"])
    v13_ok = sum(1 for i in range(total) if v13_results[i] == cases[i]["correct"])
    
    print(f"\n{'=' * 65}")
    print(f"  RESULT")
    print(f"{'=' * 65}")
    print(f"  V11.5: {v11_ok}/{total} ({v11_ok/total*100:.1f}%)")
    print(f"  V12.3: {v12_ok}/{total} ({v12_ok/total*100:.1f}%)")
    print(f"  V13.0: {v13_ok}/{total} ({v13_ok/total*100:.1f}%)")
    print(f"  V12.3→V13.0: {'+' if v13_ok>=v12_ok else ''}{v13_ok-v12_ok}건 ({'+' if v13_ok>=v12_ok else ''}{(v13_ok-v12_ok)/total*100:.1f}%p)")
    
    # New corrections / regressions
    new_ok = [(i, cases[i]) for i in range(total) if v13_results[i] == cases[i]["correct"] and cases[i]["v12_result"] != cases[i]["correct"]]
    new_ng = [(i, cases[i]) for i in range(total) if v13_results[i] != cases[i]["correct"] and cases[i]["v12_result"] == cases[i]["correct"]]
    
    if new_ok:
        print(f"\n  +++ V13 newly correct ({len(new_ok)}) +++")
        for idx, c in new_ok:
            print(f"    {c['stock']}: {c['v12_result']}->{v13_results[idx]} (ans={c['correct']}) [{c['reason_cat']}]")
    if new_ng:
        print(f"\n  --- V13 regression ({len(new_ng)}) ---")
        for idx, c in new_ng:
            print(f"    {c['stock']}: {c['v12_result']}->{v13_results[idx]} (ans={c['correct']}) [{c['reason_cat']}]")
    
    out = {"ts": datetime.now().isoformat(), "total": total,
           "v11": round(v11_ok/total*100,1), "v12": round(v12_ok/total*100,1), "v13": round(v13_ok/total*100,1)}
    out_path = Path(__file__).parent.parent / "data" / "eval_3ver_results.json"
    json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n  Saved: {out_path}")


if __name__ == "__main__":
    main()
