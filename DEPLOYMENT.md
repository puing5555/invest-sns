# 🚀 Vercel 배포 가이드

## 1. Vercel 계정 연결
1. [vercel.com](https://vercel.com) 가입/로그인
2. GitHub 계정 연결
3. 해당 레포지토리 import

## 2. 환경변수 설정
Vercel 프로젝트 Settings > Environment Variables에서 설정:

```bash
# Supabase 설정
NEXT_PUBLIC_SUPABASE_URL=https://arypzhotxflimroprmdk.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A
```

## 3. 빌드 설정
- Framework Preset: **Next.js**
- Build Command: `npm run build`
- Output Directory: `out`
- Node.js Version: **18.x** (권장)

## 4. 도메인 설정
배포 후 custom domain 연결 가능:
- Settings > Domains
- DNS 설정 (A record / CNAME)

## 5. 배포 상태 확인
- ✅ Build: 성공 (51 pages)
- ✅ 환경변수: 설정됨
- ✅ Static Export: 지원
- ✅ 실제 데이터: 통합 완료 (42개 시그널)

## 현재 데이터 상태
- **13명 인플루언서** (실제 3protv 데이터)
- **24개 종목** 시그널
- **42개 피드 포스트** (실시간 시그널)
- **탑 인플루언서**: 차영주(9), 김장열(5), 박병창(5)

## 배포 후 확인사항
1. 메인 피드 페이지 → 실제 시그널 데이터 표시
2. 인플루언서 페이지 → 13명 실제 인플루언서 
3. 시그널 통계 → 정확도/수익률 표시
4. 반응형 UI → 모바일 최적화

## 📝 다음 업데이트 예정
- YouTube 자막 차단 해제 시 추가 시그널
- 실시간 Supabase 연동
- 알림 시스템 고도화