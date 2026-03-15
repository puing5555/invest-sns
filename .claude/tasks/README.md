# 작업 기억 시스템

## 사용법

큰 작업(새 기능, 시스템 변경, 크롤링 확장 등) 시작 시:

1. `_templates/`에서 3개 파일 복사하여 작업별 폴더 생성
2. `plan.md` 작성 → **승인 후 실행**
3. 1~2단계 단위로 진행, 단계 완료 시 `checklist.md` 업데이트
4. 의사결정 발생 시 `context.md`에 기록

## 폴더 구조

```
.claude/tasks/
├── _templates/              ← 복사용 템플릿
│   ├── plan-template.md
│   ├── context-template.md
│   └── checklist-template.md
├── <작업명>/                 ← 작업별 폴더
│   ├── plan.md
│   ├── context.md
│   └── checklist.md
```

## 작업 폴더 네이밍
- 소문자 + 하이픈: `v15-prompt`, `new-channel-syuka`, `tab-restructure`
- 완료 후: 폴더 유지 (히스토리 참조용)

## 규칙
- 계획 승인 전 실행 금지 (CLAUDE.md Rules #10)
- 1~2단계 단위 진행 + checklist 업데이트 (Rules #11)
- QA Gate 실패 시 다음 단계 금지 (Rules #4)
