# Supabase DB 스키마 & 인프라

## 접속 정보
- URL: `.env.local`의 `NEXT_PUBLIC_SUPABASE_URL`
- Anon Key: `lib/supabase.ts`에 임베디드 (공개용)
- Service Key: `.env.local`의 `SUPABASE_SERVICE_ROLE_KEY` (서버 전용)

## 핵심 테이블

### 인플루언서 시그널 시스템

**speakers**
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| name | TEXT UNIQUE | |
| aliases | TEXT[] | GIN 인덱스 |
| profile_image_url | TEXT | |
| bio | TEXT | |

**influencer_channels**
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| channel_name | TEXT | 실제 채널명 |
| channel_handle | TEXT | @xxx |
| channel_url | TEXT | |
| platform | TEXT | default 'youtube' |
| subscriber_count | INT | |

**influencer_videos**
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| channel_id | UUID FK | → influencer_channels |
| video_id | TEXT UNIQUE | YouTube ID |
| title | TEXT | |
| published_at | TIMESTAMPTZ | ⚠️ 업로드 날짜 (크롤링 날짜 X) |
| duration_seconds | INT | |
| has_subtitle | BOOLEAN | |
| pipeline_version | TEXT | |
| signal_count | INT | |

**influencer_signals**
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| video_id | UUID FK | → influencer_videos |
| speaker_id | UUID FK | → speakers |
| stock | TEXT NOT NULL | 한글 종목명 |
| ticker | TEXT | KR=6자리, US=영문 |
| market | TEXT | KR, US, CRYPTO, INDEX, ETF, OTHER |
| signal | TEXT | 매수/긍정/중립/부정/매도 (**경계 사용금지**) |
| confidence | TEXT | very_high ~ very_low |
| timestamp | TEXT | MM:SS |
| key_quote | TEXT | 20~200자 |
| reasoning | TEXT | 50자+ |
| review_status | TEXT | pending/approved/rejected/modified |
| pipeline_version | TEXT | |
| price_at_signal | NUMERIC | 발언일 종가 |
| price_current | NUMERIC | |
| return_pct | NUMERIC | |

### 애널리스트 리포트 시스템

**analyst_reports** (DB 테이블 — JSON과 별도)
| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | UUID PK | |
| ticker | TEXT | KRX 6자리 |
| analyst_name | TEXT | |
| firm | TEXT | 증권사 |
| title | TEXT | |
| target_price | INTEGER | |
| opinion | TEXT | BUY/HOLD/SELL |
| published_at | DATE | |
| pdf_url | TEXT | |
| summary, ai_summary | TEXT | |

**analysts** — 애널리스트 프로필 (accuracy_rate, total_reports, avg_return 등)
**analyst_signals** — 리포트별 시그널 (stock_code, signal_type, target_price, time_horizon)
**analyst_performance** — 성과 추적 (entry_price, exit_price, return_rate, hit_target)

### 사용자 시스템

**user_profiles** — auth.users 연동 (display_name, avatar_url, dashboard_preferences)
**user_stocks** — 포트폴리오 (stock_code, quantity, avg_buy_price, UNIQUE(user_id, stock_code))
**user_watchlist** — 관심종목 (alert_on_signals, alert_price_target)
**user_notifications** — 알림 (type: signal/price_target/analyst_report/...)
**user_notification_settings** — 알림 설정 (portfolio_alerts, watchlist_alerts 등)

### 기타

**disclosures** — DART 공시 (dart_id, corp_name, grade, sentiment, ai_one_liner)
**signal_reports** — 시그널 신고 (reason, ai_review, ai_suggestion)
**signal_votes** — 투표 (vote_type, memo)
**crawl_logs** — 크롤링 이력

## RPC 함수

| 함수 | 용도 |
|------|------|
| `update_updated_at_column()` | TRIGGER — updated_at 자동 갱신 |
| `create_user_profile()` | auth.users INSERT 시 자동 프로필 생성 |
| `create_user_notification()` | 알림 생성 (설정 검증 포함) |
| `check_user_stock_duplicates()` | 포트폴리오 중복 체크 |
| `check_user_watchlist_duplicates()` | 관심종목 중복 체크 |

## Edge Functions (`supabase/functions/`)

| 함수 | 용도 |
|------|------|
| `ai-review` | 시그널 신고 AI 리뷰 (Claude API) |
| `anthropic-proxy` | Claude API 프록시 |
| `dart-crawler` | DART 공시 크롤러 |

## Views

**user_personalized_signals** — 포트폴리오+관심종목 매칭 시그널 (approved만)

## 스키마 파일 위치
- `supabase/influencer-complete-migration-v3.sql` — 인플루언서 시스템 전체
- `analyst-schema.sql` — 애널리스트 시스템
- `supabase/migrations/` — 마이그레이션 이력
- `types/supabase.ts` — TypeScript 타입
