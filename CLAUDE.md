# invest-sns

## Purpose
한국 주식 유튜버/인플루언서의 종목 시그널을 AI로 자동 수집·분석하여
개인투자자에게 신뢰도 기반 투자 정보를 제공하는 플랫폼.

## Stack
- Frontend: Next.js 14 + Tailwind (Static Export → GitHub Pages)
- Backend: Supabase (PostgreSQL + Auth + Storage)
- AI: Claude Sonnet (시그널 분석), GPT-4o (cron)
- Data: yt-dlp (자막), Yahoo Finance / 네이버금융 (가격)

## Repo Map
- app/ → 페이지 (Next.js App Router)
- lib/ → 유틸리티 (Supabase client, API helpers)
- scripts/ → 데이터 파이프라인, QA Gate
- data/ → JSON 데이터 (시그널, 가격, 채널 목록)
- docs/ → 아키텍처, ADR, 운영 매뉴얼
- docs/RETURNS_SPEC.md — ⚠️ 수익률/날짜 처리 필수 규칙 (반드시 읽을 것)
- .claude/skills/ → 워크플로우 (채널 추가, 배포 등)

## Rules (절대)
1. API 키 소스코드 하드코딩 금지 → .env.local만
2. 배포 전 체크리스트 필수 통과 (.claude/skills/deploy.md)
3. 채널 추가 시 7단계 파이프라인 필수 (.claude/skills/channel-add.md)
4. QA Gate 실패 시 다음 단계 진행 금지
5. 시그널 재분석(Sonnet)은 JAY 승인 없이 실행 금지
6. 크롤링 날짜를 published_at으로 사용 금지
7. 모델 변경 시 전체 파일 grep으로 구버전 제거

## Commands
- `npm run build` → Static export (out/)
- `python scripts/qa/run_all_gates.py` → QA 전체 실행
