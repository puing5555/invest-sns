#!/usr/bin/env pwsh
<#
.SYNOPSIS
  invest-sns 안전 배포 스크립트 v3 (orphan 방식)
  매번 히스토리 없는 깨끗한 커밋 1개만 push → 대용량 파일 히스토리 문제 원천 차단

.USAGE
  cd invest-sns
  .\deploy.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot

try {
    # 1. 현재 브랜치 확인
    $currentBranch = (git branch --show-current 2>&1)
    Write-Host "[1] 현재 브랜치: $currentBranch"

    # 2. 빌드
    Write-Host "`n[2] 빌드 시작..."
    npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "빌드 실패"
    }
    if (-not (Test-Path ".\out\index.html")) {
        throw "out/index.html 없음"
    }
    $htmlCount = (Get-ChildItem -Path out -Filter *.html -Recurse).Count
    Write-Host "[OK] 빌드 완료 (HTML ${htmlCount}개)"

    # 3. remote URL 가져오기
    $remoteUrl = (git remote get-url origin 2>&1).Trim()

    # 4. 임시 디렉토리에 orphan git 생성
    $DEPLOY_TMP = Join-Path $env:TEMP "invest-sns-deploy-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Write-Host "`n[3] orphan 배포 준비: $DEPLOY_TMP"
    New-Item $DEPLOY_TMP -ItemType Directory -Force | Out-Null

    Push-Location $DEPLOY_TMP
    try {
        git init
        git checkout --orphan gh-pages

        # out/ 복사
        Copy-Item -Path "$PSScriptRoot\out\*" -Destination . -Recurse -Force

        # .nojekyll 보장
        if (-not (Test-Path ".nojekyll")) {
            New-Item ".nojekyll" -ItemType File | Out-Null
        }

        # commit + push
        $commitMsg = "deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm') (auto)"
        git add -A
        git commit -m $commitMsg
        git remote add origin $remoteUrl
        git push origin gh-pages --force

        Write-Host "`n[OK] GitHub Pages 배포 완료!"
        Write-Host "    https://puing5555.github.io/invest-sns/"
    }
    finally {
        Pop-Location
    }

    # 5. 정리
    Remove-Item $DEPLOY_TMP -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] 임시 폴더 정리됨"
}
catch {
    Write-Host "`n[ERROR] $_"
    exit 1
}
finally {
    Pop-Location
}
