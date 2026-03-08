# SOUL.md — invest-sns AI 코딩 가이드 (OpenClaw/Claude Code용)

## 핵심 규칙 (7개)
1. API 키 소스코드 하드코딩 절대 금지 → .env.local만
2. 배포 전 체크리스트 필수: .claude/skills/deploy.md
3. 채널 추가 시 7단계 파이프라인: .claude/skills/channel-add.md
4. QA Gate 실패 시 다음 단계 진행 금지
5. 시그널 재분석(Sonnet)은 JAY 승인 없이 실행 금지
6. 크롤링 날짜를 published_at으로 사용 금지
7. 모델 변경 시 전체 파일 grep으로 구버전 제거

## 상세 문서
- 전체 아키텍처: docs/architecture.md
- 채널 추가 절차: .claude/skills/channel-add.md
- 배포 절차: .claude/skills/deploy.md
- 장애 대응: docs/runbooks/incident-response.md
- API 키 교체: docs/runbooks/api-key-rotation.md
- 엔지니어링 결정: docs/decisions/

## 모듈별 주의사항
- app/dashboard/CLAUDE.md → 공개 페이지, API fallback 필수
- app/my-portfolio/CLAUDE.md → 인증 필수, 3초 타임아웃
- app/api/CLAUDE.md → API 키 하드코딩 금지
- lib/supabase/CLAUDE.md → RLS 비활성화, 키 관리 주의

## 모델 설정
- CTO: claude-opus-4-6
- Dev/QA/Prompt: claude-sonnet-4-6
- cron 전부: openai/gpt-4o
- 파이프라인 분석: claude-sonnet-4-6

## 보안
- push 전: grep -r "sk-ant-api" --include="*.py" --include="*.js" --include="*.ts"
- 키 전달: 텔레그램 DM만
- 키 변경 시: gateway 재시작 필수
