# invest-sns

## Purpose
한국 주식 유튜버/인플루언서의 종목 시그널을 AI로 자동 수집·분석하고,
증권사 애널리스트 리포트의 적중률/수익률을 추적하여
개인투자자에게 신뢰도 기반 투자 정보를 제공하는 플랫폼.

사이트: https://puing5555.github.io/invest-sns/

## Stack
- Frontend: Next.js 14 + Tailwind (Static Export → GitHub Pages)
- Backend: Supabase (PostgreSQL + Auth + Storage)
- AI: Claude Sonnet (`claude-sonnet-4-20250514`) — 시그널 분석, 리포트 AI 요약
- Data: yt-dlp (자막), Yahoo Finance / 네이버금융 (가격), 네이버 리서치 (애널리스트 리포트)
- Deploy: GitHub Pages (gh-pages branch, orphan 방식)

## Repo Map
- `app/` → 페이지 (Next.js App Router)
  - `app/explore/analyst/` → 애널리스트 리포트 (최신/종목별/애널리스트별)
  - `app/stock/[code]/` → 종목 상세 페이지
  - `app/profile/` → 인플루언서/애널리스트 프로필
- `components/` → 공통 컴포넌트 (ReportDetailModal 등)
- `lib/` → 유틸리티 (Supabase client, API helpers)
- `scripts/` → 데이터 파이프라인, 크롤러
  - `scripts/crawl-naver-research-v2.js` → 애널리스트 리포트 3년치 크롤러
  - `scripts/calc_analyst_returns.py` → forward return 계산 (yfinance)
  - `scripts/anyuhwa/step5_pipeline.py` → 인플루언서 시그널 파이프라인
- `data/` → JSON 데이터
  - `data/analyst_reports.json` → 애널리스트 리포트 (45종목, 3년치)
  - `data/stockPrices.json` → 종목 가격 (5년치)
- `prompts/pipeline_v12.2.md` → 인플루언서 시그널 분석 프롬프트
- `docs/` → 아키텍처, 스펙 문서
  - `docs/RETURNS_SPEC.md` — ⚠️ 수익률/날짜 처리 필수 규칙
- `.claude/skills/` → 워크플로우

## 핵심 시스템

### 1. 인플루언서 시그널 (기존)
- 11개 채널, 1,133개 시그널, 70+ speakers
- 파이프라인: step1_collect → step2_filter → step5_pipeline (자막추출→Claude분석→DB→수익률)
- Eval 정확도: 55% (V12.2 프롬프트)

### 2. 애널리스트 리포트 (신규)
- 45종목, 3년치 네이버 리서치 크롤링
- 수집 필드: 종목, 증권사, 애널리스트, 목표가, 투자의견, 제목, PDF 링크
- 수익률: forward return 3개월/6개월/12개월 (yfinance)
- 기본 정렬: 12개월 수익률
- 컨센서스: 최근 3개월 리포트 기준

## Rules (절대)
1. API 키 소스코드 하드코딩 금지 → .env.local만
2. 배포 전 체크리스트 필수 통과 (.claude/skills/deploy.md)
3. 채널 추가 시 7단계 파이프라인 필수 (.claude/skills/channel-add.md)
4. QA Gate 실패 시 다음 단계 진행 금지
5. 시그널 재분석(Sonnet)은 JAY 승인 없이 실행 금지
6. 크롤링 날짜를 published_at으로 사용 금지
7. 모델 변경 시 전체 파일 grep으로 구버전 제거
8. 프론트엔드 수정 후 반드시 `npm run build` 성공 확인

## Commands
- `npm run build` → Static export (out/)
- `npm run dev` → 로컬 개발 서버
- `node scripts/crawl-naver-research-v2.js` → 애널리스트 리포트 크롤링
- `node scripts/crawl-naver-research-v2.js --resume` → 이어서 크롤링
- `python scripts/calc_analyst_returns.py` → forward return 계산
- `python scripts/qa/run_all_gates.py` → QA 전체 실행

## 현재 상태 (2026-03-15)
- 인플루언서 시그널: 1,133개 (11개 채널)
- 애널리스트 리포트: 크롤링 진행 중 (45종목 3년치)
- 기존 타임스탬프 1,000+개 재분석 필요
- 탭 구조 변경 예정 (TODAY/SNS/탐색/포트폴리오/프로필)
