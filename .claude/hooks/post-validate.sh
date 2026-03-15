#!/bin/bash
# PostToolUse hook: 파일 수정 후 검증

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('file_path', ''))
except:
    print('')
" 2>/dev/null)

[ -z "$FILE_PATH" ] && exit 0

# 경로를 forward slash로 통일
FILE_PATH_UNIX=$(echo "$FILE_PATH" | tr '\\' '/')

# .py 파일 → 구문 검증 (빠름, <1초)
case "$FILE_PATH_UNIX" in
  *.py)
    if python -m py_compile "$FILE_PATH" 2>&1; then
      echo "py-check: OK"
    else
      echo "py-check: SYNTAX ERROR in $FILE_PATH" >&2
      exit 2
    fi
    exit 0
    ;;
esac

# .ts/.tsx 파일 → 안내만 (tsc --noEmit은 10~30초 소요)
case "$FILE_PATH_UNIX" in
  *.ts | *.tsx)
    echo "ts-remind: TypeScript 수정됨 — 완료 후 npm run build 로 타입 체크 권장"
    exit 0
    ;;
esac

# app/ 또는 components/ 변경 → 빌드 안내
case "$FILE_PATH_UNIX" in
  */app/* | */components/*)
    echo "build-remind: 프론트엔드 변경 — 완료 후 npm run build 필수"
    exit 0
    ;;
esac

exit 0
