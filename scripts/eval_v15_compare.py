"""
V14.0 vs V15.1 프롬프트 Eval 비교 (280건 = 안유화 69 + 위즈덤투스 211)

V15.1 핵심 변경:
  - 매수 판별 기준 강화 (본인 보유+확신, 매집/추매, 구어체 행동 지시, 매수가 제시)
  - few-shot 매수 예시 7개 추가 (위즈덤투스 경계 케이스)
  - 긍정→매수 상향 체크리스트 추가

사용법:
  cd invest-sns
  PYTHONIOENCODING=utf-8 python scripts/eval_v15_compare.py
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


PROMPT_V15_1 = """투자 인플루언서의 발언을 분석하여 시그널을 분류하세요.
시그널 타입: 매수/긍정/중립/부정/매도

■ 매수 = 강한 확신 + 투자 권유. 아래 중 하나라도 해당하면 매수:
  1. 직접 매수 권유: "사라", "매수 추천", "지금 들어가야", "분할매수 하라"
  2. 본인 매매 공개: "저는 이 종목 샀습니다/담았습니다"
  3. 본인 매집/추매 공개: "저가 매집했고", "추매를 했거든요", "3차 매수했고"
  4. 본인 보유 + 강한 확신: "갖고 있고 팔 생각이 없다", "매도한 적 없다" + 긍정 전망
  5. 강한 행동 지시: "사야 돼요", "사는 거예요", "꼭 보유하는 게 좋습니다"
  6. 적극 추천: "추천한 거예요", "지금이 기회다", "담아야 될 타이밍"
  7. 구체적 매매 전략 + "지금이 좋다": "DCA 전략으로 지금 가장 좋을 때다"
  ❌ "~해 보시면 좋을 것 같다", "담아보시면", "소개해 드리고 싶습니다" → 긍정

⚠️ 긍정↔매수 판별 체크리스트 (순서대로 확인 — 긍정 유지 조건 먼저!):
  1. 타인 매매 소개인가? ("드러켄밀러가 샀다") → 긍정 (발언자 본인 아님)
  2. 명시적 추천 거부가 있는가? ("추천이 전혀 아니고") → 긍정
  3. 보유 + 유보/조건부 표현인가? ("만약 내려오면", "~되지 않을까", "~오겠죠") → 긍정
  4. 보유 + 단순 현황 보고인가? ("50%로 가고 있습니다", "장투 중이고") → 긍정
  --- 위 1~4에 해당하면 매수 아님 ---
  5. 직접 샀다/매집/추매했다고 말했는가? → 매수
  6. "사야 돼요/사는 거예요" 등 행동 지시인가? → 매수
  7. 보유 + 강한 확신 ("팔 생각 없다", "매도한 적 없다") + 긍정 전망인가? → 매수
  8. 위 어느 것도 아니면 → 긍정

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

Q: 종목=금융섹터ETF / 영상="드러켄밀러 13F 공개"
발언: "XLF 금융 섹터 ETF고 549만 주를 신규로 매수를 했어요. 미국 금융 섹터의 전반이 좋아질 것 같다라는 매크로 배팅을 한 걸로 보이는데"
A: {"signal_type": "긍정"} ← 타인(드러켄밀러) 매매 소개, 발언자 본인이 산 것 아님

Q: 종목=구글 / 영상="시장 급락 대응 전략"
발언: "방어력이 좋았던 구글을 신규 편입을 좀 했습니다. 추천이 전혀 아니고... 현재 기준에서는 가장 앞서 나갈 거 같은 모양을 보여주고 있기는 합니다"
A: {"signal_type": "긍정"} ← 본인 매수했지만 "추천이 전혀 아니고" 명시적 거부

Q: 종목=엔비디아 / 영상="포트폴리오 점검"
발언: "엔비디아는 건드릴 생각은 없는데 만약에 지금 레벨에서 좀 더 내려오면 추매 기회가 되지 않을까 하고 생각하고 있으니까 그냥 보유할 생각입니다."
A: {"signal_type": "긍정"} ← 보유 + "만약/되지 않을까" = 유보/조건부, 매수 아님

Q: 종목=SK하이닉스 / 영상="The next step in the dopamine-fueled market..."
발언: "국장에서는 하이닉스랑 하나 오션만 운봉 이렇게 길게 나오는 날 저가 매집했고요."
A: {"signal_type": "매수"} ← "저가 매집했고요" = 본인 매매 공개

Q: 종목=크라우드스트라이크 / 영상="The next step in the dopamine-fueled market..."
발언: "소프트웨어 주식들 정말 많이 빠졌을 때 추매를 좀 했거든요. 크라우드 스트라이크도 대부를 좀 많이 탔었기 때문에"
A: {"signal_type": "매수"} ← "추매를 했거든요" = 본인 추가 매수 공개

Q: 종목=엔비디아 / 영상="이 기업들만 보면 됩니다"
발언: "제가 엔비디아를 많이 갖고 있는 거고요. 시장 조정이 와도 소형 같은 거는 팔아도 엔비디아는 팔 생각이 별로 없습니다."
A: {"signal_type": "매수"} ← 본인 보유 + "팔 생각이 없다" = 강한 확신

Q: 종목=팔란티어 / 영상="로봇 혁명이 온다"
발언: "담아야 될 타이밍은 엔비디아 팔란티어가 되겠죠. 팔란티어는 진짜 어디다가 갖다 끼어넣어도 들어가는 그런 기업이라고."
A: {"signal_type": "매수"} ← "담아야 될 타이밍" = 매수 타이밍 직접 지목

Q: 종목=코스트코 / 영상="미국주식 실적 점검"
발언: "코스트코 주식이 좋다는 거는 왜냐면 계속 올라. 이런 주식이 세일을 하고 있습니다. 사는 거예요."
A: {"signal_type": "매수"} ← "사는 거예요" = 직접적 매수 행동 지시

Q: 종목=삼성전자 / 영상="반도체 투자 전략"
발언: "삼성전자 하이닉스는 둘 중에 하나는 꼭 보유하는 게 좋습니다. 삼성전자를 더 선호하기는 하는데."
A: {"signal_type": "매수"} ← "꼭 보유하는 게 좋습니다" = 강한 보유 권유

Q: 종목=엔비디아 / 영상="시장 급락 대응 전략"
발언: "94불이면 엔비디아도 사야 돼요. 사야 되고요. 90불 때는 그래도 기회라고 생각을 하고요."
A: {"signal_type": "매수"} ← "사야 돼요" = 구체적 가격 + 강한 행동 지시

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
                print(f"    ERROR: {e}")
                return "중립"


def load_cases():
    """안유화 69건 + 위즈덤투스 211건 = 280건 로드"""
    base = Path(__file__).parent.parent / "data"

    # 안유화 69건
    anyuhwa = json.load(open(base / "eval_ground_truth_69.json", encoding="utf-8"))
    for c in anyuhwa:
        c["source"] = "anyuhwa"

    # 위즈덤투스 211건
    wisdomtooth = json.load(open(base / "eval_ground_truth_wisdomtooth_211.json", encoding="utf-8"))

    return anyuhwa + wisdomtooth


def main():
    cases = load_cases()
    total = len(cases)
    anyuhwa_count = sum(1 for c in cases if c["source"] == "anyuhwa")
    wisdom_count = sum(1 for c in cases if c["source"] == "wisdomtooth")

    print("=" * 70)
    print(f"  V14.0 vs V15.1 Eval ({total}건 = 안유화 {anyuhwa_count} + 위즈덤투스 {wisdom_count})")
    print("=" * 70)

    v14_results = []
    v151_results = []

    for i, c in enumerate(cases):
        stock = c["stock"]
        quote = c["key_quote"]
        title = c.get("video_title", "")
        correct = c["correct"]
        src = c["source"][:3]

        print(f"[{i+1:3d}/{total}] [{src}] {stock[:10]:10s}", end=" ", flush=True)

        v14 = classify(PROMPT_V14_0, stock, quote, title)
        v15 = classify(PROMPT_V15_1, stock, quote, title)

        def mark(r): return "O" if r == correct else "X"
        print(f"정답={correct:3s} V14={v14:3s}({mark(v14)}) V15={v15:3s}({mark(v15)})")

        v14_results.append(v14)
        v151_results.append(v15)
        time.sleep(0.2)

    # === 전체 결과 ===
    v14_ok = sum(1 for i in range(total) if v14_results[i] == cases[i]["correct"])
    v15_ok = sum(1 for i in range(total) if v151_results[i] == cases[i]["correct"])

    print(f"\n{'=' * 70}")
    print(f"  OVERALL RESULT ({total}건)")
    print(f"{'=' * 70}")
    print(f"  V14.0: {v14_ok}/{total} ({v14_ok/total*100:.1f}%)")
    print(f"  V15.1: {v15_ok}/{total} ({v15_ok/total*100:.1f}%)")
    delta = v15_ok - v14_ok
    print(f"  V14→V15: {'+' if delta>=0 else ''}{delta}건 ({'+' if delta>=0 else ''}{delta/total*100:.1f}%p)")

    # === 소스별 결과 ===
    for src_name, src_key in [("안유화", "anyuhwa"), ("위즈덤투스", "wisdomtooth")]:
        idxs = [i for i in range(total) if cases[i]["source"] == src_key]
        n = len(idxs)
        s14 = sum(1 for i in idxs if v14_results[i] == cases[i]["correct"])
        s15 = sum(1 for i in idxs if v151_results[i] == cases[i]["correct"])
        d = s15 - s14
        print(f"\n  [{src_name} {n}건]")
        print(f"    V14.0: {s14}/{n} ({s14/n*100:.1f}%)")
        print(f"    V15.1: {s15}/{n} ({s15/n*100:.1f}%)")
        print(f"    delta: {'+' if d>=0 else ''}{d}건 ({'+' if d>=0 else ''}{d/n*100:.1f}%p)")

    # === 3그룹 분석 ===
    new_ok = [(i, cases[i]) for i in range(total) if v151_results[i] == cases[i]["correct"] and v14_results[i] != cases[i]["correct"]]
    new_ng = [(i, cases[i]) for i in range(total) if v151_results[i] != cases[i]["correct"] and v14_results[i] == cases[i]["correct"]]
    both_ng = [(i, cases[i]) for i in range(total) if v151_results[i] != cases[i]["correct"] and v14_results[i] != cases[i]["correct"]]

    if new_ok:
        print(f"\n  +++ V15 newly correct ({len(new_ok)}) +++")
        for idx, c in new_ok[:20]:
            print(f"    [{c['source'][:3]}] {c['stock']}: {v14_results[idx]}->{v151_results[idx]} (ans={c['correct']})")
        if len(new_ok) > 20:
            print(f"    ... +{len(new_ok)-20}건 더")

    if new_ng:
        print(f"\n  --- V15 regression ({len(new_ng)}) ---")
        for idx, c in new_ng[:20]:
            print(f"    [{c['source'][:3]}] {c['stock']}: {v14_results[idx]}->{v151_results[idx]} (ans={c['correct']})")
        if len(new_ng) > 20:
            print(f"    ... +{len(new_ng)-20}건 더")

    if both_ng:
        print(f"\n  ~~~ Still wrong ({len(both_ng)}) ~~~")
        for idx, c in both_ng[:15]:
            print(f"    [{c['source'][:3]}] {c['stock']}: V14={v14_results[idx]} V15={v151_results[idx]} (ans={c['correct']})")
        if len(both_ng) > 15:
            print(f"    ... +{len(both_ng)-15}건 더")

    # === 오분류 패턴 분석 ===
    print(f"\n  === 오분류 패턴 (V15 기준) ===")
    from collections import Counter
    error_patterns = Counter()
    for i in range(total):
        if v151_results[i] != cases[i]["correct"]:
            key = f"{cases[i]['correct']}→{v151_results[i]}"
            error_patterns[key] += 1
    for pattern, cnt in error_patterns.most_common():
        print(f"    {pattern}: {cnt}건")

    # Save
    out = {
        "ts": datetime.now().isoformat(),
        "total": total,
        "v14_pct": round(v14_ok/total*100, 1),
        "v151_pct": round(v15_ok/total*100, 1),
        "delta_pct": round(delta/total*100, 1),
        "new_correct": len(new_ok),
        "regression": len(new_ng),
        "still_wrong": len(both_ng),
        "by_source": {},
        "details": []
    }

    for src_name, src_key in [("anyuhwa", "anyuhwa"), ("wisdomtooth", "wisdomtooth")]:
        idxs = [i for i in range(total) if cases[i]["source"] == src_key]
        n = len(idxs)
        s14 = sum(1 for i in idxs if v14_results[i] == cases[i]["correct"])
        s15 = sum(1 for i in idxs if v151_results[i] == cases[i]["correct"])
        out["by_source"][src_key] = {"n": n, "v14_pct": round(s14/n*100,1), "v151_pct": round(s15/n*100,1)}

    for i in range(total):
        out["details"].append({
            "stock": cases[i]["stock"],
            "correct": cases[i]["correct"],
            "v14": v14_results[i],
            "v151": v151_results[i],
            "source": cases[i]["source"],
            "v151_correct": v151_results[i] == cases[i]["correct"]
        })

    out_path = Path(__file__).parent.parent / "data" / "eval_v151_results.json"
    json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n  Saved: {out_path}")


if __name__ == "__main__":
    main()
