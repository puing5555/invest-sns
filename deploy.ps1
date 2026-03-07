#!/usr/bin/env pwsh
<#
.SYNOPSIS
  invest-sns 안전 배포 스크립트 v2
  소스코드 절대 보호 — gh-pages에 정적 파일만 push

.USAGE
  cd invest-sns
  .\deploy.ps1

.HOW IT WORKS
  1. master 브랜치 확인 (소스코드 보호)
  2. npm run build → out/ 폴더 생성
  3. git worktree로 별도 임시 폴더에 gh-pages 체크아웃
  4. out/ 내용물을 worktree에 복사 후 커밋&push
  5. worktree 제거 — 소스코드 폴더 변경 없음
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$REPO_ROOT = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path "$REPO_ROOT\invest-sns\package.json")) {
    $REPO_ROOT = $PSScriptRoot
}

Push-Location $PSScriptRoot

try {
    # ── 1. 현재 브랜치 확인 ──────────────────────────────
    $currentBranch = (git branch --show-current 2>&1)
    Write-Host "📍 현재 브랜치: $currentBranch"

    if ($currentBranch -ne "master") {
        Write-Host "⚠️  master 브랜치가 아님. master로 전환합니다."
        git checkout master
        $currentBranch = "master"
    }

    # ── 2. 빌드 ──────────────────────────────────────────
    Write-Host "`n📦 빌드 시작..."
    npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "빌드 실패! 배포 중단."
    }

    if (-not (Test-Path ".\out\index.html")) {
        throw "out/index.html 없음 — 빌드 출력 확인 필요"
    }
    Write-Host "✅ 빌드 완료 (out/ 폴더 생성됨)"

    # ── 3. 임시 worktree로 gh-pages 체크아웃 ─────────────
    $DEPLOY_TMP = Join-Path $env:TEMP "invest-sns-deploy-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Write-Host "`n🌿 gh-pages worktree 생성: $DEPLOY_TMP"

    git worktree add $DEPLOY_TMP gh-pages 2>&1
    if ($LASTEXITCODE -ne 0) {
        # gh-pages 브랜치가 없으면 생성
        git worktree add --orphan -b gh-pages $DEPLOY_TMP 2>&1
    }

    # ── 4. out/ 내용물을 worktree에 복사 ─────────────────
    Write-Host "`n📋 out/ → gh-pages worktree 복사..."

    Push-Location $DEPLOY_TMP
    try {
        # 기존 파일 삭제 (숨김 파일 제외 — .git은 유지)
        Get-ChildItem -Force | Where-Object { $_.Name -ne ".git" } | Remove-Item -Recurse -Force

        # out/ 내용 복사
        Copy-Item -Path "$PSScriptRoot\out\*" -Destination $DEPLOY_TMP -Recurse -Force

        # .nojekyll 보장
        if (-not (Test-Path ".nojekyll")) {
            New-Item ".nojekyll" -ItemType File | Out-Null
        }

        # ── 5. 커밋 & push ────────────────────────────────
        $commitMsg = "deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm') (auto)"
        Write-Host "`n🚀 커밋: $commitMsg"

        git add -A
        git commit -m $commitMsg
        git push origin gh-pages --force

        Write-Host "`n✅ GitHub Pages 배포 완료!"
        Write-Host "🌐 https://puing5555.github.io/invest-sns/"
    }
    finally {
        Pop-Location
    }

    # ── 6. worktree 제거 ──────────────────────────────────
    git worktree remove $DEPLOY_TMP --force
    Write-Host "🧹 임시 worktree 제거됨"

    # ── 7. 소스코드 브랜치 확인 ──────────────────────────
    $afterBranch = (git branch --show-current 2>&1)
    Write-Host "`n📍 배포 후 현재 브랜치: $afterBranch"
    if ($afterBranch -ne "master") {
        Write-Host "⚠️  master가 아님! 강제 전환합니다."
        git checkout master --force
    }

    Write-Host "`n🎉 배포 완료! 소스코드 브랜치(master) 유지됨."

}
catch {
    Write-Host "`n❌ 에러: $_"

    # 에러 발생 시 master로 복귀 보장
    Push-Location $PSScriptRoot
    $br = (git branch --show-current 2>&1)
    if ($br -ne "master") {
        Write-Host "🔧 master로 긴급 복귀..."
        git checkout master --force
    }
    Pop-Location

    exit 1
}
finally {
    Pop-Location
}
