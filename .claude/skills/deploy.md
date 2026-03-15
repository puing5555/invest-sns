# 배포 절차

## 체크리스트 (전부 통과해야 배포 가능)
- [ ] `npm run build` 성공
- [ ] `out/index.html` 존재
- [ ] `out/404.html` 존재
- [ ] `out/dashboard/index.html` 존재
- [ ] 주요 페이지 5개 로컬 확인: /, /dashboard, /explore, /explore/disclosure, /profile
- [ ] API 키 grep clean: `grep -r "sk-ant\|eyJhbG\|supabase_service" out/`
- [ ] `out/` 폴더만 gh-pages에 push
- [ ] 배포 후 라이브 URL HTTP 200 확인

## 배포 명령
```bash
# 1. 빌드
npm run build

# 2. gh-pages 브랜치에 배포 (orphan 방식)
cd <deploy-directory>
git checkout gh-pages
cp -r <project-root>/out/. .
git add -A
git commit -m "deploy: $(date +%Y-%m-%d)"
git push origin gh-pages
```

## 라이브 확인
```bash
curl -s -o /dev/null -w "%{http_code}" https://puing5555.github.io/invest-sns/
```

## 절대 금지
- API 키가 grep에 걸리면 **배포 즉시 중단**
- 빌드 실패 시 이전 빌드로 배포 금지
- `out/` 폴더 없이 배포 금지
- 프론트엔드 수정 후 빌드 확인 없이 배포 금지 (CLAUDE.md Rules #8)
