# API Routes 주의사항

- API 키 절대 하드코딩 금지 → .env.local에서만 읽기
- prompt-improvements/route.ts: 한글 인코딩 주의
  → 2026-03-08 mojibake 발생 이력 있음, 파일 수정 시 UTF-8 확인
