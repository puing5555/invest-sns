# 배포 절차

## 체크리스트 (전부 통과해야 배포 가능)
- [ ] **C 드라이브 여유 공간 500MB 이상** (`df -h /c` 또는 `wmic logicaldisk get size,freespace`)
  - 500MB 이하 → ⛔ 빌드/배포 중단, 디스크 정리 먼저
- [ ] `npm run build` 성공
- [ ] `out/index.html` 존재
- [ ] `out/404.html` 존재
- [ ] `out/dashboard/index.html` 존재
- [ ] 주요 페이지 5개 로컬 확인: /, /dashboard, /explore, /explore/disclosure, /profile
- [ ] API 키 grep clean: `grep -r "sk-ant\|eyJhbG\|supabase_service" out/`
- [ ] `out/` 폴더만 gh-pages에 push
- [ ] 배포 후 라이브 URL HTTP 200 확인

## 배포 명령 (gh-pages orphan push)
```bash
# 0. 디스크 여유 확인
df -h /c | tail -1  # 500MB 이상 확인

# 1. 빌드
npm run build

# 2. /tmp에 임시 배포 디렉토리 생성 (orphan 방식)
cd /tmp && rm -rf invest-sns-deploy
mkdir invest-sns-deploy && cd invest-sns-deploy
git init
git remote add origin https://github.com/puing5555/invest-sns.git
git fetch origin gh-pages
git checkout gh-pages

# 3. 기존 파일 삭제 → 빌드 결과 복사 → 커밋 & 푸시
git rm -rf . --quiet 2>/dev/null
cp -r /c/Users/Mario/work/invest-sns/out/. .
git add -A
git commit -m "deploy: $(date +%Y-%m-%d)"
git push origin gh-pages

# 4. 정리
rm -rf /tmp/invest-sns-deploy
```

⚠️ **orphan push를 쓰는 이유**: git history 누적 방지 (repo 401MB, 1GB limit 주의)

## 라이브 확인
```bash
curl -s -o /dev/null -w "%{http_code}" https://puing5555.github.io/invest-sns/
```

## 절대 금지
- API 키가 grep에 걸리면 **배포 즉시 중단**
- 빌드 실패 시 이전 빌드로 배포 금지
- `out/` 폴더 없이 배포 금지
- 프론트엔드 수정 후 빌드 확인 없이 배포 금지 (CLAUDE.md Rules #8)
