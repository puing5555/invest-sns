# Supabase 주의사항

- RLS 비활성화 상태 (대부분의 테이블)
- anon key만 프론트에서 사용
- service key는 .env.local에만, 프론트 코드에 절대 노출 금지
- Supabase 프로젝트: invest-sns (puing5555's Org, FREE 플랜)
- supabase npm 패키지 깨짐 → REST API 직접 사용
