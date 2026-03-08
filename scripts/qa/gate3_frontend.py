# -*- coding: utf-8 -*-
"""
QA Gate 3 - 프론트엔드 빌드/배포 검증
==============================
사용법:
  python scripts/qa/gate3_frontend.py --slug godofit

  # 배포 후 체크 포함 (GitHub Pages HTTP 200 확인)
  python scripts/qa/gate3_frontend.py --slug godofit --check-deploy

  # 프로젝트 루트 지정
  python scripts/qa/gate3_frontend.py --slug godofit --project-root C:/path/to/invest-sns

옵션:
  --slug          인플루언서 슬러그 (필수, 예: godofit)
  --check-deploy  배포 후 HTTP 200 체크 활성화 (기본: 비활성)
  --project-root  프로젝트 루트 경로 (기본: scripts/qa/../../)

출력:
  - 콘솔: 검증 결과 리포트 (한글)
  - 성공(exit 0): 모든 ⛔ 체크 통과
  - 실패(exit 1): data/qa/error_patterns.json에 에러 패턴 추가
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# .env.local 로드
def load_env(project_root):
    env_path = os.path.join(project_root, '.env.local')
    if os.path.exists(env_path):
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

QA_DIR_REL = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'qa')
ERROR_PATTERNS_FILE = os.path.join(QA_DIR_REL, 'error_patterns.json')

# API 키 유출 탐지 패턴
API_KEY_PATTERNS = [
    'sk-ant',
    'SUPABASE_SERVICE',
    'service_role',
]

# ────────────────────────────────────────
# 유틸
# ────────────────────────────────────────

def ensure_qa_dir():
    os.makedirs(os.path.dirname(ERROR_PATTERNS_FILE), exist_ok=True)

def load_error_patterns():
    if os.path.exists(ERROR_PATTERNS_FILE):
        with open(ERROR_PATTERNS_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []

def save_error_pattern(channel, gate, check_name, detail):
    ensure_qa_dir()
    patterns = load_error_patterns()
    patterns.append({
        "channel": channel,
        "gate": gate,
        "check_name": check_name,
        "detail": detail,
        "timestamp": datetime.now().isoformat()
    })
    with open(ERROR_PATTERNS_FILE, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)

# ────────────────────────────────────────
# 체크 함수
# ────────────────────────────────────────

def check_build_exists(out_dir):
    """체크 1: out/ 폴더 존재 여부 (빌드 완료 확인)"""
    return os.path.isdir(out_dir)

def check_profile_page(out_dir, slug):
    """체크 2: 프로필 페이지 존재 확인"""
    page_path = os.path.join(out_dir, 'profile', 'influencer', slug, 'index.html')
    return os.path.isfile(page_path), page_path

def check_api_key_leak(out_dir):
    """체크 3: out/ 폴더에 API 키 노출 탐지"""
    found = []
    out_path = Path(out_dir)
    for html_file in out_path.rglob('*.html'):
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            for pattern in API_KEY_PATTERNS:
                if pattern in content:
                    found.append({'file': str(html_file.relative_to(out_path)), 'pattern': pattern})
        except Exception:
            pass
    # JS 파일도 스캔
    for js_file in out_path.rglob('*.js'):
        try:
            content = js_file.read_text(encoding='utf-8', errors='ignore')
            for pattern in API_KEY_PATTERNS:
                if pattern in content:
                    found.append({'file': str(js_file.relative_to(out_path)), 'pattern': pattern})
        except Exception:
            pass
    return found

def check_required_pages(out_dir):
    """체크 4/5: 404.html + 주요 페이지 존재"""
    required = {
        '404.html': os.path.join(out_dir, '404.html'),
        'index.html': os.path.join(out_dir, 'index.html'),
        'dashboard/index.html': os.path.join(out_dir, 'dashboard', 'index.html'),
        'explore/index.html': os.path.join(out_dir, 'explore', 'index.html'),
    }
    missing = []
    for name, path in required.items():
        if not os.path.isfile(path):
            missing.append(name)
    return missing

def check_deploy_http(slug):
    """체크 6: GitHub Pages 배포 후 HTTP 200 확인"""
    url = f"https://puing5555.github.io/invest-sns/profile/influencer/{slug}/"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, url
    except urllib.error.HTTPError as e:
        return e.code, url
    except Exception as e:
        return None, url

# ────────────────────────────────────────
# 메인
# ────────────────────────────────────────

def run_gate3(slug, project_root, check_deploy=False):
    """Gate 3 실행. 반환: passed (bool)"""
    load_env(project_root)
    out_dir = os.path.join(project_root, 'out')

    print(f"\n{'='*60}")
    print(f"🔍 QA Gate 3 - 프론트엔드 빌드/배포 검증")
    print(f"   슬러그: {slug} | out 경로: {out_dir}")
    print(f"{'='*60}")

    has_fatal = False

    # ── 체크 1: 빌드 성공 (out/ 존재) ──
    if check_build_exists(out_dir):
        print(f"\n✅ [체크 1] 빌드 확인 — out/ 폴더 존재")
    else:
        print(f"\n⛔ [체크 1] 빌드 실패 — out/ 폴더 없음")
        print(f"   → 먼저 `npm run build`를 실행하세요")
        save_error_pattern(slug, 'gate3', 'build_missing', f"out/ 폴더 없음: {out_dir}")
        has_fatal = True

    # ── 체크 2: 프로필 페이지 존재 ──
    exists, page_path = check_profile_page(out_dir, slug)
    if exists:
        print(f"\n✅ [체크 2] 프로필 페이지 존재")
        print(f"   {page_path}")
    else:
        print(f"\n⛔ [체크 2] 프로필 페이지 없음")
        print(f"   찾는 경로: {page_path}")
        save_error_pattern(slug, 'gate3', 'profile_page_missing',
                           f"파일 없음: {page_path}")
        has_fatal = True

    # ── 체크 3: API 키 유출 스캔 ──
    print(f"\n🔎 [체크 3] API 키 유출 스캔 중...")
    if os.path.isdir(out_dir):
        leaks = check_api_key_leak(out_dir)
        if leaks:
            print(f"⛔ [체크 3] API 키 유출 감지 — {len(leaks)}건!")
            for leak in leaks[:10]:
                print(f"   ⚠️  {leak['file']}: '{leak['pattern']}' 패턴 발견")
            save_error_pattern(slug, 'gate3', 'api_key_leak',
                               f"{len(leaks)}건 유출: {[l['pattern'] for l in leaks[:3]]}")
            has_fatal = True
        else:
            print(f"✅ [체크 3] API 키 유출 없음")
    else:
        print(f"⚠️  [체크 3] out/ 폴더 없어 스킵")

    # ── 체크 4/5: 필수 페이지 존재 ──
    if os.path.isdir(out_dir):
        missing = check_required_pages(out_dir)
        if missing:
            print(f"\n⛔ [체크 4/5] 필수 페이지 누락 — {len(missing)}개")
            for m in missing:
                print(f"   - {m}")
            save_error_pattern(slug, 'gate3', 'required_pages_missing',
                               f"누락: {missing}")
            has_fatal = True
        else:
            print(f"\n✅ [체크 4/5] 필수 페이지 모두 존재 (404.html, index.html, dashboard, explore)")
    else:
        print(f"\n⚠️  [체크 4/5] out/ 폴더 없어 스킵")

    # ── 체크 6: 배포 후 HTTP 체크 ──
    if check_deploy:
        print(f"\n🌐 [체크 6] GitHub Pages 배포 확인 중...")
        status, url = check_deploy_http(slug)
        if status == 200:
            print(f"✅ [체크 6] HTTP 200 확인")
            print(f"   {url}")
        elif status is None:
            print(f"⚠️  [체크 6] 연결 실패 (타임아웃 또는 DNS 오류)")
            print(f"   URL: {url}")
        else:
            print(f"⚠️  [체크 6] HTTP {status} 응답")
            print(f"   URL: {url}")
            save_error_pattern(slug, 'gate3', 'deploy_http_check',
                               f"HTTP {status}: {url}")
    else:
        print(f"\nℹ️  [체크 6] 배포 후 HTTP 체크 스킵 (--check-deploy 옵션으로 활성화)")

    # ── 결과 ──
    print(f"\n{'='*60}")
    if has_fatal:
        print(f"❌ Gate 3 실패 — 배포 차단. 치명적 오류 해결 후 재시도.")
        print(f"{'='*60}\n")
        return False
    else:
        print(f"✅ Gate 3 통과 — 프론트엔드 검증 완료. 배포 승인.")
        print(f"{'='*60}\n")
        return True


def main():
    parser = argparse.ArgumentParser(description='QA Gate 3 - 프론트엔드 빌드/배포 검증')
    parser.add_argument('--slug', '-s', required=True, help='인플루언서 슬러그 (예: godofit)')
    parser.add_argument('--check-deploy', action='store_true',
                        help='GitHub Pages 배포 후 HTTP 200 체크 활성화')
    parser.add_argument('--project-root', '-r',
                        default=os.path.join(os.path.dirname(__file__), '..', '..'),
                        help='프로젝트 루트 경로 (기본: scripts/qa/../../)')
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    passed = run_gate3(args.slug, project_root, args.check_deploy)
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
