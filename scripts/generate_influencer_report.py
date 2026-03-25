"""
인플루언서 AI 분석 리포트 생성 v3 (룰 기반, API 호출 없음)
- influencer_scorecard.json (v3: 1Y/Current return, 매수+긍정+매도 적중률)
- 인플루언서별 텍스트 리포트 생성
- data/influencer_reports.json + public/influencer_reports.json 출력
"""
import json, sys
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
SCORECARD_FILE = BASE_DIR / "data" / "influencer_scorecard.json"
OUTPUT_FILE = BASE_DIR / "data" / "influencer_reports.json"
PUBLIC_FILE = BASE_DIR / "public" / "influencer_reports.json"

MIN_ELIGIBLE = 3  # 리포트 생성 최소 기준
MIN_HIT = 10      # 적중률 평가 최소 기준

BUY_SIGNALS = {'매수', '긍정', 'STRONG_BUY', 'BUY', 'POSITIVE'}
SELL_SIGNALS = {'매도', 'SELL', 'STRONG_SELL'}


def fmt_pct(v):
    if v is None:
        return '-'
    return f"+{v:.1f}%" if v >= 0 else f"{v:.1f}%"


def fmt_money(v):
    if abs(v) >= 100_000_000:
        return f"{v / 100_000_000:.1f}억원"
    return f"{v / 10_000:,.0f}만원"


def generate_one_liner(card):
    name = card['name']
    eligible = card.get('hit_eligible', 0)
    hit = card.get('hit_rate')
    style = card.get('style_tag', '')
    homerun = card.get('homerun_rate', 0)

    if eligible < MIN_HIT or hit is None:
        return f"{name}은(는) 아직 적중률 평가에 필요한 시그널이 부족합니다 (매수/매도 {eligible}건)."

    if '올라운더' in style:
        return f"{name}은(는) 적중률 {hit}%에 홈런 비율 {homerun}%로, 안정성과 대형 수익을 겸비한 올라운더입니다."
    elif '스나이퍼' in style:
        return f"{name}은(는) 적중률 {hit}%의 꾸준한 정확도를 보여주는 안정형 분석가입니다."
    elif '홈런히터' in style:
        return f"{name}은(는) 적중률은 낮지만 홈런 비율 {homerun}%로 대형 수익을 노리는 공격형입니다."
    else:
        return f"{name}은(는) 적중률 {hit}%, 매수/매도 {eligible}건의 분석 이력을 보유하고 있습니다."


def generate_strengths_weaknesses(card):
    strengths = []
    weaknesses = []

    hit = card.get('hit_rate')
    homerun = card.get('homerun_rate', 0)
    market = card.get('market', {})
    best = card.get('best_call')
    worst = card.get('worst_call')
    expected = card.get('expected_return')

    if hit and hit >= 60:
        strengths.append(f"높은 적중률 ({hit}%)")
    if homerun >= 20:
        strengths.append(f"높은 홈런 비율 ({homerun}%)")
    if expected and expected > 0:
        strengths.append(f"양의 기대수익률 ({fmt_pct(expected)})")

    for mkt, data in market.items():
        if data.get('hit_rate') and data['hit_rate'] >= 65 and data.get('count', 0) >= 5:
            strengths.append(f"{mkt} 시장 적중률 우수 ({data['hit_rate']}%, {data['count']}건)")

    if best:
        ret = best.get('return_1y')
        strengths.append(f"최고 콜: {best['stock']} 1Y {fmt_pct(ret)}")

    if hit and hit < 50:
        weaknesses.append(f"낮은 적중률 ({hit}%)")
    if expected and expected < 0:
        weaknesses.append(f"음의 기대수익률 ({fmt_pct(expected)})")

    for mkt, data in market.items():
        if data.get('hit_rate') and data['hit_rate'] < 45 and data.get('count', 0) >= 3:
            weaknesses.append(f"{mkt} 시장 적중률 저조 ({data['hit_rate']}%, {data['count']}건)")

    if worst:
        ret = worst.get('return_1y')
        weaknesses.append(f"최악 콜: {worst['stock']} 1Y {fmt_pct(ret)}")

    parts = []
    if strengths:
        parts.append("강점: " + " / ".join(strengths))
    if weaknesses:
        parts.append("약점: " + " / ".join(weaknesses))
    if not parts:
        parts.append("특별한 강점/약점이 뚜렷하지 않습니다.")

    return "\n".join(parts)


def generate_top_worst_calls(card):
    top3 = card.get('top3_calls', [])
    worst3 = card.get('worst3_calls', [])

    lines = []
    if top3:
        lines.append("TOP 3 콜:")
        for i, c in enumerate(top3, 1):
            r1y = fmt_pct(c.get('return_1y'))
            r_cur = fmt_pct(c.get('return_current'))
            lines.append(f"  {i}. {c['stock']} 1Y {r1y} / 현재 {r_cur} ({c['date']})")

    if worst3:
        lines.append("WORST 3 콜:")
        for i, c in enumerate(worst3, 1):
            r1y = fmt_pct(c.get('return_1y'))
            r_cur = fmt_pct(c.get('return_current'))
            lines.append(f"  {i}. {c['stock']} 1Y {r1y} / 현재 {r_cur} ({c['date']})")

    return "\n".join(lines) if lines else "데이터 부족"


def generate_investment_pattern(card):
    market = card.get('market', {})
    signal_types = card.get('signal_types', {})
    total = card.get('total_signals', 0)

    parts = []

    if market:
        sorted_mkts = sorted(market.items(), key=lambda x: x[1].get('count', 0), reverse=True)
        total_mkt = max(sum(v['count'] for v in market.values()), 1)
        mkt_strs = [f"{m} {d['count']}건({round(d['count']/total_mkt*100)}%)" for m, d in sorted_mkts if d.get('count', 0) > 0]
        if mkt_strs:
            parts.append("시장 분포: " + ", ".join(mkt_strs))

    if signal_types:
        bullish = sum(signal_types.get(s, 0) for s in ['매수', '긍정'])
        bearish = sum(signal_types.get(s, 0) for s in ['매도', '부정'])
        neutral = signal_types.get('중립', 0)
        if total > 0:
            parts.append(f"시그널 성향: 긍정적 {bullish}건({round(bullish/total*100)}%) / 부정적 {bearish}건({round(bearish/total*100)}%) / 중립 {neutral}건({round(neutral/total*100)}%)")

    scored_list = card.get('scored_list', [])
    if scored_list:
        stock_freq = {}
        for s in scored_list:
            stock_freq[s['stock']] = stock_freq.get(s['stock'], 0) + 1
        top_stocks = sorted(stock_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        if top_stocks:
            parts.append("주력 종목: " + ", ".join(f"{s}({c}건)" for s, c in top_stocks))

    return "\n".join(parts) if parts else "패턴 분석을 위한 데이터가 부족합니다."


def generate_trend_analysis(card):
    recent = card.get('recent_30d', {})
    hit = card.get('hit_rate')
    recent_hit = recent.get('hit_rate')
    delta = recent.get('delta')
    recent_count = recent.get('count', 0)

    if recent_count < 2:
        return f"최근 30일 평가 시그널이 {recent_count}건으로, 트렌드 분석이 어렵습니다."

    if delta is not None:
        if delta > 5:
            return f"트렌드: 상승세 (최근 30일 {recent_count}건)\n최근 30일 적중률({recent_hit}%)이 전체({hit}%)보다 {delta}%p 높아, 최근 분석 정확도가 개선되고 있습니다."
        elif delta < -5:
            return f"트렌드: 하락세 (최근 30일 {recent_count}건)\n최근 30일 적중률({recent_hit}%)이 전체({hit}%)보다 {abs(delta)}%p 낮아, 최근 분석 정확도가 떨어지고 있습니다."
        else:
            return f"트렌드: 유지 (최근 30일 {recent_count}건)\n최근 30일 적중률({recent_hit}%)이 전체({hit}%)와 유사하여, 안정적인 분석력을 유지하고 있습니다."

    return f"최근 30일: {recent_count}건, 적중률 {recent_hit if recent_hit else '-'}%"


def generate_follow_simulation(card):
    """팔로우 시뮬레이션: 매 콜 100만원 투입 (매수+긍정+매도만, 1Y / 현재 각각)"""
    scored_list = card.get('scored_list', [])
    eligible = [s for s in scored_list if s.get('signal') in (BUY_SIGNALS | SELL_SIGNALS)]
    if not eligible:
        return {'text': '시뮬레이션 데이터 부족', 'total_invested_1y': 0, 'profit_1y': 0, 'return_1y': 0, 'total_invested_cur': 0, 'profit_cur': 0, 'return_cur': 0}

    invest = 1_000_000
    cnt_1y = cnt_cur = 0
    profit_1y = profit_cur = 0

    for s in eligible:
        is_sell = s.get('signal') in SELL_SIGNALS
        r1y = s.get('return_1y')
        rcur = s.get('return_current')
        if r1y is not None:
            r = -r1y if is_sell else r1y
            profit_1y += invest * r / 100
            cnt_1y += 1
        if rcur is not None:
            r = -rcur if is_sell else rcur
            profit_cur += invest * r / 100
            cnt_cur += 1

    ret_1y = round(profit_1y / (cnt_1y * invest) * 100, 1) if cnt_1y > 0 else 0
    ret_cur = round(profit_cur / (cnt_cur * invest) * 100, 1) if cnt_cur > 0 else 0

    text = (
        f"매 시그널마다 100만원씩 투입했다면:\n"
        f"1Y 기준: {cnt_1y}건, 누적 {fmt_money(profit_1y)} ({fmt_pct(ret_1y)})\n"
        f"현재 기준: {cnt_cur}건, 누적 {fmt_money(profit_cur)} ({fmt_pct(ret_cur)})"
    )

    return {
        'text': text,
        'total_invested_1y': cnt_1y * invest,
        'profit_1y': round(profit_1y),
        'return_1y': ret_1y,
        'total_invested_cur': cnt_cur * invest,
        'profit_cur': round(profit_cur),
        'return_cur': ret_cur,
    }


def generate_ai_opinion(card):
    name = card['name']
    style = card.get('style_tag', '')
    hit = card.get('hit_rate')
    homerun = card.get('homerun_rate', 0)
    expected = card.get('expected_return')
    eligible = card.get('hit_eligible', 0)
    wins = card.get('wins', 0)
    losses = card.get('losses', 0)

    if eligible < MIN_HIT or hit is None:
        return f"{name}의 매수/매도 시그널이 아직 충분하지 않습니다. 더 많은 시그널이 쌓인 후 종합 평가가 가능합니다."

    parts = []

    if hit >= 65:
        parts.append(f"{name}은(는) {eligible}건의 매수/매도 시그널 중 {wins}건을 적중시키며 {hit}%의 높은 적중률을 기록하고 있습니다.")
    elif hit >= 50:
        parts.append(f"{name}은(는) {eligible}건 기준 {hit}%의 적중률로 평균 수준의 분석력을 보이고 있습니다.")
    else:
        parts.append(f"{name}은(는) {eligible}건 기준 {hit}%의 적중률로, 방향 예측에 어려움을 보이고 있습니다.")

    if '올라운더' in style:
        parts.append("적중률과 대형 수익 모두 양호하여 밸런스형 분석가로 평가됩니다.")
    elif '스나이퍼' in style:
        parts.append("대형 수익보다는 꾸준한 적중에 강점이 있어, 안정적 팔로우에 적합합니다.")
    elif '홈런히터' in style:
        parts.append("적중률은 낮지만 맞을 때 큰 수익을 내는 특성이 있어, 리스크 감수형 투자자에게 맞습니다.")

    if expected is not None:
        if expected > 50:
            parts.append(f"1년 기대수익률 {fmt_pct(expected)}으로, 시그널 팔로우 시 양의 기대값을 제공합니다.")
        elif expected > 0:
            parts.append(f"1년 기대수익률 {fmt_pct(expected)}으로, 소폭 양의 기대값이 있습니다.")
        else:
            parts.append(f"1년 기대수익률 {fmt_pct(expected)}으로, 단순 팔로우 시 손실이 예상됩니다.")

    return " ".join(parts)


def generate_report(slug, card):
    sim = generate_follow_simulation(card)
    return {
        'name': card['name'],
        'style_tag': card.get('style_tag', '📊시그널 수집 중'),
        'sections': {
            'one_liner': generate_one_liner(card),
            'strengths_weaknesses': generate_strengths_weaknesses(card),
            'top_worst_calls': generate_top_worst_calls(card),
            'investment_pattern': generate_investment_pattern(card),
            'trend_analysis': generate_trend_analysis(card),
            'follow_simulation': sim,
            'ai_opinion': generate_ai_opinion(card),
        }
    }


def main():
    print("=== 인플루언서 AI 분석 리포트 생성 v3 ===", flush=True)

    scorecard = json.loads(SCORECARD_FILE.read_text(encoding='utf-8'))
    speakers = scorecard.get('speakers', {})

    reports = {}
    for slug, card in speakers.items():
        if card.get('hit_eligible', 0) >= MIN_ELIGIBLE:
            reports[slug] = generate_report(slug, card)

    result = {
        'generated_at': datetime.now().isoformat(),
        'total_reports': len(reports),
        'reports': reports
    }

    out = json.dumps(result, ensure_ascii=False, indent=2)
    OUTPUT_FILE.write_text(out, encoding='utf-8')
    PUBLIC_FILE.write_text(out, encoding='utf-8')

    print(f"총 {len(reports)}건 리포트 생성 완료", flush=True)
    print(f"출력: {OUTPUT_FILE}", flush=True)
    print(f"공개: {PUBLIC_FILE}", flush=True)

    if reports:
        sample_slug = list(reports.keys())[0]
        sample = reports[sample_slug]
        print(f"\n--- 샘플: {sample['name']} ---", flush=True)
        print(f"스타일: {sample['style_tag']}", flush=True)
        print(f"한줄: {sample['sections']['one_liner']}", flush=True)


if __name__ == '__main__':
    main()
