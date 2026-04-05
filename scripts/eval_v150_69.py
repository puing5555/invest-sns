# -*- coding: utf-8 -*-
"""
V14.0 vs V15.0 Eval (69건, Sonnet + GPT-4o)

V15.0: 비종목 시그널 제외 + 타인 인용 speaker 구분

사용법:
  cd invest-sns
  PYTHONIOENCODING=utf-8 python scripts/eval_v150_69.py
"""

import json, os, sys, time
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

env_path = Path(__file__).parent.parent / '.env.local'
if env_path.exists():
    for line in env_path.read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())

ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY')
OPENAI_KEY = os.environ.get('OPENAI_API_KEY')
if not ANTHROPIC_KEY:
    print("ANTHROPIC_API_KEY not found"); sys.exit(1)
if not OPENAI_KEY:
    print("OPENAI_API_KEY not found"); sys.exit(1)

import anthropic
from openai import OpenAI

sonnet_client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
oai_client = OpenAI(api_key=OPENAI_KEY)


def build_eval_prompt(version):
    """V14.0 / V15.0 eval 프롬프트 생성. 파일이 아닌 인라인 조립."""

    base = """투자 인플루언서의 발언을 분석하여 시그널을 분류하세요.
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

■ 매도 = 직접적 매도 권유"""

    v15_addition = """

⚠️ 개별 종목만 시그널로 추출. 다음은 시그널에서 제외 ("해당없음" 반환):
  - 지수: KOSPI, KOSDAQ, 나스닥, S&P500, 다우존스, 러셀 2000
  - 자산군: 미국 주식, 한국 주식, 중국 주식, 선진국 주식, 신흥국 주식
  - 원자재(현물): 금, 은, 구리, 원유 (단, GLD/SLV 등 ETF는 개별 상품이므로 분류 OK)
  - 일반 카테고리: 알트코인, 소형주, 대형주, 가치주
  - 통화/섹터/비상장/인물
  → 위 항목이 종목으로 주어지면 반드시 {"signal_type": "해당없음"} 반환

⚠️ 타인 인용 구분:
  - "~가 말했다", "~에 따르면", "~가 추천했다" 등 타인 의견 인용
    → 본인 동의 표현 없으면 = 중립
    → 본인 동의 있으면 ("저도 같은 생각", "저도 샀습니다") = 본인 시그널"""

    fewshot = """

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
A: {"signal_type": "매수"} ← 구체적 매매 전략 + "지금 가장 좋을 때\""""

    v15_fewshot_extra = """

Q: 종목=나스닥 / 영상="2026 하반기 전망"
발언: "나스닥은 7월부터 조정 올 수 있다"
A: {"signal_type": "해당없음"} ← 지수는 시그널 대상 아님

Q: 종목=금 / 영상="자산배분 전략"
발언: "레이 달리오가 금을 사라고 했다"
A: {"signal_type": "해당없음"} ← 원자재(현물)는 시그널 대상 아님 + 타인 인용"""

    if version == "v14":
        tail = '\n\n반드시 JSON으로만 응답: {"signal_type": "매수|긍정|중립|부정|매도"}'
        return base + fewshot + tail
    else:  # v15
        tail = '\n\n반드시 JSON으로만 응답: {"signal_type": "매수|긍정|중립|부정|매도|해당없음"}'
        return base + v15_addition + fewshot + v15_fewshot_extra + tail


def classify_sonnet(prompt, stock, key_quote, video_title, retries=2):
    user_msg = f'종목: {stock}\n영상 제목: {video_title}\n발언: "{key_quote}"\n\n이 발언의 시그널 타입을 분류하세요.'
    for attempt in range(retries + 1):
        try:
            r = sonnet_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100, temperature=0,
                system=prompt,
                messages=[{"role": "user", "content": user_msg}]
            )
            text = r.content[0].text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(text).get("signal_type", "중립")
        except Exception as e:
            if attempt < retries: time.sleep(2)
            else:
                print(f"    Sonnet error: {str(e)[:80]}")
                return "중립"


def classify_gpt4o(prompt, stock, key_quote, video_title, retries=2):
    user_msg = f'종목: {stock}\n영상 제목: {video_title}\n발언: "{key_quote}"\n\n이 발언의 시그널 타입을 분류하세요.'
    for attempt in range(retries + 1):
        try:
            r = oai_client.chat.completions.create(
                model="gpt-4o", temperature=0, max_tokens=100,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_msg},
                ],
            )
            text = r.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(text).get("signal_type", "중립")
        except Exception as e:
            if attempt < retries: time.sleep(2)
            else:
                print(f"    GPT-4o error: {str(e)[:80]}")
                return "중립"


def main():
    base = Path(__file__).parent.parent
    gt_path = base / "data" / "eval_ground_truth_69.json"
    cases = json.load(open(gt_path, encoding="utf-8"))
    total = len(cases)

    # V14.0 Sonnet 기존 결과 로드
    v14_path = base / "data" / "eval_v14_results.json"
    v14_data = json.load(open(v14_path, encoding="utf-8"))
    v14_details = v14_data["details"]

    prompt_v15 = build_eval_prompt("v15")

    print("=" * 75)
    print(f"  V14.0 vs V15.0 Eval ({total}건) — Sonnet + GPT-4o")
    print("=" * 75)

    v15_sonnet = []
    v15_gpt4o = []

    for i, c in enumerate(cases):
        stock = c["stock"]
        correct = c["correct"]
        v14_r = v14_details[i]["v14"]

        s15 = classify_sonnet(prompt_v15, stock, c["key_quote"], c["video_title"])
        v15_sonnet.append(s15)

        g15 = classify_gpt4o(prompt_v15, stock, c["key_quote"], c["video_title"])
        v15_gpt4o.append(g15)

        def mark(r): return "O" if r == correct else "X"

        print(f"[{i+1:2d}/{total}] {stock[:10]:10s} ans={correct:3s} "
              f"V14S={v14_r:4s}({mark(v14_r)}) "
              f"V15S={s15:4s}({mark(s15)}) "
              f"V15G={g15:4s}({mark(g15)})")

        time.sleep(0.5)

    # ── 집계 ──
    v14_ok = sum(1 for d in v14_details if d["v14_correct"])
    v15s_ok = sum(1 for i in range(total) if v15_sonnet[i] == cases[i]["correct"])
    v15g_ok = sum(1 for i in range(total) if v15_gpt4o[i] == cases[i]["correct"])

    print(f"\n{'='*75}")
    print(f"  RESULT")
    print(f"{'='*75}")
    print(f"  V14.0 Sonnet: {v14_ok}/{total} ({v14_ok/total*100:.1f}%)")
    print(f"  V15.0 Sonnet: {v15s_ok}/{total} ({v15s_ok/total*100:.1f}%)")
    print(f"  V15.0 GPT-4o: {v15g_ok}/{total} ({v15g_ok/total*100:.1f}%)")

    ds = v15s_ok - v14_ok
    dg = v15g_ok - v14_ok
    print(f"\n  V14->V15 Sonnet: {'+' if ds>=0 else ''}{ds} ({'+' if ds>=0 else ''}{ds/total*100:.1f}%p)")
    print(f"  V14->V15 GPT-4o: {'+' if dg>=0 else ''}{dg} ({'+' if dg>=0 else ''}{dg/total*100:.1f}%p)")

    # ── Group A/B/C ──
    group_a, group_b, group_c = [], [], []
    for i in range(total):
        v14c = v14_details[i]["v14_correct"]
        v15c = v15_sonnet[i] == cases[i]["correct"]
        c = cases[i]
        if not v14c and v15c:
            group_a.append((i, c, v14_details[i]["v14"], v15_sonnet[i]))
        elif v14c and not v15c:
            group_b.append((i, c, v14_details[i]["v14"], v15_sonnet[i]))
        elif not v14c and not v15c:
            group_c.append((i, c, v14_details[i]["v14"], v15_sonnet[i]))

    if group_a:
        print(f"\n  +++ Group A: V15 newly correct ({len(group_a)}) +++")
        for idx, c, v14, v15 in group_a:
            print(f"    {c['stock']:12s} ans={c['correct']:3s} V14={v14:4s}->V15={v15:4s} [{c['reason_cat']}]")
    if group_b:
        print(f"\n  --- Group B: V15 regression ({len(group_b)}) ---")
        for idx, c, v14, v15 in group_b:
            print(f"    {c['stock']:12s} ans={c['correct']:3s} V14={v14:4s}->V15={v15:4s} [{c['reason_cat']}]")
    if group_c:
        print(f"\n  ~~~ Group C: both wrong ({len(group_c)}) ~~~")
        for idx, c, v14, v15 in group_c:
            print(f"    {c['stock']:12s} ans={c['correct']:3s} V14={v14:4s} V15S={v15:4s} V15G={v15_gpt4o[idx]:4s} [{c['reason_cat']}]")

    # ── "해당없음" false positive 체크 ──
    na_s = sum(1 for r in v15_sonnet if r == "해당없음")
    na_g = sum(1 for r in v15_gpt4o if r == "해당없음")
    if na_s or na_g:
        print(f"\n  !! '해당없음' false positive: Sonnet={na_s}, GPT-4o={na_g}")
        for i in range(total):
            if v15_sonnet[i] == "해당없음" or v15_gpt4o[i] == "해당없음":
                print(f"     {cases[i]['stock']:12s} V15S={v15_sonnet[i]:5s} V15G={v15_gpt4o[i]:5s}")

    # ── 저장 ──
    out = {
        "ts": datetime.now().isoformat(),
        "total": total,
        "v14_sonnet": round(v14_ok / total * 100, 1),
        "v15_sonnet": round(v15s_ok / total * 100, 1),
        "v15_gpt4o": round(v15g_ok / total * 100, 1),
        "delta_sonnet": round(ds / total * 100, 1),
        "delta_gpt4o": round(dg / total * 100, 1),
        "group_a": len(group_a),
        "group_b": len(group_b),
        "group_c": len(group_c),
        "details": [
            {
                "stock": cases[i]["stock"],
                "correct": cases[i]["correct"],
                "v14_sonnet": v14_details[i]["v14"],
                "v15_sonnet": v15_sonnet[i],
                "v15_gpt4o": v15_gpt4o[i],
                "reason_cat": cases[i]["reason_cat"],
                "v14_correct": v14_details[i]["v14_correct"],
                "v15s_correct": v15_sonnet[i] == cases[i]["correct"],
                "v15g_correct": v15_gpt4o[i] == cases[i]["correct"],
            }
            for i in range(total)
        ],
    }
    out_path = base / "data" / "eval_v150_results.json"
    json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n  Saved: {out_path}")


if __name__ == "__main__":
    main()
