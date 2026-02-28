# Supabase 인플루언서 DB 마이그레이션 가이드

_작성일: 2026-02-27 14:50_

## 📋 작업 완료 상황

### ✅ 완료된 작업
1. **테이블 DDL 작성** - `influencer-migration.sql`
2. **3protv 시그널 데이터 변환** - `3protv_signals_insert.sql`
3. **데이터 변환 스크립트** - `convert_signals_to_supabase.py`

### 📊 데이터 현황  
- **삼프로TV V7**: 20개 (승인된 시그널)
- **코린이아빠 V5**: 11개 (승인된 시그널)
- **총 시그널 수**: 31개 (실제 사용 가능한 데이터)

## 🗂️ 파일 구조

```
invest-sns/supabase/
├── influencer-migration.sql          # 테이블 생성 DDL
├── 3protv_signals_insert.sql          # 3protv 데이터 INSERT
├── convert_signals_to_supabase.py     # 데이터 변환 스크립트
├── check_tables.py                    # 테이블 존재 확인
├── insert_data.py                     # 테스트 데이터 삽입
├── list_tables.py                     # 기존 테이블 목록 확인
├── insert_to_existing_tables.py       # 기존 테이블 활용
└── README_MIGRATION.md               # 이 문서
```

## 🏗️ 테이블 구조

### 1. influencer_channels
- **목적**: 인플루언서의 채널 정보
- **주요 컬럼**: channel_name, channel_url, platform, subscriber_count
- **외래키**: influencer_id → influencers(id)

### 2. influencer_videos  
- **목적**: 분석된 비디오 정보
- **주요 컬럼**: video_id, title, published_at, duration_seconds, has_subtitle
- **외래키**: channel_id → influencer_channels(id)

### 3. influencer_signals
- **목적**: 추출된 투자 시그널
- **주요 컬럼**: speaker, stock, ticker, market, signal, confidence, key_quote
- **외래키**: video_id → influencer_videos(id)
- **시그널 타입**: STRONG_BUY, BUY, POSITIVE, HOLD, NEUTRAL, CONCERN, SELL, STRONG_SELL

## 🚀 실행 방법

### 방법 1: Supabase 대시보드 (권장)
1. Supabase 프로젝트 대시보드 접속
2. **SQL Editor** 메뉴 이동
3. `influencer-migration.sql` 내용 복사/붙여넣기 → 실행 (테이블 생성)
4. `3protv_signals_insert.sql` 내용 복사/붙여넣기 → 실행 (데이터 삽입)

### 방법 2: 추가 데이터 변환
```bash
# 추가 시그널 데이터가 있을 경우
cd invest-sns/supabase
python convert_signals_to_supabase.py
```

## ⚠️ 제약사항 및 이슈

### API 키 권한
- **anon key**: 읽기 전용, INSERT 권한 없음 (401 에러)
- **service role key**: 필요시 관리자 권한으로 직접 삽입 가능

### 현재 데이터 상태
- **승인된 시그널만 사용**: 총 31개 (삼프로TV 20개 + 코린이아빠 11개)
- **실제 비디오 메타데이터**: 현재는 Mock 데이터 사용

### 테이블 관계
- **기존 테이블**: influencers, posts, profiles 등이 이미 존재
- **신규 테이블**: influencer_channels, influencer_videos, influencer_signals
- **연동 방식**: 기존 influencers 테이블과 연결 또는 독립 운영

## 📈 다음 단계

### 단기 (이번 주)
1. **SQL 파일 실행**: Supabase 대시보드에서 테이블 생성 및 데이터 삽입
2. **승인된 데이터만 사용**: 총 31개 시그널 (삼프로TV 20개 + 코린이아빠 11개)
3. **데이터 검증**: 삽입된 데이터 정합성 확인

### 중기 (다음 주)
1. **REST API 연동**: Next.js 앱에서 새 테이블 읽기
2. **UI 업데이트**: 인플루언서 탭에서 실제 DB 데이터 표시
3. **검색/필터링**: 시그널 타입별, 종목별, 인플루언서별 필터

### 장기 (월말)
1. **실시간 동기화**: 새 시그널 분석 결과 자동 DB 삽입
2. **성과 추적**: 시그널 정확도, 수익률 계산
3. **알림 시스템**: 새 시그널 발생 시 텔레그램 알림

## 🔧 문제 해결

### 테이블이 없다는 오류
```sql
-- 테이블 존재 확인
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name LIKE 'influencer_%';
```

### 데이터 타입 오류
- **UUID**: PostgreSQL uuid_generate_v4() 함수 사용
- **TIMESTAMPTZ**: ISO 8601 형식으로 변환
- **TEXT**: 따옴표 이스케이프 처리

### 외래키 제약
- **influencer_id**: 기존 influencers 테이블 참조 또는 임시 UUID
- **순서**: channels → videos → signals 순으로 삽입

---

**작성자**: OpenClaw Agent  
**연락처**: 텔레그램 그룹 -1003764256213  
**업데이트**: 2026-02-27 14:50 KST