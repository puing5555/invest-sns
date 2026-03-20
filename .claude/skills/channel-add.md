# 채널 추가 7단계 파이프라인

## 전체 흐름

```
[1. 채널 등록]
    ↓
[2. 메타데이터 수집] ← yt-dlp
    ↓
[3. QA Gate 1] ⛔ 실패 시 중단
    ↓
[4. 자막 추출 + 시그널 분석] ← yt-dlp + V14.0
    ↓
[5. QA Gate 2] ⛔ 실패 시 중단
    ↓
[6. DB 저장 + 수익률 계산]
    ↓
[7. QA Gate 3] ⛔ 실패 시 배포 차단
    ↓
[배포]
```

## 실행 명령
```bash
# 전체 자동 실행
python scripts/auto_pipeline.py --channel https://www.youtube.com/@채널핸들 --execute

# QA 없이 실행 (긴급 시만)
python scripts/auto_pipeline.py --channel URL --execute --skip-qa

# 미리보기
python scripts/auto_pipeline.py --channel URL --dry-run
```

## 1단계: 채널 등록 규칙
- channel_name: YouTube 실제 채널명 (핸들 @xxx 사용 금지)
- channel_handle: @xxx 형식
- slug: 소문자+하이픈 (URL용)
- 영문만인 경우 경고 → 한글명 수동 확인

## 2단계: 메타데이터 수집
수집 필드: video_id, title, published_at, duration_seconds, view_count

필터 제외:
- 60초 미만 (Shorts), 7200초 초과 (라이브)
- 조회수 1000 미만
- 키워드: 일상/먹방/여행/브이로그/구독/이벤트/광고/멤버십

필터 통과 키워드:
- 종목명, 매수/매도/전망/분석/추천
- 코스피/나스닥/비트코인

## 3단계: QA Gate 1 (메타데이터)
| 체크 | 조건 | 실패 시 |
|------|------|---------|
| 제목 검증 | YouTube ID 패턴 | ⛔ 중단 |
| 날짜 검증 | 50%+ 같은 날짜 | ⛔ 중단 |
| 날짜 범위 | 미래 날짜 존재 | ⛔ 중단 |
| 채널명 | 영문 핸들만 | ⚠️ 경고 |
| 중복 | DB에 이미 존재 | ⚠️ 스킵 |

## 4단계: 자막 추출 + 시그널 분석
- yt-dlp로 ko 자막 우선, 없으면 en
- **V14.0 프롬프트**로 Sonnet 분석 (→ `prompt.md` 참조)
- 시그널 타입: **매수/긍정/중립/부정/매도** (5단계)
- 레이트 리밋: 20개 후 5분 휴식

## 5단계: QA Gate 2 (시그널)
- 타임스탬프 유효성
- 1영상 1종목 1시그널 원칙
- 비표준 시그널 타입 0건 확인
- confidence 5~10 범위 확인

## 6단계: DB 저장 + 새 종목 처리
- INSERT 전 중복 체크 (video_id 기준)
- 새 종목 자동 감지 → Yahoo Finance/네이버금융 가격 수집
- `data/signal_prices.json`, `data/stock_tickers.json` 업데이트
- ⚠️ 신규 ticker → 재빌드 필요 (정적 생성 구조)

## 7단계: QA Gate 3 (프론트 검증)
- 인플루언서 슬러그 페이지 존재 확인
- 시그널 렌더링 확인
- 실패 시 배포 차단

## 주의사항
- published_at = 영상 업로드 날짜 (**크롤링 날짜 사용 금지**)
- channel_name = 실제 채널명 (**핸들 사용 금지**)
- **시그널 재분석은 JAY 승인 필수**
- **배포 시 gh-pages orphan push 사용** (→ `deploy.md` 참조, repo 1GB limit 주의)

## 파이프라인 기존 버그 (수정 완료)
- extract_flat upload_date 미반환 → 보완 추출 구현
- ticker: stock/ticker/market 분리 전달 수정
- speakers 테이블 참조 수정 (influencer_speakers 아님)
- speaker_name 폴백 channel_name 구현
- Windows npm.cmd 수정
- Gate 2 새 채널 완화 구현

## 크립토 종목 검증 (Gate 3 체크 10)
채널에 크립토 시그널이 포함된 경우 자동 검증:

| 체크 | 내용 | 실패 시 |
|------|------|---------|
| -USD 매핑 | BTC→BTC-USD, ETH→ETH-USD 등 yfinance ticker 확인 | ⚠️ 경고 |
| 가격 누락 | stockPrices.json에 ticker 존재 여부 | ⚠️ 경고 |
| 가격 0/$0 | currentPrice가 0 또는 None | ⚠️ 경고 |
| 극소수 가격 | $0.01 미만 → 프론트 소수점 6~8자리 표시 확인 | 💰 안내 |

**CoinGecko fallback**: yfinance에서 가격을 못 가져오는 크립토 종목은 CoinGecko API로 시도.
```bash
# yfinance 실패 시 CoinGecko 수집
python scripts/fetch_crypto_prices.py --ticker SHIB --source coingecko
```

**극소수 가격 표시**: $0.01 미만 가격은 `formatStockPrice()`가 소수점 6~8자리를 반올림 없이 절삭 표시.
- 예: $0.00001234 → `$0.00001234` (8자리)
- 예: $0.005 → `$0.0050` (4자리, < $1 브랜치)

## 채널 추가 후 검증
- published_at NULL 0건
- ticker NULL 0건
- speaker_id NULL 0건
- return_pct 계산 완료
- signal_prices.json 포함
- stock_tickers.json 포함
- stockPrices.json 차트 포함
- speaker_slugs.js 실행
- 프로필 페이지 빌드 포함
- 종목 페이지 가격 정상
- **크립토: -USD 매핑 + 가격 0 + 극소수 가격 확인**
