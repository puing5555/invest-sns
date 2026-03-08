# My Portfolio 모듈 주의사항

- 인증 필수 페이지
- authLoading 3초 타임아웃 있음 (2026-03-08 추가)
  → 3초 지나면 /login으로 리다이렉트
- user_stocks 테이블: quantity, avg_buy_price는 nullable
- "수익률 보려면 매수 정보 입력하세요" 버튼 있음
