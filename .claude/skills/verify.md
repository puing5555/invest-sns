# verify — 배포 전 검증

## 실행 절차

### 1. 빌드
```bash
npm run build
```
- 실패 시 → ⛔ 즉시 중단, 에러 보고

### 2. out/ 폴더 존재 확인
```bash
test -f out/index.html && test -f out/404.html && test -f out/dashboard/index.html
```

### 3. 주요 종목 페이지 존재 확인
```bash
# 한국 대표
test -f out/stock/005930/index.html && echo "OK: 삼성전자"
# 크립토
test -f out/stock/BTC/index.html && echo "OK: BTC"
# 미국
test -f out/stock/AAPL/index.html && echo "OK: AAPL"
```
- 하나라도 없으면 → ⛔ 배포 중단

### 4. 컴포넌트 import 정상 확인
- 새로 추가/변경된 컴포넌트가 있으면:
  - dynamic import 사용 여부 확인 (`next/dynamic`)
  - optional chaining (`?.`) 사용 여부 확인
  - 에러 바운더리 존재 여부 확인
- JS 번들 크기 확인: `/stock/[code]` 페이지 3.5MB 이하

### 5. API 키 유출 점검
```bash
grep -r "sk-ant\|supabase_service" out/
```
- 매칭 시 → ⛔ 배포 즉시 중단

### 6. 결과 리포트
```
✅ 빌드: 성공
✅ out/ 존재: index.html, 404.html, dashboard
✅ 종목 페이지: 005930, BTC, AAPL
✅ 컴포넌트: dynamic import 확인
✅ API 키: clean
→ 배포 가능
```

## 문제 발견 시
- 배포 중단
- 문제 항목 + 원인 + 수정 방안 보고
- 수정 후 verify 재실행
