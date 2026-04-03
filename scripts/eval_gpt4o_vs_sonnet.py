# -*- coding: utf-8 -*-
"""
GPT-4o vs Sonnet V14.0 Eval 비교
=================================
동일 V14.0 프롬프트, temperature=0으로 69건 정답지 대비 정확도 비교.
Sonnet 결과는 기존 eval_v14_results.json에서 가져옴.

사용법:
  PYTHONIOENCODING=utf-8 python scripts/eval_gpt4o_vs_sonnet.py

환경변수:
  OPENAI_API_KEY (필수) — .env.local 또는 환경변수
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# ── 환경변수 로드 ──
env_path = Path(__file__).parent.parent / '.env.local'
if env_path.exists():
    for line in env_path.read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())

OPENAI_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_KEY:
    print("OPENAI_API_KEY not found. Set it in .env.local or environment.")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("pip install openai")
    sys.exit(1)

oai_client = OpenAI(api_key=OPENAI_KEY)

# ── V14.0 프롬프트 (Sonnet eval과 동일) ──
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


def classify_gpt4o(stock, key_quote, video_title, retries=2):
    """GPT-4o로 시그널 분류"""
    user_msg = f'종목: {stock}\n영상 제목: {video_title}\n발언: "{key_quote}"\n\n이 발언의 시그널 타입을 분류하세요.'
    for attempt in range(retries + 1):
        try:
            r = oai_client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                max_tokens=100,
                messages=[
                    {"role": "system", "content": PROMPT_V14_0},
                    {"role": "user", "content": user_msg},
                ],
            )
            text = r.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
            result = json.loads(text).get("signal_type", "중립")
            tokens = {
                "prompt": r.usage.prompt_tokens,
                "completion": r.usage.completion_tokens,
                "total": r.usage.total_tokens,
            }
            return result, tokens
        except Exception as e:
            if attempt < retries:
                time.sleep(2)
            else:
                print(f"    GPT-4o error: {str(e)[:80]}")
                return "중립", {"prompt": 0, "completion": 0, "total": 0}


def main():
    base = Path(__file__).parent.parent

    # 1) 정답지 로드
    gt_path = base / "data" / "eval_ground_truth_69.json"
    cases = json.load(open(gt_path, encoding="utf-8"))
    total = len(cases)

    # 2) 기존 Sonnet V14.0 결과 로드
    sonnet_path = base / "data" / "eval_v14_results.json"
    sonnet_data = json.load(open(sonnet_path, encoding="utf-8"))
    sonnet_details = sonnet_data["details"]

    print("=" * 70)
    print(f"  GPT-4o vs Sonnet V14.0 Eval ({total}건, 동일 프롬프트)")
    print("=" * 70)

    # 3) GPT-4o 실행
    gpt_results = []
    gpt_tokens_total = {"prompt": 0, "completion": 0, "total": 0}

    for i, c in enumerate(cases):
        stock = c["stock"]
        correct = c["correct"]
        sonnet_v14 = sonnet_details[i]["v14"]

        gpt_result, tokens = classify_gpt4o(stock, c["key_quote"], c["video_title"])
        gpt_results.append(gpt_result)

        for k in gpt_tokens_total:
            gpt_tokens_total[k] += tokens[k]

        s_mark = "O" if sonnet_v14 == correct else "X"
        g_mark = "O" if gpt_result == correct else "X"

        print(f"[{i+1:2d}/{total}] {stock[:10]:10s} 정답={correct:3s} Sonnet={sonnet_v14:3s}({s_mark}) GPT4o={gpt_result:3s}({g_mark})")

        time.sleep(0.3)

    # 4) 집계
    sonnet_ok = sum(1 for d in sonnet_details if d["v14_correct"])
    gpt_ok = sum(1 for i in range(total) if gpt_results[i] == cases[i]["correct"])

    print(f"\n{'='*70}")
    print(f"  RESULT")
    print(f"{'='*70}")
    print(f"  Sonnet V14.0: {sonnet_ok}/{total} ({sonnet_ok/total*100:.1f}%)")
    print(f"  GPT-4o:       {gpt_ok}/{total} ({gpt_ok/total*100:.1f}%)")
    delta = gpt_ok - sonnet_ok
    print(f"  차이: {'+' if delta>=0 else ''}{delta}건 ({'+' if delta>=0 else ''}{delta/total*100:.1f}%p)")

    # 5) 비용 비교
    # Sonnet: ~$3/1M input, ~$15/1M output
    # GPT-4o: ~$2.50/1M input, ~$10/1M output
    sonnet_input_est = gpt_tokens_total["prompt"]  # 비슷한 토큰 수 가정
    sonnet_output_est = gpt_tokens_total["completion"]
    sonnet_cost = sonnet_input_est * 3 / 1_000_000 + sonnet_output_est * 15 / 1_000_000
    gpt_cost = gpt_tokens_total["prompt"] * 2.5 / 1_000_000 + gpt_tokens_total["completion"] * 10 / 1_000_000

    print(f"\n  === 토큰 & 비용 ===")
    print(f"  GPT-4o 토큰: input={gpt_tokens_total['prompt']:,} output={gpt_tokens_total['completion']:,} total={gpt_tokens_total['total']:,}")
    print(f"  GPT-4o 비용: ${gpt_cost:.4f}")
    print(f"  Sonnet 비용 (추정, 동일 토큰 가정): ${sonnet_cost:.4f}")

    # 6) 모델별 틀린 케이스
    sonnet_wrong = []
    gpt_wrong = []
    both_wrong = []
    gpt_only_correct = []
    sonnet_only_correct = []

    for i in range(total):
        s_ok = sonnet_details[i]["v14_correct"]
        g_ok = gpt_results[i] == cases[i]["correct"]
        c = cases[i]
        if not s_ok and not g_ok:
            both_wrong.append((i, c, sonnet_details[i]["v14"], gpt_results[i]))
        elif not s_ok and g_ok:
            gpt_only_correct.append((i, c, sonnet_details[i]["v14"], gpt_results[i]))
        elif s_ok and not g_ok:
            sonnet_only_correct.append((i, c, sonnet_details[i]["v14"], gpt_results[i]))

    if gpt_only_correct:
        print(f"\n  +++ GPT-4o만 정답 ({len(gpt_only_correct)}건) +++")
        for idx, c, s, g in gpt_only_correct:
            print(f"    {c['stock']:12s} 정답={c['correct']:3s} Sonnet={s:3s} GPT4o={g:3s} [{c['reason_cat']}]")

    if sonnet_only_correct:
        print(f"\n  --- Sonnet만 정답 ({len(sonnet_only_correct)}건) ---")
        for idx, c, s, g in sonnet_only_correct:
            print(f"    {c['stock']:12s} 정답={c['correct']:3s} Sonnet={s:3s} GPT4o={g:3s} [{c['reason_cat']}]")

    if both_wrong:
        print(f"\n  ~~~ 둘 다 오답 ({len(both_wrong)}건) ~~~")
        for idx, c, s, g in both_wrong:
            print(f"    {c['stock']:12s} 정답={c['correct']:3s} Sonnet={s:3s} GPT4o={g:3s} [{c['reason_cat']}]")

    # 7) 결과 저장
    out = {
        "ts": datetime.now().isoformat(),
        "total": total,
        "sonnet_accuracy": round(sonnet_ok / total * 100, 1),
        "gpt4o_accuracy": round(gpt_ok / total * 100, 1),
        "delta": round(delta / total * 100, 1),
        "gpt4o_tokens": gpt_tokens_total,
        "gpt4o_cost_usd": round(gpt_cost, 4),
        "sonnet_cost_est_usd": round(sonnet_cost, 4),
        "details": [
            {
                "stock": cases[i]["stock"],
                "correct": cases[i]["correct"],
                "sonnet": sonnet_details[i]["v14"],
                "gpt4o": gpt_results[i],
                "reason_cat": cases[i]["reason_cat"],
                "sonnet_correct": sonnet_details[i]["v14_correct"],
                "gpt4o_correct": gpt_results[i] == cases[i]["correct"],
            }
            for i in range(total)
        ],
    }
    out_path = base / "data" / "eval_gpt4o_vs_sonnet.json"
    json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n  Saved: {out_path}")


if __name__ == "__main__":
    main()
