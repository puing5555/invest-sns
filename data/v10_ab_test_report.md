# V10.8 vs V10.9 A/B 테스트 결과

테스트 일시: 2026-03-04
모델: claude-sonnet-4-20250514
테스트 자막: 5개

## 요약

| 항목 | V10.8 | V10.9 |
|------|-------|-------|
| 총 시그널 | 3 | 2 |
| 비종목 포함 (암호화폐/원자재 등) | 0 | 0 |
| key_quote 200자 초과 | 0 | 0 |

## V10.9 주요 변경사항 적용 여부

### 1. 비종목 필터링 (암호화폐, 금, 원자재 등)
- V10.8: 0개 비종목 시그널 생성
- V10.9: 0개 비종목 시그널 생성
- **⚠️ 차이 없음**

### 2. key_quote 200자 제한
- V10.8: 0개 초과
- V10.9: 0개 초과
- **⚠️ 차이 없음**

### 3. confidence 4 이하 제외 (V10.9 신규)
- 4wCO1fdl9iU.ko.vtt: V10.8=0개 low-conf, V10.9=0개 low-conf
- wsaj_0pS0CTDgVmU_[기업해부학] Amazon 아마존 3Q 2023 어닝콜! 클라우드 매출 하회했는데 주가는 왜 올랐을까？.ko.vtt: V10.8=0개 low-conf, V10.9=0개 low-conf
- wsaj_AQ2z2ZCBFa4_[기업해부학] Nvidia, AI⧸메타버스⧸자율주행의 완벽 콜라보？ 혹은 내리막 직전의 롤러코스터？.ko.vtt: V10.8=0개 low-conf, V10.9=0개 low-conf
- wsaj_B17xc8zl3Z4_[기업해부학] Meta 메타 3Q 2023 어닝콜 분석! 메타버스 버리고 AI버스 탑승하자!.ko.vtt: V10.8=0개 low-conf, V10.9=0개 low-conf
- wsaj_EbfuT0zGGjU_[기업해부학] IPO 공모주 투자, 놓치기 쉬운 3가지 핵심 포인트.ko.vtt: V10.8=0개 low-conf, V10.9=0개 low-conf

### 4. 1영상 1종목 1시그널


---

## 자막 1: 4wCO1fdl9iU.ko.vtt

### V10.8 결과 (0개 시그널)

```json
[]
```

### V10.9 결과 (0개 시그널)

```json
[]
```

### 차이점 분석
- 시그널 수: V10.8=0 vs V10.9=0
- 비종목: V10.8=0 vs V10.9=0
- key_quote 200자 초과: V10.8=0 vs V10.9=0

### V10.8 API 원문 응답

```
```json
{
  "signals": []
}
```
```

### V10.9 API 원문 응답

```
```json
{
  "signals": []
}
```
```

---

## 자막 2: wsaj_0pS0CTDgVmU_[기업해부학] Amazon 아마존 3Q 2023 어닝콜! 클라우드 매출 하회했는데 주가는 왜 올랐을까？.ko.vtt

### V10.8 결과 (1개 시그널)

```json
[
  {
    "stock": "아마존",
    "ticker": "AMZN",
    "signal_type": "긍정",
    "key_quote": "아마존 3분기 실적이 아주 잘 나왔어요. 영업 이익이 전년 동기 대비 네 배가 넘는 엄청난 수치입니다",
    "reasoning": "3분기 영업이익 11.2B으로 전년동기 대비 4배 증가, EPS도 0.94달러로 컨센서스 0.58달러 대비 크게 상회하며 비용 절감 효과가 나타남",
    "timestamp": "01:12",
    "confidence": 7
  }
]
```

### V10.9 결과 (0개 시그널)

```json
[]
```

### 차이점 분석
- 시그널 수: V10.8=1 vs V10.9=0
- 비종목: V10.8=0 vs V10.9=0
- key_quote 200자 초과: V10.8=0 vs V10.9=0

### V10.8 API 원문 응답

```
```json
{
  "signals": [
    {
      "stock": "아마존",
      "ticker": "AMZN",
      "signal_type": "긍정",
      "key_quote": "아마존 3분기 실적이 아주 잘 나왔어요. 영업 이익이 전년 동기 대비 네 배가 넘는 엄청난 수치입니다",
      "reasoning": "3분기 영업이익 11.2B으로 전년동기 대비 4배 증가, EPS도 0.94달러로 컨센서스 0.58달러 대비 크게 상회하며 비용 절감 효과가 나타남",
      "timestamp": "01:12",
      "confidence": 7
    }
  ]
}
```
```

### V10.9 API 원문 응답

```
이 영상은 아마존의 3분기 실적에 대한 기업 분석 영상으로, 개별 종목에 대한 구체적인 투자 추천이나 의견보다는 아마존의 실적 분석과 해석에 초점을 맞추고 있습니다.

분석가는 아마존의 실적이 "아주 잘 나왔다"고 평가하며 주가 움직임의 배경을 설명하고 있지만, 이는 실적 분석의 차원에서 언급된 것이며 명확한 투자 시그널로 보기는 어렵습니다.

영상 내용이 실적 해석과 교육적 설명 위주이고, confidence 4 이하에 해당하는 단순 언급 수준으로 판단되어 시그널을 추출하지 않겠습니다.

```json
{
  "signals": []
}
```
```

---

## 자막 3: wsaj_AQ2z2ZCBFa4_[기업해부학] Nvidia, AI⧸메타버스⧸자율주행의 완벽 콜라보？ 혹은 내리막 직전의 롤러코스터？.ko.vtt

### V10.8 결과 (1개 시그널)

```json
[
  {
    "stock": "엔비디아",
    "ticker": "NVDA",
    "signal_type": "긍정",
    "key_quote": "ai용 GPU 사업도 한다고 알게 됐어요 거의 둘이 현재 엔비디아의 가장 큰 수익원이기는 한데",
    "reasoning": "AI용 GPU 사업이 현재 엔비디아의 주요 수익원 중 하나로 확인되며, 게이밍과 함께 핵심 사업영역임을 언급",
    "timestamp": "37:30",
    "confidence": 6
  }
]
```

### V10.9 결과 (1개 시그널)

```json
[
  {
    "stock": "엔비디아",
    "ticker": "NVDA",
    "signal_type": "긍정",
    "key_quote": "엔비디아는 AI, 자율주행, 메타버스 핫한 테마를 전부 어루는 기업으로 매출까지 가파르게 성장해왔고 안정적으로 흑자까지 내는 성장형 테마주의 집합체입니다",
    "reasoning": "AI, 자율주행, 메타버스 등 여러 핫한 테마를 보유하고 매출 성장과 안정적 수익성을 동시에 달성한 기업으로 긍정적 평가",
    "timestamp": "20:15",
    "confidence": 7
  }
]
```

### 차이점 분석
- 시그널 수: V10.8=1 vs V10.9=1
- 비종목: V10.8=0 vs V10.9=0
- key_quote 200자 초과: V10.8=0 vs V10.9=0

### V10.8 API 원문 응답

```
```json
{
  "signals": [
    {
      "stock": "엔비디아",
      "ticker": "NVDA",
      "signal_type": "긍정",
      "key_quote": "ai용 GPU 사업도 한다고 알게 됐어요 거의 둘이 현재 엔비디아의 가장 큰 수익원이기는 한데",
      "reasoning": "AI용 GPU 사업이 현재 엔비디아의 주요 수익원 중 하나로 확인되며, 게이밍과 함께 핵심 사업영역임을 언급",
      "timestamp": "37:30",
      "confidence": 6
    }
  ]
}
```
```

### V10.9 API 원문 응답

```
```json
{
  "signals": [
    {
      "stock": "엔비디아",
      "ticker": "NVDA",
      "signal_type": "긍정",
      "key_quote": "엔비디아는 AI, 자율주행, 메타버스 핫한 테마를 전부 어루는 기업으로 매출까지 가파르게 성장해왔고 안정적으로 흑자까지 내는 성장형 테마주의 집합체입니다",
      "reasoning": "AI, 자율주행, 메타버스 등 여러 핫한 테마를 보유하고 매출 성장과 안정적 수익성을 동시에 달성한 기업으로 긍정적 평가",
      "timestamp": "20:15",
      "confidence": 7
    }
  ]
}
```
```

---

## 자막 4: wsaj_B17xc8zl3Z4_[기업해부학] Meta 메타 3Q 2023 어닝콜 분석! 메타버스 버리고 AI버스 탑승하자!.ko.vtt

### V10.8 결과 (1개 시그널)

```json
[
  {
    "stock": "메타 (META)",
    "ticker": "META",
    "signal_type": "경계",
    "key_quote": "애프터마켓에서 주가가 확 떨어졌거든요. 광고 지출이 확실히 좀 약화되는 모습이 보였다고 답변을 했더라고요",
    "reasoning": "3분기 실적은 좋았지만 지정학적 리스크로 4분기 광고 매출 성장에 의구심이 생기고, 메타버스 투자 확대로 비용 증가 우려",
    "timestamp": "07:30",
    "confidence": 6
  }
]
```

### V10.9 결과 (1개 시그널)

```json
[
  {
    "stock": "메타",
    "ticker": "META",
    "signal_type": "중립",
    "key_quote": "메타가 AI 메타버스 쪽에 사활을 걸고 있지만 매출 성장성에 대한 의구심이 있고 메타버스 부문 영업적자가 계속 늘어나고 있어서 투자 결실을 맺을 수 있을지 의구심이 있는 상태입니다",
    "reasoning": "3분기 실적은 좋았으나 지정학적 리스크로 인한 광고매출 성장 우려와 메타버스 부문 지속적 적자 확대에 대한 의구심 표명",
    "timestamp": "34:30",
    "confidence": 6
  }
]
```

### 차이점 분석
- 시그널 수: V10.8=1 vs V10.9=1
- 비종목: V10.8=0 vs V10.9=0
- key_quote 200자 초과: V10.8=0 vs V10.9=0

### V10.8 API 원문 응답

```
```json
{
  "signals": [
    {
      "stock": "메타 (META)",
      "ticker": "META",
      "signal_type": "경계",
      "key_quote": "애프터마켓에서 주가가 확 떨어졌거든요. 광고 지출이 확실히 좀 약화되는 모습이 보였다고 답변을 했더라고요",
      "reasoning": "3분기 실적은 좋았지만 지정학적 리스크로 4분기 광고 매출 성장에 의구심이 생기고, 메타버스 투자 확대로 비용 증가 우려",
      "timestamp": "07:30",
      "confidence": 6
    }
  ]
}
```
```

### V10.9 API 원문 응답

```
```json
{
  "signals": [
    {
      "stock": "메타",
      "ticker": "META",
      "signal_type": "중립",
      "key_quote": "메타가 AI 메타버스 쪽에 사활을 걸고 있지만 매출 성장성에 대한 의구심이 있고 메타버스 부문 영업적자가 계속 늘어나고 있어서 투자 결실을 맺을 수 있을지 의구심이 있는 상태입니다",
      "reasoning": "3분기 실적은 좋았으나 지정학적 리스크로 인한 광고매출 성장 우려와 메타버스 부문 지속적 적자 확대에 대한 의구심 표명",
      "timestamp": "34:30",
      "confidence": 6
    }
  ]
}
```
```

---

## 자막 5: wsaj_EbfuT0zGGjU_[기업해부학] IPO 공모주 투자, 놓치기 쉬운 3가지 핵심 포인트.ko.vtt

### V10.8 결과 (0개 시그널)

```json
[]
```

### V10.9 결과 (0개 시그널)

```json
[]
```

### 차이점 분석
- 시그널 수: V10.8=0 vs V10.9=0
- 비종목: V10.8=0 vs V10.9=0
- key_quote 200자 초과: V10.8=0 vs V10.9=0

### V10.8 API 원문 응답

```
Looking at this video transcript, this is an educational content about IPO investment fundamentals that doesn't contain any specific stock signals or investment recommendations. The video discusses general concepts like:

1. How IPO public offerings work
2. The difference between firm commitment and best efforts underwriting
3. Primary vs. secondary offerings
4. How to check offering documents (DART system in Korea, EDGAR in US)

The content is purely educational and informational, explaining IPO mechanics to help investors understand what to look for when evaluating public offerings. There are no mentions of specific companies, stock picks, buy/sell recommendations, or investment signals.

```json
{
  "signals": []
}
```
```

### V10.9 API 원문 응답

```
```json
{
  "signals": []
}
```

이 영상은 IPO 공모주 투자 시 확인해야 할 포인트들을 교육하는 매크로/교육 영상입니다. 개별 종목에 대한 구체적인 투자 의견이나 추천이 없으며, 버켄스탁과 같은 기업들이 단순히 설명 예시로만 언급되었습니다. 따라서 투자 시그널을 추출할 대상이 없습니다.
```
