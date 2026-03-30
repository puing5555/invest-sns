# 아키텍처

_Last updated: 2026-03-08_

## 데이터 흐름
YouTube → yt-dlp(자막) → Sonnet(분석) → Supabase(저장) → Next.js(표시)

## DB 테이블 (주요)
- influencer_channels: 채널 정보 (10개 채널)
- influencer_signals: 시그널 (종목/신호/발언/타임스탬프) — 901건
- influencer_videos: 영상 메타데이터
- analyst_reports: 애널리스트 리포트 (565건)
- research_invest_platforms: 투자 플랫폼 리서치
- signal_prices: 시그널별 가격 데이터 (952건)

## 인증
- Supabase Auth (이메일/소셜)
- 공개 페이지: /, /dashboard, /explore, /explore/disclosure, /feed, /my-watchlist
- 인증 필요: /my-portfolio, /profile
- authLoading 3초 타임아웃 → /login 리다이렉트 (2026-03-08 추가)

## 배포
- GitHub Pages (정적 export)
- gh-pages 브랜치에 out/ 폴더 push
- trailingSlash: true (URL이 /route/index.html 형태)
- 배포 워크트리: D:\work\invest-sns-deploy

## 외부 API
- Yahoo Finance: 미국장 시황 (5분 갱신)
- 네이버금융: 국내장 (KRX 직접 접근 차단되어 대체)
- Supabase REST: 데이터 CRUD
- yt-dlp: YouTube 자막/메타데이터

## cron (16개 — 전부 GPT-4o)
기본 cron (12개):
- Patrol: 6시간마다
- Research 3종: 08:00/14:00/17:00
- Copywriter 텍스트QA: 11:30
- Copywriter 데일리: 21:00
- 일일요약: 22:30
- 핀플루언서법: 매주 월 10:00
- 아이디어소스: 11:00

브리핑 cron (4개):
- 모닝: 07:00
- 장시작: 09:05
- 장마감: 16:00
- 미국장: 23:00

## 현재 데이터 규모 (2026-03-08 기준)
- 시그널: 901건
- 채널: 10개 (삼프로TV, 코린이아빠, 부읽남TV, 이효석아카데미, 슈카월드, 달란트투자, 세상학개론, 월가아재, 올랜도캠퍼스, Godofit)
- 애널리스트 리포트: 565건
- 가격 데이터: 155개 종목
