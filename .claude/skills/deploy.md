# 배포 절차

## 체크리스트 (전부 통과해야 배포 가능)
☐ npm run build 성공
☐ out/index.html 존재
☐ out/404.html 존재
☐ out/dashboard/index.html 존재
☐ 주요 페이지 5개 로컬 확인: /, /dashboard, /explore, /explore/disclosure, /profile
☐ API 키 grep clean
☐ out/ 폴더만 gh-pages에 push
☐ 배포 후 라이브 URL HTTP 200 확인

## 배포 명령
```bash
npm run build
cd C:\Users\Mario\invest-sns-deploy
git checkout gh-pages
cp -r ../invest-sns/out/. .
git add -A
git commit -m "deploy: $(date)"
git push origin gh-pages
```

## 절대 금지
- API 키가 grep에 걸리면 배포 중단
- 빌드 실패 시 이전 빌드로 배포 금지
- out/ 폴더 없이 배포 금지
