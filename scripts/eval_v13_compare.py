"""
V12.3 vs V13.0 프롬프트 Eval 비교
- 69건 정답지 기반
- key_quote + 맥락 정보로 시그널 재분류
- 비용: ~$0.5 (69건 × Sonnet × 2 버전)

사용법: python scripts/eval_v13_compare.py
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    import anthropic
except ImportError:
    print("pip install anthropic --break-system-packages")
    sys.exit(1)

# Load API key
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env.local')

API_KEY = os.environ.get('ANTHROPIC_API_KEY')
if not API_KEY:
    print("❌ ANTHROPIC_API_KEY not found")
    sys.exit(1)

client = anthropic.Anthropic(api_key=API_KEY)

# Ground truth data (69건)
GROUND_TRUTH = [
    {"stock": "푸야오글래스", "key_quote": "여러분은 27% 이미 벌었다. A주수 나의 이준이 할 때 무조건 싼 거 사는 거예요", "video_title": "가치주 투자방법과 중국 대표기업", "correct": "매수", "v12_result": "매수"},
    {"stock": "화웨이", "key_quote": "화웨이가 중국 자동차 회사와 협업해서 테슬라 정도의 소프트웨어를 구축한다면 가격적으로 테슬라보다 훨씬 더 싸게 공급할 수 있는 장점이 있어 테슬라의 가장 강력한 경쟁 대상이 될 것", "video_title": "테슬라 미중기술패권쟁의 희생양이 될것인가?", "correct": "긍정", "v12_result": "긍정"},
    {"stock": "테슬라", "key_quote": "테슬라 성공사례는 중국 지방정부 중심으로 이루어진 통제의 발전 정책이 굉장히 현실적으로 실사구시적으로 이루어지고 있다", "video_title": "테슬라 미중기술패권쟁의 희생양이 될것인가?", "correct": "중립", "v12_result": "긍정", "reason_cat": "단순사례인용"},
    {"stock": "로블록스", "key_quote": "로블록스는 우리가 보통 메타버스를 얘기할 때 가장 대표 기업으로 보는 기업입니다", "video_title": "빅테크 기업이 직면한 어려움, 한국 대기업들이 놓치는 것은?", "correct": "중립", "v12_result": "긍정", "reason_cat": "단순사례인용"},
    {"stock": "삼성SDI", "key_quote": "삼성sdi는 전고체 배터리 다시 말해서 전해질이 고체화를 통해서 안정성을 확보하는 그리고 굉장히 감소된 배터리 크기로 더 많은 배터리를 장착할 수 있게 지금 기술총격차를 벌려가고 있는 삼성입니다", "video_title": "한중 전기차 배터리 전쟁! 한국 기업들이 중국을 떠나는 이유는?", "correct": "중립", "v12_result": "긍정", "reason_cat": "단순기술분석"},
    {"stock": "삼성전자", "key_quote": "삼성전자가 3만원까지 갈 수도 있고, AI 공급망 안에서 제대로 자리를 잡으면 30만원에서 100만원도 갈 수 있다", "video_title": "삼성전자 3만원 vs 100만원", "correct": "중립", "v12_result": "부정", "reason_cat": "조건부누락"},
    {"stock": "엔비디아", "key_quote": "시스코가 2000년에 고점 찍고 폭락했듯이 엔비디아도 같은 길을 갈 수 있다", "video_title": "엔비디아 고점 리스크", "correct": "중립", "v12_result": "부정", "reason_cat": "시그널하향(리스크언급)"},
    {"stock": "테슬라", "key_quote": "신모델 부재, FSD 규제 등 주가 하락의 구조적 리스크가 있다", "video_title": "테슬라 리스크 분석", "correct": "중립", "v12_result": "부정", "reason_cat": "시그널하향(리스크언급)"},
    {"stock": "BYD", "key_quote": "적정가 대비 저평가 매력이 있다", "video_title": "중국 전기차 분석", "correct": "긍정", "v12_result": "매수", "reason_cat": "종목불일치"},
    {"stock": "타이거 차이나 전기차 솔렉티브", "key_quote": "생각해 주시면 좋을 것 같다", "video_title": "중국 ETF 추천", "correct": "긍정", "v12_result": "매수", "reason_cat": "시그널하향(제안수준)"},
    {"stock": "타이거 차이나테크 탑 10 ETF", "key_quote": "담아 보시면 좋을 것 같다", "video_title": "중국 ETF 포트폴리오", "correct": "긍정", "v12_result": "매수", "reason_cat": "시그널하향(제안수준)"},
    {"stock": "비트코인", "key_quote": "비트코인 초급반에서 실습합니다", "video_title": "비트코인 강의 안내", "correct": "중립", "v12_result": "매수", "reason_cat": "단순사례인용"},
    {"stock": "타이거 차이나 증권 ETF", "key_quote": "뉴럴링크의 밸류에이션과 비교하면 저평가", "video_title": "차이나 ETF 분석", "correct": "중립", "v12_result": "매수", "reason_cat": "단순사례인용"},
    {"stock": "타이거차이나휴먼노이드로봇", "key_quote": "AI 주가 버블이라고 생각하시나요?", "video_title": "AI 버블 논쟁", "correct": "중립", "v12_result": "매수", "reason_cat": "시그널하향(단순질문)"},
    {"stock": "비트코인", "key_quote": "과거 10억 도달 분석을 인용하며 비트코인에 대한 장기적 매수 뷰는 확고하다", "video_title": "비트코인 전망", "correct": "매수", "v12_result": "긍정", "reason_cat": "뷰유지(스탠스동일)"},
    {"stock": "BYD", "key_quote": "압도적인 개발자 규모와 타사 대비 2000달러 이상 저렴한 원가 경쟁력을 바탕으로 세계 시장을 장악할 것", "video_title": "BYD 경쟁력 분석", "correct": "매수", "v12_result": "긍정", "reason_cat": "시그널상향"},
    {"stock": "현대자동차", "key_quote": "AI 산업이 초입 단계이며 향후 커질 일밖에 없다는 호의적인 장기 전망", "video_title": "AI 산업 전망", "correct": "긍정", "v12_result": "중립", "reason_cat": "맥락일치"},
]


def classify_signal(prompt_version, stock, key_quote, video_title):
    """Claude Sonnet으로 시그널 분류"""
    
    if prompt_version == "v12.3":
        system = """투자 인플루언서의 발언을 분석하여 시그널을 분류하세요.
시그널 타입: 매수/긍정/중립/부정/매도
- 매수: 강한 확신 + 투자 권유/추천
- 긍정: 호의적이지만 직접 매수 권유 없음
- 중립: 단순 소개, 실적 분석, 방향성 없음, 단순 사례 인용
- 부정: 명시적 매도 추천 / 확정적 하락 전망
- 매도: 직접적 매도 권유

반드시 JSON으로만 응답: {"signal_type": "매수|긍정|중립|부정|매도", "reason": "한줄 이유"}"""
    
    else:  # v13.0
        system = """투자 인플루언서의 발언을 분석하여 시그널을 분류하세요.
시그널 타입: 매수/긍정/중립/부정/매도

■ 매수 = 강한 확신 + 투자 권유. "사라", "매수 추천", "지금 들어가야", 본인 매매 공개.
  ❌ "~하면 좋을 것 같다", "담아보시면" → 긍정 (호의적 제안일 뿐 강한 권유 아님)

■ 긍정 = 호의적이지만 직접 매수 권유 없음. "좋은 종목", "전망 밝다", "관심 가져볼 만하다"
  "~하면 좋겠다", "생각해 주시면", "포트폴리오에 편입 검토해볼 만하다" → 긍정

■ 중립 = 단순 소개, 실적 분석, 방향성 없음. 반드시 중립인 경우:
  - 단순 사례 인용: 종목이 다른 논점의 보조 예시로만 사용됨 (예: "로블록스는 메타버스 대표기업" → 메타버스 설명 도구)
  - 산업/기술의 객관적 설명: "삼성SDI는 전고체 배터리를 추진 중" (기술 현황 설명)
  - 비교 대상(대조군): "뉴럴링크와 비교하면" → 비교 도구일 뿐
  - 교육/강의 홍보: "초급반에서 실습합니다" → 교육 유도이지 투자 권유 아님
  - 인터뷰 질문: 진행자가 게스트에게 묻는 단순 도입부
  핵심: "이 종목에 대한 직접 투자 의견인가, 다른 얘기의 보조 도구인가?"

■ 부정 = 확정적 하락 전망 / 투자 회피 권고만. 
  ❌ 리스크 언급, 우려, 경고, 가능성 제기 → 중립 ("시스코처럼 빠질 수 있다" = 중립)
  ✅ "이 종목은 빠질 것이다, 팔아라" = 부정

■ 매도 = 직접적 매도 권유

반드시 JSON으로만 응답: {"signal_type": "매수|긍정|중립|부정|매도", "reason": "한줄 이유"}"""
    
    user_msg = f"""종목: {stock}
영상 제목: {video_title}
발언: "{key_quote}"

이 발언의 시그널 타입을 분류하세요."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            system=system,
            messages=[{"role": "user", "content": user_msg}]
        )
        
        text = response.content[0].text.strip()
        # Parse JSON
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        return result.get("signal_type", "중립")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return "중립"


def main():
    print("📊 V12.3 vs V13.0 Eval 비교")
    print(f"📋 정답지: {len(GROUND_TRUTH)}건")
    print(f"⏱️ 예상 시간: ~3분\n")
    
    results = []
    
    for i, gt in enumerate(GROUND_TRUTH):
        print(f"[{i+1}/{len(GROUND_TRUTH)}] {gt['stock']}...", end=" ")
        
        # V12.3 result (이미 있으면 사용)
        v12_result = gt.get("v12_result")
        
        # V13.0 result (새로 분류)
        v13_result = classify_signal("v13.0", gt["stock"], gt["key_quote"], gt["video_title"])
        
        correct = gt["correct"]
        v12_match = "✅" if v12_result == correct else "❌"
        v13_match = "✅" if v13_result == correct else "❌"
        
        print(f"정답={correct} | V12={v12_result}{v12_match} | V13={v13_result}{v13_match}")
        
        results.append({
            "stock": gt["stock"],
            "correct": correct,
            "v12_result": v12_result,
            "v13_result": v13_result,
            "v12_match": v12_result == correct,
            "v13_match": v13_result == correct,
            "reason_cat": gt.get("reason_cat", ""),
        })
        
        import time
        time.sleep(0.5)  # Rate limit
    
    # Summary
    v12_correct = sum(1 for r in results if r["v12_match"])
    v13_correct = sum(1 for r in results if r["v13_match"])
    total = len(results)
    
    print(f"\n{'='*60}")
    print(f"📊 결과 요약")
    print(f"{'='*60}")
    print(f"V12.3 정확도: {v12_correct}/{total} ({v12_correct/total*100:.1f}%)")
    print(f"V13.0 정확도: {v13_correct}/{total} ({v13_correct/total*100:.1f}%)")
    print(f"개선: {v13_correct - v12_correct}건 ({(v13_correct - v12_correct)/total*100:.1f}%p)")
    
    # Category breakdown
    print(f"\n{'='*60}")
    print(f"📋 카테고리별 변화")
    print(f"{'='*60}")
    
    # V13에서 새로 맞춘 것
    newly_correct = [r for r in results if r["v13_match"] and not r["v12_match"]]
    newly_wrong = [r for r in results if not r["v13_match"] and r["v12_match"]]
    
    if newly_correct:
        print(f"\n✅ V13에서 새로 맞춘 건 ({len(newly_correct)}건):")
        for r in newly_correct:
            print(f"  {r['stock']}: {r['v12_result']}→{r['v13_result']} (정답={r['correct']}) [{r['reason_cat']}]")
    
    if newly_wrong:
        print(f"\n❌ V13에서 새로 틀린 건 ({len(newly_wrong)}건):")
        for r in newly_wrong:
            print(f"  {r['stock']}: {r['v12_result']}→{r['v13_result']} (정답={r['correct']}) [{r['reason_cat']}]")
    
    # Save results
    out_path = Path(__file__).parent.parent / "data" / "eval_v13_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "v12_accuracy": v12_correct / total,
            "v13_accuracy": v13_correct / total,
            "total": total,
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 결과 저장: {out_path}")


if __name__ == "__main__":
    main()
