#!/usr/bin/env python3
"""
빌드 → 검증 → 배포 통합 래퍼 스크립트
Usage:
  python scripts/deploy.py [--skip-build] [--skip-check] [--no-fix]
"""

import argparse
import subprocess
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run(cmd, cwd=None, shell=True):
    """Run a command and return (returncode, stdout)"""
    print(f"\n{'='*60}")
    print(f"▶ {cmd}")
    print('='*60)
    result = subprocess.run(
        cmd, cwd=cwd or PROJECT_ROOT, shell=shell,
        capture_output=False,  # show output in real-time
    )
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="빌드→검증→배포 통합 스크립트")
    parser.add_argument("--skip-build", action="store_true", help="빌드 스킵")
    parser.add_argument("--skip-check", action="store_true", help="검증 스킵")
    parser.add_argument("--no-fix", action="store_true", help="자동 수정 비활성화")
    args = parser.parse_args()

    print("🚀 배포 파이프라인 시작\n")

    # Step 1: Build
    if not args.skip_build:
        print("\n📦 Step 1/3: 빌드")
        rc = run("npx next build")
        if rc != 0:
            print("\n❌ 빌드 실패! 배포 중단.")
            sys.exit(1)
        print("✅ 빌드 완료")
    else:
        print("\n⏭️  Step 1/3: 빌드 스킵")

    # Step 2: Quality check
    if not args.skip_check:
        print("\n🔍 Step 2/3: 품질 검증")
        fix_flag = "" if args.no_fix else "--auto-fix"
        rc = run(f"python scripts/pre_deploy_check.py {fix_flag} --report")
        if rc != 0:
            print("\n❌ 품질 검증 실패! 수동 수정 필요. 배포 중단.")
            sys.exit(1)
        print("✅ 품질 검증 통과")
    else:
        print("\n⏭️  Step 2/3: 검증 스킵")

    # Step 3: Deploy
    print("\n🌐 Step 3/3: GitHub Pages 배포")
    rc = run("npx gh-pages -d out --dotfiles")
    if rc != 0:
        print("\n❌ 배포 실패!")
        sys.exit(1)

    print("\n" + "="*60)
    print("🎉 배포 완료!")
    print("="*60)


if __name__ == "__main__":
    main()
