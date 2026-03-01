# 자동화 파이프라인 스크립트

투자 유튜버 채널을 자동으로 분석하여 시그널을 추출하는 파이프라인입니다.

## 구조

### 메인 스크립트
- `auto_pipeline.py` - 전체 파이프라인 실행

### 모듈
- `pipeline_config.py` - 설정 파일 (API키, 프록시, 레이트리밋 등)
- `title_filter.py` - 제목 기반 영상 필터링
- `subtitle_extractor.py` - 자막 추출 (youtube_transcript_api + yt-dlp)
- `signal_analyzer.py` - AI 시그널 분석 (Anthropic Claude)
- `db_inserter.py` - Supabase DB INSERT

## 설치

```bash
# 의존성 설치
pip install -r scripts/requirements.txt

# 환경변수 설정 (.env.local에 이미 설정됨)
# ANTHROPIC_API_KEY
# WEBSHARE_PROXY_URL (선택사항)
# SUPABASE 관련 설정들
```

## 사용법

### 1. Dry Run (추천)
```bash
# 영상 목록과 필터링 결과만 확인
python scripts/auto_pipeline.py --channel https://www.youtube.com/@sesang101 --dry-run
```

### 2. 실제 실행
```bash
# 전체 파이프라인 실행
python scripts/auto_pipeline.py --channel https://www.youtube.com/@sesang101 --execute

# 최대 10개 영상만 처리
python scripts/auto_pipeline.py --channel https://www.youtube.com/@sesang101 --execute --limit 10

# DB에 이미 있는 영상 건너뛰기
python scripts/auto_pipeline.py --channel https://www.youtube.com/@sesang101 --execute --skip-existing
```

## 파이프라인 단계

1. **채널 영상 목록 수집** (yt-dlp)
   - 채널의 최신 영상들 메타데이터 수집
   - 제목, URL, 길이, 업로드일, 조회수 등

2. **제목 필터링**
   - Skip: 구독자 Q&A, 일상/브이로그, 채널 공지, 교육/자기계발, 영어, 인트로/쇼츠, 멤버십
   - Pass: 특정 종목 언급, 시장/섹터 전망, 매매 의견

3. **자막 추출** (Webshare 프록시)
   - youtube_transcript_api 우선 시도
   - 실패 시 yt-dlp --write-sub 사용
   - 레이트리밋: 요청 간 3초, 429시 60초, 20개 후 5분 휴식

4. **시그널 분석** (Anthropic Claude)
   - 모델: claude-sonnet-4-20250514
   - 프롬프트: V10 (pipeline_v10.md)
   - 배치: 1영상씩, 요청 간 5초

5. **DB INSERT**
   - influencer_channels 확인/생성
   - influencer_videos INSERT
   - speakers 확인/생성
   - influencer_signals INSERT

6. **가격 업데이트 준비**
   - signal_prices.json 업데이트용 종목 목록 생성
   - yfinance 스크립트 별도 실행 필요

## 시그널 타입 (한글 5단계)
- 매수: "사라, 담아라, 들어가라, 비중 확대"
- 긍정: "좋아보인다, 괜찮다, 관심가져라"
- 중립: "지켜보자, 모르겠다" 또는 뉴스/리포트/교육
- 경계: "조심해라, 리스크 있다, 주의"
- 매도: "팔아라, 손절해라, 빠져라"

## 레이트리밋 설정

### 자막 추출
- 요청 간 3초 대기
- 429 에러 시 60초 대기
- 20개 처리 후 5분 휴식

### AI 분석
- API 요청 간 5초 대기

## 첫 번째 대상 채널

**세상의 모든 지식 (세모지)**
- URL: https://www.youtube.com/@sesang101
- 특징: 경제/투자 전문 채널
- 예상 통과율: 약 60-70%

## 주의사항

1. **Webshare 프록시 필수** - 자막 추출 시 IP 차단 방지
2. **Anthropic API 사용량** - 영상 1개당 약 3,000-5,000 토큰
3. **실행 시간** - 영상 50개 기준 약 2-3시간 소요
4. **백업 파일** - 분석 결과를 중간 백업으로 저장 (`scripts/pipeline_backup_*.json`)

## 문제 해결

### yt-dlp 에러
- Windows에서 PATH 설정 확인
- `pip install --upgrade yt-dlp`

### 프록시 에러
- WEBSHARE_PROXY_URL 형식: `http://username:password@proxy:port`
- 프록시 연결 상태 확인

### DB 에러
- Supabase 서비스키 권한 확인
- 네트워크 연결 상태 확인