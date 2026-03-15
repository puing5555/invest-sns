# Skills 목차

## 상황별 가이드

| 상황 | 읽을 skill |
|------|-----------|
| 프론트엔드 컴포넌트 추가/수정 | `frontend.md` |
| 배포 | `deploy.md` |
| 새 채널 추가 | `channel-add.md` |
| 애널리스트 리포트 종목 추가 | `analyst-report.md` → `crawling.md` |
| 네이버 크롤링 / yfinance 수익률 | `crawling.md` |
| DB 스키마 확인 / 테이블 구조 | `supabase.md` |
| 프롬프트 수정 / 시그널 분석 규칙 | `prompt.md` |
| Eval 실행 / 정확도 비교 | `eval.md` |
| 프롬프트 개선 (전체 흐름) | `eval.md` → `prompt.md` |

## 각 skill 요약

| 파일 | 내용 |
|------|------|
| `index.md` | 이 파일. 상황→skill 매핑 |
| `frontend.md` | Next.js/Tailwind 컨벤션, 레이아웃, 시그널 색상, 빌드 |
| `deploy.md` | 배포 체크리스트, gh-pages push 절차 |
| `channel-add.md` | 인플루언서 채널 추가 7단계 파이프라인 |
| `analyst-report.md` | 애널리스트 리포트 데이터 구조, 종목 추가 |
| `crawling.md` | 네이버 리서치 크롤러, yfinance 수익률, 프록시, 레이트리밋 |
| `supabase.md` | DB 테이블 15개+ 스키마, RPC, Edge Function, 인덱스 |
| `prompt.md` | 시그널 5단계, V14.0 핵심 규칙, 프롬프트 수정 절차 |
| `eval.md` | 69건 정답지, eval 스크립트, 3그룹 분석법, 정확도 이력 |

## 참조 관계
```
channel-add.md ──→ prompt.md (시그널 분석 규칙)
                ──→ crawling.md (자막 추출, 레이트리밋)

analyst-report.md ──→ crawling.md (크롤링, 수익률 계산)
                  ──→ frontend.md (페이지 구조)

eval.md ──→ prompt.md (프롬프트 수정 절차)

prompt.md ──→ eval.md (정확도 검증)

deploy.md ──→ frontend.md (빌드 규칙)
```
