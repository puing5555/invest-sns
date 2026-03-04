# 한국어 투자 아이디어 수집 시스템 - 기술 스펙 문서

## 프로젝트 개요

### 목표
한국 웹 전체에서 "근거 있는 투자 아이디어"를 자동 수집하는 시스템 구축

### 투자 아이디어 정의
- **필수 요소:**
  - 특정 종목 언급 (주식코드 또는 종목명)
  - 명확한 긍정/부정 의견 존재
  - 근거 있음 (실적, 밸류에이션, 산업 전망, 차트 분석 등)
  - 최소 3문장 이상의 분석 내용

- **제외 대상:**
  - 1줄 추천 ("삼성전자 매수하세요")
  - 단순 뉴스 공유/링크
  - 광고/스팸 성격 게시물
  - 근거 없는 감정적 의견

## 데이터 소스 분석

### 1. 유튜브 (YouTube)

**크롤링 가능 여부:** ✅ 기존 파이프라인 활용 가능
- **방법:** yt-dlp + 자막 추출
- **기존 인프라:** 이미 구축된 영상 크롤링 시스템 존재

**API 제한사항:**
- YouTube Data API v3: 일일 할당량 10,000 쿼터 (무료)
- yt-dlp: API 제한 없음 (직접 추출)
- 자막 추출: 한국어 자막 가능

**데이터 구조:**
```json
{
  "video_id": "string",
  "title": "string", 
  "channel": "string",
  "upload_date": "datetime",
  "transcript": "string",
  "view_count": "number",
  "like_count": "number"
}
```

**품질/볼륨:**
- 하루 신규 투자 영상: 약 50-100개 추정
- 투자 아이디어 비율: 30-40% (실제 분석 포함)
- 품질: 높음 (긴 형태 컨텐츠, 상세 분석)

**법적 리스크:** 낮음
- 공개 영상, 자막 추출
- Fair use 원칙 적용 가능

**구현 난이도:** 쉬움 (기존 시스템 활용)

### 2. 네이버 카페 (Naver Cafe)

**크롤링 가능 여부:** ⚠️ 제한적
- **문제점:** 로그인 필요, 카페별 가입 승인
- **방법:** 웹 스크래핑 (Selenium/Playwright)

**API 제한사항:**
- 공식 카페 API 없음
- 네이버 검색 API: 카페 게시글 제한적 노출
- 스크래핑 시 IP 차단 위험
- Rate limiting 필요

**데이터 구조:**
```json
{
  "cafe_name": "string",
  "post_id": "string",
  "title": "string",
  "content": "string",
  "author": "string", 
  "post_date": "datetime",
  "view_count": "number",
  "comment_count": "number"
}
```

**주요 타겟 카페:**
- 종토넷 (주식토론네트워크)
- 팍스넷 카페
- 인베스트맘 카페
- 각종 주식 동호회 카페

**품질/볼륨:**
- 하루 게시글: 300-500개 (주요 카페 합산)
- 투자 아이디어 비율: 20-30%
- 품질: 중상 (커뮤니티 검증 효과)

**법적 리스크:** 중간
- 카페 이용약관 확인 필요
- 개인정보 노출 주의
- 저작권 이슈 가능

**구현 난이도:** 어려움

### 3. 네이버 블로그 (Naver Blog)

**크롤링 가능 여부:** ✅ 가능
- **방법:** 네이버 검색 API + RSS 피드

**API 제한사항:**
- 네이버 검색 API: 일일 25,000건 호출
- 블로그 검색 쿼리: 종목명 기반
- RSS 피드: 개별 블로그별 제공

**데이터 구조:**
```json
{
  "blog_id": "string",
  "post_id": "string", 
  "title": "string",
  "content": "string",
  "author": "string",
  "post_date": "datetime",
  "blog_url": "string"
}
```

**검색 전략:**
- 종목명 + "분석", "전망", "투자" 키워드 조합
- 주요 주식 블로거 RSS 구독
- 최신 게시글 우선 수집

**품질/볼륨:**
- 하루 관련 포스트: 200-400개
- 투자 아이디어 비율: 40-50%
- 품질: 중상 (개인 블로거의 심도 있는 분석)

**법적 리스크:** 낮음
- 공개 블로그, 검색 API 이용
- 출처 명시 시 문제없음

**구현 난이도:** 보통

### 4. 트위터/X (Twitter/X)

**크롤링 가능 여부:** ✅ API 이용 가능
- **방법:** X API v2

**API 제한사항:**
- **무료 티어:** 월 10,000건 트윗 읽기
- **Basic 티어 ($100/월):** 월 50,000건
- **Pro 티어 ($5,000/월):** 월 300만건
- 실시간 스트림 API 제공

**데이터 구조:**
```json
{
  "tweet_id": "string",
  "text": "string",
  "author_id": "string", 
  "author_username": "string",
  "created_at": "datetime",
  "public_metrics": "object",
  "lang": "string"
}
```

**수집 전략:**
- 한국 주요 주식 계정 팔로우
- 종목명/주식코드 키워드 검색
- 해시태그 활용 (#삼성전자, #투자분석)

**품질/볼륨:**
- 하루 관련 트윗: 500-1,000개
- 투자 아이디어 비율: 15-25%
- 품질: 중하 (짧은 형태, 근거 부족 많음)

**법적 리스크:** 낮음
- 공개 트윗, 공식 API 이용

**구현 난이도:** 보통 (API 비용 고려)

### 5. 디시인사이드 / 에펨코리아

**크롤링 가능 여부:** ⚠️ 스크래핑만 가능
- **방법:** 웹 스크래핑 (requests + BeautifulSoup)

**API 제한사항:**
- 공식 API 없음
- robots.txt 확인 필요
- IP 차단 위험 (Rate limiting 필수)
- User-Agent 로테이션 필요

**타겟 갤러리:**
- 주식 갤러리
- 투자 갤러리  
- 삼성전자 갤러리
- 기타 종목별 갤러리

**데이터 구조:**
```json
{
  "gallery_name": "string",
  "post_id": "string",
  "title": "string", 
  "content": "string",
  "author": "string",
  "post_date": "datetime",
  "view_count": "number",
  "comment_count": "number"
}
```

**품질/볼륨:**
- 하루 게시글: 1,000-2,000개
- 투자 아이디어 비율: 10-20%
- 품질: 중하 (익명성, 신뢰도 낮음)

**법적 리스크:** 중간
- 웹 스크래핑 TOS 위반 가능성
- 익명 게시판 특성

**구현 난이도:** 어려움

### 6. 텔레그램 (Telegram)

**크롤링 가능 여부:** ✅ API 이용 가능
- **방법:** Telethon/Pyrogram 라이브러리

**API 제한사항:**
- Telegram Bot API: 무료, 제한 거의 없음
- 공개 채널만 접근 가능
- 실시간 메시지 수신 가능

**주요 투자 채널:**
- 주식 정보 공유 채널
- 투자 분석 채널
- 종목 추천 채널

**데이터 구조:**
```json
{
  "channel_name": "string",
  "message_id": "number",
  "text": "string",
  "author": "string",
  "date": "datetime", 
  "views": "number",
  "forwards": "number"
}
```

**품질/볼륨:**
- 하루 메시지: 100-300개 (주요 채널 합산)
- 투자 아이디어 비율: 25-35%
- 품질: 중간 (채널별 편차 큼)

**법적 리스크:** 낮음
- 공개 채널, 공식 API 이용

**구현 난이도:** 쉬움

### 7. 구글 검색 (Google Search)

**크롤링 가능 여부:** ✅ API 이용 가능
- **방법:** Google Custom Search API

**API 제한사항:**
- 무료: 일일 100건
- 유료: $5/1,000건 추가
- SerpAPI 대안: $50/월 (5,000건)

**검색 전략:**
- "종목명 + 투자 + 분석 + site:blog.naver.com"
- "주식 분석 + 종목명 + 2024"
- 투자 관련 사이트 특정 검색

**데이터 구조:**
```json
{
  "query": "string",
  "title": "string",
  "snippet": "string", 
  "url": "string",
  "display_url": "string",
  "search_date": "datetime"
}
```

**품질/볼륨:**
- 하루 검색 결과: 제한적 (API 한도)
- 투자 아이디어 비율: 60-70%
- 품질: 높음 (검색 결과 필터링)

**법적 리스크:** 낮음
- 공식 API, 공개 정보

**구현 난이도:** 쉬움 (API 비용 고려)

## 시스템 아키텍처

### 전체 파이프라인

```
[소스별 크롤러] → [원문 수집] → [1차 필터] → [2차 필터] → [시그널 추출] → [DB 저장]
     ↓              ↓            ↓          ↓            ↓            ↓
  Python Scripts  Raw Text    Rule-based  AI Filter   AI Extract   Supabase
  (각 소스별)     MongoDB     Filtering   (Haiku)     (Sonnet)     PostgreSQL
```

### 상세 단계별 설계

#### 1. 수집 단계 (Collection)
```python
# 소스별 크롤러 구조
class BaseCrawler:
    def fetch_posts(self) -> List[RawPost]:
        pass
    
    def parse_content(self, raw_data) -> Post:
        pass
        
    def save_raw(self, posts: List[Post]):
        # MongoDB에 원문 저장
        pass

class YoutubeCrawler(BaseCrawler):
    # 기존 파이프라인 연동
    
class NaverCafeCrawler(BaseCrawler):
    # Selenium/Playwright
    
class TwitterCrawler(BaseCrawler):
    # X API v2
```

#### 2. 1차 필터링 (Rule-based)
```python
def rule_based_filter(post: Post) -> bool:
    # 길이 체크 (최소 100자)
    if len(post.content) < 100:
        return False
        
    # 종목명/주식코드 포함 여부
    if not contains_stock_symbol(post.content):
        return False
        
    # 스팸/광고 키워드 제외
    if is_spam_content(post.content):
        return False
        
    return True
```

#### 3. 2차 필터링 (AI)
```python
async def ai_filter_investment_idea(content: str) -> bool:
    prompt = f"""
    다음 글이 '근거 있는 투자 아이디어'인지 판단해주세요.
    
    기준:
    - 특정 종목에 대한 긍정/부정 의견 있음
    - 실적, 밸류에이션, 산업전망 등 구체적 근거 있음  
    - 3문장 이상의 분석 내용
    
    글: {content}
    
    답변: YES/NO
    """
    
    response = await haiku_api.complete(prompt)
    return response.strip() == "YES"
```

#### 4. 시그널 추출 (AI)
```python
async def extract_investment_signal(content: str) -> InvestmentSignal:
    prompt = f"""
    투자 아이디어에서 다음 정보를 추출해주세요:
    
    1. 종목명/종목코드
    2. 투자 의견 (STRONG_BUY/BUY/POSITIVE/HOLD/NEUTRAL/CONCERN/SELL/STRONG_SELL)
    3. 핵심 근거 (3줄 요약)
    4. 목표가 (있는 경우)
    5. 시간 프레임 (단기/중기/장기)
    
    글: {content}
    """
    
    response = await sonnet_api.complete(prompt)
    return parse_signal_response(response)
```

### 데이터베이스 스키마

#### 기존 테이블과의 통합 방안
기존 `influencer_signals` 테이블과 통합하여 `source` 컬럼으로 구분

```sql
-- 기존 테이블 확장
ALTER TABLE influencer_signals 
ADD COLUMN source TEXT DEFAULT 'youtube',
ADD COLUMN platform_id TEXT,
ADD COLUMN platform_url TEXT,
ADD COLUMN author_info JSONB,
ADD COLUMN engagement_metrics JSONB;

-- 새로운 인덱스 추가
CREATE INDEX idx_signals_source ON influencer_signals(source);
CREATE INDEX idx_signals_platform_id ON influencer_signals(platform_id);
CREATE INDEX idx_signals_created_date ON influencer_signals(DATE(created_at));
```

#### 원문 저장 테이블 (MongoDB)
```javascript
// raw_posts 컬렉션
{
  _id: ObjectId,
  source: "youtube|naver_cafe|naver_blog|twitter|dcinside|telegram|google",
  platform_id: "게시글 ID",
  title: "제목",
  content: "원문 내용",
  author: "작성자 정보",
  post_date: ISODate,
  url: "원본 URL", 
  metadata: {
    // 플랫폼별 추가 정보
    view_count: Number,
    like_count: Number,
    comment_count: Number
  },
  processing_status: "pending|processed|filtered_out|error",
  created_at: ISODate,
  updated_at: ISODate
}

// 인덱스
db.raw_posts.createIndex({source: 1, post_date: -1})
db.raw_posts.createIndex({processing_status: 1})
db.raw_posts.createIndex({created_at: -1})
```

## 비용 산출

### 월간 예상 비용

#### 1. 인프라 비용
- **서버:** AWS t3.medium (24시간) - $30/월
- **MongoDB Atlas:** M10 Cluster - $57/월  
- **Supabase:** Pro 플랜 - $25/월
- **소계:** $112/월

#### 2. API 비용
- **X API Basic:** $100/월 (월 50,000건)
- **Google Custom Search:** $50/월 (10,000건)
- **네이버 API:** 무료 (제한 내 사용)
- **소계:** $150/월

#### 3. AI 처리 비용
```
예상 처리량:
- 일일 수집: 2,000건
- 1차 필터 통과: 800건 (40%)
- 2차 AI 필터: 800건 × Haiku ($0.00025/1K토큰)
- 시그널 추출: 320건 × Sonnet ($0.003/1K토큰)

월간 AI 비용:
- Haiku 필터링: 800건/일 × 30일 × 500토큰 × $0.00025/1K = $3/월
- Sonnet 추출: 320건/일 × 30일 × 1000토큰 × $0.003/1K = $29/월
- 소계: $32/월
```

#### 4. 기타 비용
- **프록시/VPN:** $20/월 (IP 로테이션)
- **모니터링:** $10/월
- **소계:** $30/월

### **총 월간 예상 비용: $324/월**

## 구현 우선순위 매트릭스

### 우선순위 1 (즉시 시작)
| 소스 | 구현 난이도 | 데이터 품질 | 법적 리스크 | 비용 | 점수 |
|------|-------------|-------------|-------------|------|------|
| 유튜브 | ⭐ (쉬움) | ⭐⭐⭐ (높음) | ⭐⭐⭐ (낮음) | ⭐⭐⭐ (낮음) | 10/12 |
| 네이버 블로그 | ⭐⭐ (보통) | ⭐⭐⭐ (높음) | ⭐⭐⭐ (낮음) | ⭐⭐ (보통) | 10/12 |
| 텔레그램 | ⭐ (쉬움) | ⭐⭐ (중간) | ⭐⭐⭐ (낮음) | ⭐⭐⭐ (낮음) | 9/12 |

### 우선순위 2 (단계별 구현)
| 소스 | 구현 난이도 | 데이터 품질 | 법적 리스크 | 비용 | 점수 |
|------|-------------|-------------|-------------|------|------|
| 구글 검색 | ⭐ (쉬움) | ⭐⭐⭐ (높음) | ⭐⭐⭐ (낮음) | ⭐ (높음) | 8/12 |
| 트위터/X | ⭐⭐ (보통) | ⭐⭐ (중간) | ⭐⭐⭐ (낮음) | ⭐ (높음) | 8/12 |

### 우선순위 3 (후순위)
| 소스 | 구현 난이도 | 데이터 품질 | 법적 리스크 | 비용 | 점수 |
|------|-------------|-------------|-------------|------|------|
| 네이버 카페 | ⭐⭐⭐ (어려움) | ⭐⭐⭐ (높음) | ⭐⭐ (중간) | ⭐⭐ (보통) | 7/12 |
| 디시/에펨 | ⭐⭐⭐ (어려움) | ⭐ (낮음) | ⭐⭐ (중간) | ⭐⭐ (보통) | 5/12 |

## 개발 로드맵

### Phase 1 (1-2주): 기본 파이프라인 구축
1. **유튜브 크롤러 확장**
   - 기존 시스템에 투자 채널 추가
   - 자막 기반 시그널 추출 파이프라인 구축

2. **텔레그램 크롤러**
   - 주요 투자 채널 모니터링
   - 실시간 메시지 수집 및 필터링

3. **기본 AI 파이프라인**
   - Haiku 기반 1차 필터링
   - Sonnet 기반 시그널 추출

### Phase 2 (2-3주): 웹 소스 추가
1. **네이버 블로그 크롤러**
   - 검색 API 연동
   - RSS 피드 모니터링

2. **구글 검색 크롤러**
   - Custom Search API 연동
   - 검색 쿼리 최적화

### Phase 3 (3-4주): 고급 소스 추가  
1. **트위터/X 크롤러**
   - API 연동 및 실시간 수집
   - 한국 주식 계정 타겟팅

2. **데이터 품질 개선**
   - 중복 제거 로직
   - 시그널 검증 시스템

### Phase 4 (4-6주): 고난이도 소스
1. **네이버 카페 크롤러**
   - 웹 스크래핑 시스템
   - 로그인 자동화

2. **디시인사이드 크롤러**
   - 스크래핑 및 우회 시스템
   - IP 로테이션 구현

## 위험 요소 및 대응책

### 기술적 위험
1. **API 제한/차단**
   - 대응: 다중 계정, 프록시 로테이션
   - 백업: 스크래핑 방식 준비

2. **AI 필터링 정확도**
   - 대응: 학습 데이터 지속 개선
   - 백업: 사람 검증 파이프라인

### 법적 위험  
1. **저작권 이슈**
   - 대응: Fair use 원칙, 출처 명시
   - 백업: 요약/인용 수준으로 제한

2. **TOS 위반**
   - 대응: 플랫폼별 TOS 주기적 검토
   - 백업: API 우선, 스크래핑 최소화

### 운영 위험
1. **서버 부하**
   - 대응: AWS Auto Scaling, 분산 처리
   - 모니터링: CloudWatch 알림

2. **데이터 품질 저하**
   - 대응: 실시간 품질 모니터링
   - 알림: 일일 품질 리포트

## 성공 지표 (KPI)

### 정량적 지표
- **수집량:** 일일 1,000개 이상 원문 수집
- **필터링 정확도:** 90% 이상
- **시그널 추출 정확도:** 85% 이상  
- **시스템 가동률:** 99% 이상

### 정성적 지표
- **데이터 다양성:** 7개 소스 모두 안정적 수집
- **실시간성:** 30분 이내 최신 데이터 반영
- **사용자 만족도:** 투자 결정에 도움되는 인사이트 제공

---

## 결론

본 투자 아이디어 수집 시스템은 한국 웹의 주요 플랫폼에서 체계적으로 투자 정보를 수집하고 AI를 활용해 고품질 시그널을 추출하는 종합적인 솔루션입니다.

**핵심 강점:**
- 7개 주요 플랫폼 커버로 포괄적 데이터 수집
- 기존 유튜브 파이프라인 활용으로 빠른 구축 가능
- AI 2단계 필터링으로 높은 데이터 품질 보장
- 단계적 구현으로 위험 최소화

**즉시 시작 가능한 우선순위 1 소스들(유튜브, 네이버 블로그, 텔레그램)부터 구축하여 초기 성과를 확보한 후, 순차적으로 확장하는 전략을 권장합니다.**