# 프론트엔드 규칙 & 컨벤션

## 기술 스택
- Next.js 14 (App Router, `output: 'export'` 정적 빌드)
- Tailwind CSS (유틸리티 퍼스트, CSS 모듈 사용 안 함)
- Recharts (차트)
- Supabase Auth (`context/AuthContext.tsx`)

## next.config.js 핵심
```js
output: 'export'           // GitHub Pages 정적 빌드
basePath: '/invest-sns'    // 서브패스 배포
trailingSlash: true         // /page/ 형식
images: { unoptimized: true } // 정적 빌드 호환
```

## 레이아웃 구조
```
RootLayout (app/layout.tsx)
  └─ MainLayout ('use client')
      ├─ Sidebar (md 이상 표시, 고정)
      ├─ main (flex-1)
      │   └─ {children}
      ├─ RightSidebar (xl 이상, 홈 페이지만)
      └─ BottomNav (md 미만, 모바일 탭바)
```
- 로그인/회원가입 페이지: Sidebar/BottomNav 숨김

## 페이지 패턴
- 서버 컴포넌트 기본, 인터랙티브 부분만 `'use client'`
- 동적 라우트: `generateStaticParams()`로 정적 생성
- 코드 분리: `page.tsx` → `*Client.tsx` 위임 패턴
- 데이터: `data/*.json` 정적 import (API 호출 아님)

## 컴포넌트 컨벤션

### 네이밍
- PascalCase: `SignalCard.tsx`, `ReportDetailModal.tsx`
- 기능별 하위 디렉터리: `components/disclosure/`, `components/stock/`

### 패턴
| 유형 | 예시 | 특징 |
|------|------|------|
| Card | `SignalCard`, `ReportCard` | onClick 핸들러, 데이터 표시 |
| Modal | `ReportDetailModal`, `SignalDetailModal` | `isOpen` + `onClose` props |
| Badge | `SignalTag`, `SentimentBadge` | 작은 표시 컴포넌트 |
| Layout | `MainLayout`, `Sidebar`, `BottomNav` | 영구 네비게이션 |

### 상태 관리
- Context API: Auth만 (`useAuth()`)
- 로컬 state: 모달, 탭, 필터 (`useState`)

## Tailwind 스타일 규칙

### 색상
| 용도 | 값 |
|------|---|
| 배경 | `#f4f4f4` |
| 텍스트 (주) | `#191f28` |
| 텍스트 (보조) | `#8b95a1` |
| 테두리 | `#e8e8e8` |
| 액센트 (파랑) | `#3182f6` |
| 긍정 (초록) | `#22c55e` |
| 부정 (빨강) | `#ef4444` |

### 시그널 배지 색상
| 시그널 | 클래스 |
|--------|--------|
| 매수 | `bg-green-600 text-white` |
| 긍정 | `bg-blue-600 text-white` |
| 중립 | `bg-gray-500 text-white` |
| 부정 | `bg-yellow-600 text-white` |
| 매도 | `bg-red-800 text-white` |

### 공통 패턴
```
카드:        rounded-xl shadow-sm hover:shadow-md transition-shadow
패딩:        px-4 py-3
간격:        space-y-2, gap-3
배지 (pill):  rounded-full px-3 py-1 text-xs font-medium
호버:        hover:bg-[#f2f4f6] transition-colors cursor-pointer
왼쪽 보더:    border-l-4 border-[색상]
```

### 반응형 브레이크포인트
- 모바일 퍼스트: `md:` (태블릿+), `lg:` (데스크톱), `xl:` (와이드)
- 패턴: `hidden md:flex` (모바일 숨김), `lg:hidden xl:block`

### 타이포그래피
- 페이지 제목: `font-bold text-xl`
- 카드 제목: `font-bold text-lg text-gray-900`
- 메타 텍스트: `text-xs text-gray-400` / `text-sm text-gray-600`
- 기본 폰트: 시스템 폰트 + Pretendard

## 빌드 & 확인
```bash
npm run build    # out/ 폴더 생성
npm run dev      # localhost:3000 로컬 확인
```
- **빌드 실패 = 배포 금지** (CLAUDE.md Rules #8)
- `out/` 폴더가 배포 대상 (gh-pages branch)

## 주요 라이브러리 버전
- next: 14.2.35
- react: 18
- recharts: 3.7.0
- @supabase/supabase-js: 2.97.0
