"""
V12.3 vs V14.0 프롬프트 Eval 비교 (69건)

V14.0 핵심 변경:
  - 영상 맥락 판별 규칙 추가 (직접 분석 vs 보조 예시)
  - V13 효과 유지 (단순사례인용, 리스크≠부정, 매수vs긍정)
  - few-shot 예시 11개

사용법:
  cd invest-sns
  PYTHONIOENCODING=utf-8 python scripts/eval_v14_compare.py
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


PROMPT_V14_0 = """투자 인플루언서의 발언을 분석하여 시그널을 분류하세요.
시그널 타입: 매수/긍정/중립/부정/매도

■ 매수 = 강한 확신 + 투자 권유.
  "사라", "매수 추천", "추천한 거예요", "지금 들어가야", 본인 매매 공개.
  구체적 매매 전략 + "지금이 좋다": "DCA 전략으로 지금 가장 좋을 때다"
  ❌ "~해 보시면 좋을 것 같다", "담아보시면", "소개해 드리고 싶습니다" → 긍정

■ 긍정 = 호의적이지만 직접 매수 권유 없음.
  - 영상이 해당 종목을 직접 분석하며 성장성/매력을 호의적으로 서술 → 긍정
  - "좋은 종목", "전망 밝다", "관심 가져볼 만하다"
  - "~하면 좋겠다", "담아 보시면", "소개해 드리고 싶습니다" → 긍정 (매수 아님)

■ 중립 = 단순 소개, 방향성 없음, 또는 아래 해당:
  - 단순 사례 인용: 다른 주제 영상에서 보조 예시로만 언급
  - 비교 대조군으로만 사용
  - 진행자의 질문 (게스트 답변이 아닌 질문 자체)
  - 교육/홍보 맥락
  - 기술/산업 현황의 객관적 설명 (투자 의견 없음)
  ⚠️ 핵심: "영상이 이 종목에 대해 투자 관점의 분석을 하는가, 다른 얘기의 보조로 잠깐 언급한 것인가?"
  → 직접 분석 + 호의적 서술 = 긍정 / 보조 예시 = 중립

■ 부정 = 확정적 하락 전망 선언 + 투자 회피 권고만.
  ❌ 리스크 분석, 우려, 가능성 제기, 경고, 비유적 표현 → 중립
  ✅ "빠질 것이다 팔아라", "투자하지 마세요" → 부정

■ 매도 = 직접적 매도 권유

## 판별 예시

Q: 종목=엔비디아 / 영상="삼성전자의 진짜 위기는 이것!"
발언: "엔비디아가 완전 칩에서 팍 최고봉으로 갔고"
A: {"signal_type": "중립"} ← 삼성전자 영상에서 비교 예시

Q: 종목=테슬라 / 영상="테슬라 미중기술패권쟁의 희생양이 될것인가?"
발언: "테슬라 성공사례는 중국 지방정부 중심으로 이루어진 통제의 발전 정책이 실사구시적으로 이루어지고 있다"
A: {"signal_type": "중립"} ← 중국 정책 설명의 보조 사례

Q: 종목=삼성전자 / 영상="50년에 한 번 올 기회! 2026 3대 메가트렌드"
발언: "교수님 지금 AI 주가 과연 버블일까요?"
A: {"signal_type": "중립"} ← 진행자 질문, 투자 의견 아님

Q: 종목=삼성전자 / 영상="삼성전자의 진짜 위기는 이것!"
발언: "삼성전자 3만 원대 주식으로 갈 수도 있는 거죠"
A: {"signal_type": "중립"} ← "~수도 있다" 가능성 제기, 확정 아님

Q: 종목=삼성전자 / 영상="이런 시기에 리스크 관리..."
발언: "삼성전자 얘네는 외국인이 가장 쉽게 가져가고 쉽게 빠져나가는 ATM기입니다"
A: {"signal_type": "중립"} ← 리스크 분석, 확정 하락 선언 아님

Q: 종목=알리바바 / 영상="딥시크 수혜 6개 기업! 지금 투자해야 하나?"
발언: "알리바바 같은 경우에는 자체 LM 모델을 가지고 있습니다. AI 전쟁에 뛰어들어서 성과를 시장이 기다리고 있는 상황"
A: {"signal_type": "긍정"} ← 영상이 해당 종목을 직접 분석, 호의적 평가

Q: 종목=CATL / 영상="앞으로 더 오른다! 세계 1등 기업의 주가가 고작 3만원?"
발언: "닝더시 같은 경우는 해외 진출이 핵심이에요"
A: {"signal_type": "긍정"} ← 영상이 해당 종목을 직접 분석

Q: 종목=타이거 차이나테크 탑 10 ETF / 영상="이제는 타이밍 문제다! 중국 테크"
발언: "포트폴리오에 타이거 차이나테크 탑 10 ETF를 꼭 한번 담아 보시면 좋을 것 같습니다"
A: {"signal_type": "긍정"} ← "담아 보시면 좋을 것 같습니다" = 제안 수준

Q: 종목=화웨이 / 영상="테슬라 미중기술패권쟁의 희생양이 될것인가?"
발언: "화웨이가 테슬라의 가장 강력한 경쟁 대상이 될 것"
A: {"signal_type": "긍정"} ← 화웨이의 경쟁력을 직접 평가

Q: 종목=비트코인 / 영상="솔라나 향후 우상향 가능성"
발언: "제가 그래서 여러분들한테 비트코인을 추천한 거예요"
A: {"signal_type": "매수"} ← "추천한 거예요" = 직접 추천

Q: 종목=비트코인 / 영상="네이버 두나무 합병! 투자 전략은?"
발언: "비트코인은 하락할 때는 무조건 빅셀이다. DCA 전략으로 지금 가장 좋을 때다"
A: {"signal_type": "매수"} ← 구체적 매매 전략 + "지금 가장 좋을 때"

반드시 JSON으로만 응답: {"signal_type": "매수|긍정|중립|부정|매도"}"""


def classify(system_prompt, stock, key_quote, video_title, retries=2):
    user_msg = f'종목: {stock}\n영상 제목: {video_title}\n발언: "{key_quote}"\n\n이 발언의 시그널 타입을 분류하세요.'
    for attempt in range(retries + 1):
        try:
            r = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100,
                temperature=0,
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
    print(f"  V12.3 vs V14.0 Eval ({total}건)")
    print("=" * 65)

    v14_results = []

    for i, c in enumerate(cases):
        print(f"[{i+1:2d}/{total}] {c['stock'][:8]:8s}", end=" ")

        v14 = classify(PROMPT_V14_0, c["stock"], c["key_quote"], c["video_title"])

        correct = c["correct"]
        v12 = c["v12_result"]

        def mark(r): return "O" if r == correct else "X"
        print(f"정답={correct:3s} V12.3={v12:3s}({mark(v12)}) V14.0={v14:3s}({mark(v14)})")

        v14_results.append(v14)
        time.sleep(0.3)

    v12_ok = sum(1 for c in cases if c["v12_result"] == c["correct"])
    v14_ok = sum(1 for i in range(total) if v14_results[i] == cases[i]["correct"])

    print(f"\n{'=' * 65}")
    print(f"  RESULT")
    print(f"{'=' * 65}")
    print(f"  V12.3: {v12_ok}/{total} ({v12_ok/total*100:.1f}%)")
    print(f"  V14.0: {v14_ok}/{total} ({v14_ok/total*100:.1f}%)")
    delta = v14_ok - v12_ok
    print(f"  V12.3→V14.0: {'+' if delta>=0 else ''}{delta}건 ({'+' if delta>=0 else ''}{delta/total*100:.1f}%p)")

    # New corrections / regressions
    new_ok = [(i, cases[i]) for i in range(total) if v14_results[i] == cases[i]["correct"] and cases[i]["v12_result"] != cases[i]["correct"]]
    new_ng = [(i, cases[i]) for i in range(total) if v14_results[i] != cases[i]["correct"] and cases[i]["v12_result"] == cases[i]["correct"]]
    both_ok = sum(1 for i in range(total) if v14_results[i] == cases[i]["correct"] and cases[i]["v12_result"] == cases[i]["correct"])
    both_ng = [(i, cases[i]) for i in range(total) if v14_results[i] != cases[i]["correct"] and cases[i]["v12_result"] != cases[i]["correct"]]

    print(f"\n  Both correct: {both_ok}")
    print(f"  Both wrong:   {len(both_ng)}")

    if new_ok:
        print(f"\n  +++ V14 newly correct ({len(new_ok)}) +++")
        for idx, c in new_ok:
            print(f"    {c['stock']}: {c['v12_result']}->{v14_results[idx]} (ans={c['correct']}) [{c['reason_cat']}]")
    if new_ng:
        print(f"\n  --- V14 regression ({len(new_ng)}) ---")
        for idx, c in new_ng:
            print(f"    {c['stock']}: {c['v12_result']}->{v14_results[idx]} (ans={c['correct']}) [{c['reason_cat']}]")
    if both_ng:
        print(f"\n  ~~~ Still wrong ({len(both_ng)}) ~~~")
        for idx, c in both_ng:
            print(f"    {c['stock']}: V12={c['v12_result']} V14={v14_results[idx]} (ans={c['correct']}) [{c['reason_cat']}]")

    # Save detailed results
    out = {
        "ts": datetime.now().isoformat(),
        "total": total,
        "v12": round(v12_ok/total*100, 1),
        "v14": round(v14_ok/total*100, 1),
        "delta": round(delta/total*100, 1),
        "new_correct": len(new_ok),
        "regression": len(new_ng),
        "details": [
            {
                "stock": cases[i]["stock"],
                "correct": cases[i]["correct"],
                "v12": cases[i]["v12_result"],
                "v14": v14_results[i],
                "reason_cat": cases[i]["reason_cat"],
                "v14_correct": v14_results[i] == cases[i]["correct"]
            }
            for i in range(total)
        ]
    }
    out_path = Path(__file__).parent.parent / "data" / "eval_v14_results.json"
    json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n  Saved: {out_path}")


if __name__ == "__main__":
    main()
