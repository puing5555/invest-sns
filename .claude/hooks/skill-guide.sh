#!/bin/bash
# PreToolUse hook: 파일 경로 기반 관련 skill 자동 안내

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

# 경로를 forward slash로 통일 (Windows 호환)
FILE_PATH=$(echo "$FILE_PATH" | tr '\\' '/')

case "$FILE_PATH" in
  */components/* | */app/*)
    echo "skill-hint: frontend.md (UI 컨벤션, Tailwind, 레이아웃)"
    ;;
  */scripts/crawl* | */scripts/calc_analyst*)
    echo "skill-hint: crawling.md (크롤러, yfinance, 프록시)"
    ;;
  */prompts/*)
    echo "skill-hint: prompt.md (시그널 규칙, 수정 절차)"
    ;;
  */supabase/*)
    echo "skill-hint: supabase.md (DB 스키마, RPC, Edge Function)"
    ;;
  */data/eval* | */scripts/eval*)
    echo "skill-hint: eval.md (정답지, 3그룹 분석법)"
    ;;
esac

exit 0
