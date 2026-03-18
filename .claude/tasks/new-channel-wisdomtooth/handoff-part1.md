# 위즈덤투스 채널 추가 — 핸드오프 Part 1
**작성**: 2026-03-16
**상태**: 채널 추가 완료, 커밋/배포 미완

## 이번 세션에서 한 일

### 1. 위즈덤투스 채널 추가 (7단계 파이프라인 완료)
- 155개 영상 중 116개 통과 → 112영상, 211시그널 Supabase INSERT
- 신규 종목 44개 가격 수집, IRNE→IREN 교정
- speaker_id null 문제 근본 수정 (테이블명 오류 + 채널명 폴백 + 백필)
- 인플루언서 프로필 404 해결 (generateStaticParams 로컬 JSON 기반)
- signal_prices.json 폴백 추가로 종목 페이지 $0 표시 수정

### 2. stockPrices.json 최적화 + 배포
- 22MB → 12MB (5년치 → 3년치 트리밍, 375K → 227K entries)
- npm run build 성공
- gh-pages orphan 방식 force push 완료

## 관련 커밋 (master)
```
1b113583 종목 페이지 $0 수정: signal_prices.json 폴백 추가
b542a3e7 신규 종목 검증 + 가격 수집: 44개 유효, IRNE→IREN 교정
69e48340 위즈덤투스 3대 문제 실제 수정 완료 + 종목 링크 추가
d074eab5 백필 완료 + 빌드: 116영상 날짜 복원, 208시그널 ticker 설정, 321종목 페이지
71bd91f2 채널 추가 3대 문제 근본 수정: 날짜/ticker/종목 연결
1839272c speaker_id null 근본 수정: 테이블명 오류 + 채널명 폴백 + 백필
ca7fb87e slugToSpeaker 클라이언트 런타임 수정: require → static import
25f70ade 인플루언서 프로필 시그널 미표시 근본 수정: slug→이름 역매핑 추가
0d452ae2 speaker slug 생성에 채널명 포함: speaker-mzeuvs 404 수정
f9a0262e 인플루언서 프로필 404 근본 해결: generateStaticParams를 로컬 JSON 기반으로 변경
```

## 미커밋 변경 (working tree)
- `data/stockPrices.json`, `public/stockPrices.json` — 3년치 트리밍
- `components/ReportDetailModal.tsx` — 변경 내용 미확인
- `data/analyst_reports.json` — 변경 내용 미확인
- 루트의 임시 스크립트 30+개 삭제 (D 상태)
- `out/` 폴더 — 최신 빌드 산출물

## 미완료 작업 (우선순위)
1. **미커밋 변경 정리 + 커밋** — stockPrices 트리밍, 임시 스크립트 삭제 등
2. **라이브 사이트 확인** — https://puing5555.github.io/invest-sns/ 에서 위즈덤투스 채널/시그널 표시 확인
3. **기존 타임스탬프 1,000+개 재분석** — CLAUDE.md에 언급된 대기 작업
4. **탭 구조 변경** — TODAY/SNS/탐색/포트폴리오/프로필 (CLAUDE.md 예정)
