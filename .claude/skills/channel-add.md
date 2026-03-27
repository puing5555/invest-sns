# 채널 추가 7단계 파이프라인

## 전체 흐름

```
[1. 채널 등록]
    ↓
[2. 메타데이터 수집] ← yt-dlp
    ↓
[3. QA Gate 1] ⛔ 실패 시 중단
    ↓
[4. 자막 추출 + 시그널 분석] ← yt-dlp + V15.2 + channel_info
    ↓
[5. QA Gate 2] ⛔ 실패 시 중단
    ↓
[6. DB 저장 + 스코어카드 v4 재생성]
    ↓
[7. QA Gate 3] ⛔ 실패 시 배포 차단
    ↓
[배포 --force push]
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
- `pipeline_config.py` CHANNEL_OWNERS에 추가
- `data/speaker_slugs.json`에 slug 추가
- `lib/speakerSlugs.ts`에 매핑 추가

## 2단계: 메타데이터 수집
수집 필드: video_id, title, published_at, duration_seconds, view_count

⚠️ **published_at = 영상 업로드 날짜** (크롤링 날짜 사용 절대 금지)

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
| published_at | 크롤링 날짜 아닌지 | ⛔ 중단 |
| 채널명 | 영문 핸들만 | ⚠️ 경고 |
| 중복 | DB에 이미 존재 | ⚠️ 스킵 |

## 4단계: 자막 추출 + 시그널 분석
- yt-dlp로 ko 자막 우선, 없으면 en
- **V15.2 프롬프트**로 Sonnet 분석
- **channel_info 필수 주입**: `{CHANNEL_OWNER}`, `{CHANNEL_TYPE}` 플레이스홀더
- 자막 한도: **20000자**
- 시그널 타입: **매수/긍정/중립/부정/매도** (5단계)
- 레이트 리밋: 20개 후 60초 휴식, API 간 5초

## 5단계: QA Gate 2 (시그널)
- 타임스탬프 유효성
- 1영상 1종목 1시그널 원칙
- 비표준 시그널 타입 0건 확인
- confidence 5~10 범위 확인
- key_quote 20~200자 범위
- ticker 접미사(.HK/.T/.KS) 없는지
- 비상장 종목에 ticker 잘못 매핑 안 됐는지

## 6단계: DB 저장 + 스코어카드 v4
- INSERT 전 중복 체크 (video_id 기준)
- 새 종목 자동 감지 → Yahoo Finance/네이버금융 가격 수집
- `data/stockPrices.json` 업데이트 (종목명 포함!)
- **스코어카드 v4 재생성** (`python scripts/calc_influencer_scorecard.py`)
  - 스윙(1Y)/중기(1~3Y)/장기(3Y+) 3구간
  - 하이브리드 fallback (1Y→3개월+ current→pending)
  - EVAL_GRACE_DAYS=90
  - TOP3/WORST3: current 기준, 종목 중복 제거
- **리포트 재생성** (`python scripts/generate_influencer_report.py`)
- ⚠️ 신규 ticker → 재빌드 필요 (정적 생성 구조)

## 7단계: QA Gate 3 (프론트 검증)
| 체크 | 내용 |
|------|------|
| 프로필 페이지 | 인플루언서 슬러그 페이지 존재 |
| 시그널 렌더링 | 수익률 표시 (current 컬러 + 1Y 회색) |
| 3구간 카드 | 스윙/중기/장기 적중률 카드 표시 |
| 탐색 카드 | 장기>중기>스윙 fallback + "(장기)" 표시 |
| 수익률 색상 | 3개월 미만 회색, 3개월+ 컬러 |
| 크립토 가격 | -USD 매핑 + 가격 0 확인 |
| 배포 | --force push 필수 |

## 주의사항
- published_at = 영상 업로드 날짜 (**크롤링 날짜 사용 금지**)
- channel_name = 실제 채널명 (**핸들 사용 금지**)
- **시그널 재분석은 JAY 승인 필수**
- **배포 시 gh-pages --force push 사용** (→ `deploy.md` 참조, repo 1GB limit 주의)
- 크립토 채널: 동일 코인 반복 → dedup 후 scored 적은 건 정상

## 파이프라인 기존 버그 (수정 완료)
- extract_flat upload_date 미반환 → 보완 추출 구현
- ticker: stock/ticker/market 분리 전달 수정
- speakers 테이블 참조 수정 (influencer_speakers 아님)
- speaker_name 폴백 channel_name 구현
- Windows npm.cmd 수정
- Gate 2 새 채널 완화 구현
- speaker_id UUID 타입 에러 → speakers 테이블 경유만 (2026-03-26 수정)
- speakerSlugs 짧은 이름 우선 버그 → DB name과 일치시킴

## 크립토 종목 검증 (Gate 3 체크 10)
| 체크 | 내용 | 실패 시 |
|------|------|---------|
| -USD 매핑 | BTC→BTC-USD 등 yfinance ticker 확인 | ⚠️ 경고 |
| 가격 누락 | stockPrices.json에 ticker 존재 여부 | ⚠️ 경고 |
| 가격 0/$0 | currentPrice가 0 또는 None | ⚠️ 경고 |
| 극소수 가격 | $0.01 미만 → 소수점 6~8자리 표시 확인 | 💰 안내 |

**CoinGecko fallback**: yfinance 실패 시 CoinGecko API (현재 401 차단 — Pro 키 필요)

## 채널 추가 후 검증 체크리스트
- [ ] published_at NULL 0건 (영상 업로드 날짜인지!)
- [ ] ticker NULL → 비상장이면 정상, 상장이면 수정
- [ ] speaker_id NULL 0건
- [ ] stockPrices.json에 종목명(name) 포함
- [ ] speaker_slugs.json + speakerSlugs.ts 등록
- [ ] pipeline_config.py CHANNEL_OWNERS 등록
- [ ] 프로필 페이지 빌드 포함
- [ ] 종목 페이지 가격 정상
- [ ] 스코어카드 + 리포트 재생성
- [ ] --force 배포
