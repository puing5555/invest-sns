# 채널 추가 7단계 파이프라인

## 전체 흐름

```
[1. 채널 등록]
    ↓
[2. 메타데이터 수집] ← yt-dlp
    ↓
[3. 메타데이터 검증] ← 자동 QA Gate 1 ⛔ 실패 시 중단+보고
    ↓
[4. 자막 추출 + 시그널 분석] ← yt-dlp + V11.2
    ↓
[5. 시그널 검증] ← 자동 QA Gate 2 ⛔ 실패 시 중단+보고
    ↓
[6. DB 저장 + 수익률 계산]
    ↓
[7. 프론트 검증] ← 자동 QA Gate 3 ⛔ 실패 시 배포 차단
    ↓
[배포]
```

## 실행 명령
```bash
# 전체 자동 실행 (채널 URL만 넣으면 됨)
python scripts/auto_pipeline.py --channel https://www.youtube.com/@채널핸들 --execute

# QA 없이 실행 (긴급 시만)
python scripts/auto_pipeline.py --channel URL --execute --skip-qa

# 영상 목록 미리 확인 (dry-run)
python scripts/auto_pipeline.py --channel URL --dry-run
```

## 1단계: 채널 등록 규칙
- channel_name: YouTube 실제 채널명 (핸들 @xxx 사용 금지)
- channel_handle: @xxx 형식
- slug: 소문자+하이픈 (URL용)
- 영문만인 경우 경고 → 한글명 수동 확인

## 2단계: 메타데이터 수집
수집 필드: video_id, title(실제 제목), published_at(업로드날짜), duration_seconds, view_count

필터 제외:
- 60초 미만 (Shorts)
- 7200초 초과 (라이브 리플레이)
- 조회수 1000 미만
- 일상/먹방/여행/브이로그/구독/이벤트/경품/광고/협찬

필터 통과 키워드:
- 종목명, 매수/매도/포트폴리오/주가/실적/전망/분석/추천
- 코스피/나스닥/S&P/비트코인
- 긴급/속보/실적발표/어닝/컨콜

## 3단계: QA Gate 1 (메타데이터 검증)
| 체크 | 조건 | 실패 시 |
|------|------|---------|
| 제목 검증 | YouTube ID 패턴 있으면 | ⛔ 중단 |
| 날짜 검증 | 50%+ 같은 날짜면 | ⛔ 중단 |
| 날짜 범위 | 미래 날짜 있으면 | ⛔ 중단 |
| 채널명 | 영문 핸들만이면 | ⚠️ 경고 |
| 중복 | DB에 이미 있으면 | ⚠️ 스킵 |
| 필터 통과율 | 5% 미만이면 | ⚠️ 경고 |

## 4단계: 자막 추출
- yt-dlp로 ko 자막 우선, 없으면 en
- 자막 없는 영상 스킵 + 리포트 기록
- 레이트 리밋: 20개 후 5분 휴식, 요청 간 2-3초 딜레이

## 5단계: 시그널 분석 + QA Gate 2
- V11.2 프롬프트로 Sonnet 분석
- 시그널 타입: 매수/긍정/중립/부정/매도 (5단계만)
- QA Gate 2: 타임스탬프 필수, 1영상 1종목 원칙, 비표준 신호 0

## 6단계: DB 저장
- INSERT 전 중복 체크 (video_id 기준)
- signal_prices.json 업데이트

## 7단계: QA Gate 3 (프론트 검증)
- 인플루언서 슬러그 페이지 존재 확인
- 시그널 렌더링 확인
- 실패 시 배포 차단

## 주의사항
- published_at = 영상 업로드 날짜 (크롤링 날짜 사용 금지)
- channel_name = 실제 채널명 (핸들 사용 금지)
- 시그널 재분석은 JAY 승인 필수
