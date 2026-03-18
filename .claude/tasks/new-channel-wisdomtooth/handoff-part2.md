# V15.0 프롬프트 고도화 + 정답지 정제 — 핸드오프 Part 2
**작성**: 2026-03-18
**상태**: V15 eval 완료, V14.0 운영 유지, 정답지 정제 완료

## 이번 세션에서 한 일

### 1. 배포
- gh-pages orphan push로 애널리스트 이름 데이터 배포 완료
- 미커밋 변경 정리: PDF 344개 삭제, progress JSON, tmp 파일, out/ 빌드

### 2. 삼성전자(005930) 리포트 분석
- 전체 359건 중 analyst null 54건 (85.0% 추출률)
- 한화투자증권 18건으로 null 최다 (PDF 포맷 문제 추정)
- StockAnalystTab → data/analyst_reports.json 직접 import 확인

### 3. V15.0 프롬프트 고도화
- 위즈덤투스 211건 정답지 생성 (eval_ground_truth_wisdomtooth_211.json)
- V15.0: 매수 판별 기준 강화 + few-shot 7개 추가
  - 결과: 74.3% (V14 대비 -5.0%p) — **긍정→매수 과잉 상향 18건**
- V15.1: 가드레일 4가지 추가 (타인매매/추천거부/유보조건부/현황보고)
  - 결과: 77.1% (V14 대비 -1.8%p) — regression 줄었으나 여전히 마이너스
- **결론: V14.0 운영 유지** (78.9%로 최고)

### 4. 정답지 정제 (JAY 승인 완료)
- 위즈덤투스 4건: 압셀라바이오/브로드컴/일라이릴리/소파이 긍정→매수
- 안유화 8건: 비트코인×4/BYD/지리자동차 매수→긍정, 현대자동차 긍정→중립 등
- 통합 280건 정답지: eval_ground_truth_280.json

### 5. Skill 문서 업데이트
- deploy.md: C드라이브 500MB 체크 + gh-pages orphan push 절차
- channel-add.md: 파이프라인 버그 이력 6건 + 채널 추가 후 검증 10건

## 커밋 이력 (2026-03-18)
```
e4901a8d channel-add.md: 파이프라인 버그 이력 + 채널 추가 후 검증 체크리스트 추가
41d04f31 channel-add.md: gh-pages orphan push 주의사항 추가
aa87e9e2 deploy.md: C드라이브 500MB 체크 + gh-pages orphan push 절차 추가
5f9fe43c V15.0/V15.1 프롬프트 + 280건 정답지 정제 + eval 결과
7d340c10 out/ 빌드 산출물 업데이트 (2026-03-18 배포분)
11d646b3 파이프라인 중간 산출물 추가: progress JSON 7개 + tmp 배치 + 추출 스크립트 + 핸드오프
6b1b1ae3 애널리스트 PDF 344개 삭제 (이미 파싱 완료된 파일 정리)
```

## 주요 수치
| 항목 | 값 |
|------|-----|
| 운영 프롬프트 | V14.0 (78.9%, 280건 기준) |
| 정답지 | 280건 (안유화 69 + 위즈덤투스 211) |
| V15.0 정확도 | 74.3% (불채택) |
| V15.1 정확도 | 77.1% (불채택) |
| Git repo 크기 | 401 MB (1GB limit의 40%) |
| gh-pages 크기 | 39.6 MB |

## 미완료 작업 (우선순위)
1. **기존 타임스탬프 1,000+개 재분석** — CLAUDE.md 대기 작업
2. **탭 구조 변경** — TODAY/SNS/탐색/포트폴리오/프로필
3. **애널리스트 null 54건 (삼성전자)** — 한화투자증권 PDF 포맷 대응
4. **git history 정리** — node_modules/supabase.exe 등 400MB 차지 (filter-repo 검토)
5. **V15.2 추가 튜닝** — regression 22건 타겟 few-shot (V14 대비 개선 시)
