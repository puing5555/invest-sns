# 크롤링 & 수익률 계산 인프라

## 1. 네이버 리서치 크롤러 (애널리스트 리포트)

### 실행
```bash
node scripts/crawl-naver-research-v2.js          # 전체 (처음부터)
node scripts/crawl-naver-research-v2.js --resume  # 이어서
```

### 동작 방식
1. 45종목 × 최대 30페이지 순회 (3년 rolling window)
2. 목록 페이지 → 상세 페이지 2단계 크롤링
3. HTML 인코딩: **EUC-KR** (`TextDecoder('euc-kr')`)
4. 정규식 추출: target_price (6패턴), opinion, analyst (한글명)
5. nid 기준 중복 제거 + 날짜순 정렬
6. 주기적 저장 → `data/analyst_reports.json`

### 설정
| 항목 | 값 |
|------|---|
| 종목 수 | 45 (KR_TICKERS 배열) |
| 기간 | 3년 (자동 계산) |
| 상세 딜레이 | 1,500ms |
| 페이지 딜레이 | 2,000ms |
| 종목간 딜레이 | 3,000ms |
| 지터링 | +random(1,000ms) |
| 429 대응 | 60초 대기, 최대 3회 재시도 |

### 진행 상황 파일
- `data/crawl_progress.json` — 중단/재개 추적

### 종목 추가 시
1. `scripts/crawl-naver-research-v2.js`의 `KR_TICKERS` 배열에 추가
2. `TICKER_NAMES`에 한글명 매핑 추가
3. `--resume`으로 해당 종목만 크롤링
4. 프론트엔드 `app/explore/analyst/page.tsx`의 `TICKER_NAMES`에도 추가

## 2. 수익률 계산 (yfinance)

### 실행
```bash
python scripts/calc_analyst_returns.py          # 미계산분만
python scripts/calc_analyst_returns.py --force  # 전체 재계산
```

### 알고리즘
1. KRX 코드 → yfinance 형식 변환 (예: `005930` → `005930.KS`)
2. 종목별 5년 가격 히스토리 캐시 (API 호출 최소화)
3. `published_at` 기준 종가 조회 (±5 영업일 허용)
4. forward return 계산: `((target_price - base_price) / base_price) × 100`

### 추가되는 필드
| 필드 | 설명 |
|------|------|
| return_3m | 3개월 (90일) forward return % |
| return_6m | 6개월 (180일) forward return % |
| return_12m | 12개월 (365일) forward return % |
| price_at_signal | 발언일 종가 |
| price_current | 현재가 |
| target_achieved | 현재가 ≥ target_price 여부 |

### ⚠️ 수익률 필수 규칙 (docs/RETURNS_SPEC.md)
- **날짜**: `published_at` 사용 (크롤링 날짜 절대 금지)
- **미래 날짜**: target_date > today이면 None 반환
- **프록시**: Yahoo Finance IP 차단 → Webshare residential 프록시 필요
- **에러**: 실패 시 로그 기록, "-"로 대체 금지

## 3. 인플루언서 자막 크롤링

### 실행 (채널 파이프라인)
```bash
python scripts/auto_pipeline.py --channel URL --execute
```

### 도구
- **yt-dlp**: 자막 추출 (ko 우선, 없으면 en)
- **레이트 리밋**: 20개 후 5분 휴식, 요청간 2~3초

### 필터링 (pipeline_config.py)
- 제외: 60초 미만(Shorts), 7200초 초과(라이브), 조회수 1000 미만
- 키워드 제외: 일상/먹방/여행/멤버십/쇼츠/광고
- 키워드 통과: 종목명/매수/매도/전망/분석/비트코인

## 4. 공통 인프라

### 환경변수 (.env.local)
```
ANTHROPIC_API_KEY=sk-...
NEXT_PUBLIC_SUPABASE_URL=https://...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

### 레이트 리밋 패턴
| 컴포넌트 | 전략 |
|----------|------|
| 네이버 크롤 | 429 → 60s 대기 + 3회 재시도 |
| Claude API | RateLimitError → 30s × attempt |
| Eval 배치 | 5건마다 15s 대기 |
| yt-dlp | 20건마다 5분 휴식 |

### Python 의존성
```
anthropic, yfinance, requests, beautifulsoup4, supabase, yt-dlp
```
