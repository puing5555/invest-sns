// ============================================
// DART 공시 크롤링 파이프라인
// 용도: 로컬 테스트 + Supabase Edge Function 양쪽 사용
// ============================================

// ============================================
// 1. 설정
// ============================================

const CONFIG = {
  DART_API_KEY: 'e4523175bccca28542cb423e21adb2ef080cc2f5',
  DART_BASE_URL: 'https://opendart.fss.or.kr/api',
  SUPABASE_URL: 'https://arypzhotxflimroprmdk.supabase.co',
  SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A',
  PAGE_COUNT: 100,  // 한 번에 가져올 공시 수 (최대 100)
};

// ============================================
// 2. DART API 호출 함수들
// ============================================

interface DartDisclosure {
  corp_code: string;
  corp_name: string;
  stock_code: string;
  corp_cls: string;       // Y:유가, K:코스닥, N:코넥스, E:기타
  report_nm: string;      // 공시 제목
  rcept_no: string;       // 접수번호 (고유ID)
  flr_nm: string;         // 공시 제출인
  rcept_dt: string;       // 접수일자 (YYYYMMDD)
  rm: string;             // 비고 (유/코/코넥)
}

interface DartResponse {
  status: string;
  message: string;
  page_no: number;
  page_count: number;
  total_count: number;
  total_page: number;
  list: DartDisclosure[];
}

// 공시 목록 검색
async function fetchDisclosures(
  bgn_de: string,  // 시작일 YYYYMMDD
  end_de: string,  // 종료일 YYYYMMDD
  page_no: number = 1,
  corp_cls: string = ''  // Y:유가, K:코스닥 (빈값=전체)
): Promise<DartResponse> {
  const params = new URLSearchParams({
    crtfc_key: CONFIG.DART_API_KEY,
    bgn_de,
    end_de,
    page_no: String(page_no),
    page_count: String(CONFIG.PAGE_COUNT),
    sort: 'date',
    sort_mth: 'desc',
  });
  
  if (corp_cls) params.append('corp_cls', corp_cls);

  const url = `${CONFIG.DART_BASE_URL}/list.json?${params.toString()}`;
  const res = await fetch(url);
  const data: DartResponse = await res.json();
  
  if (data.status !== '000') {
    console.error(`DART API Error: ${data.status} - ${data.message}`);
  }
  
  return data;
}

// ============================================
// 3. AI 등급 분류 (키워드 룰엔진 Phase 1)
// ============================================

interface GradeResult {
  grade: 'A' | 'B' | 'C';
  disclosure_type: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  ai_one_liner: string;
}

function classifyDisclosure(title: string, corp_name: string): GradeResult {
  const t = title.toLowerCase();
  
  // ========== A등급: 주가에 즉시 영향 ==========
  
  // 공급계약/수주
  if (t.includes('공급계약') || t.includes('수주') || t.includes('납품계약')) {
    const isLarge = t.includes('대규모') || t.includes('단일판매') || t.includes('단일공급');
    return {
      grade: 'A',
      disclosure_type: '공급계약',
      sentiment: 'positive',
      ai_one_liner: `${corp_name} ${isLarge ? '대규모 ' : ''}공급계약 체결. 매출 증가 기대.`,
    };
  }

  // 자기주식 취득 (매수 = 호재)
  if (t.includes('자기주식') && (t.includes('취득') || t.includes('신탁계약'))) {
    return {
      grade: 'A',
      disclosure_type: '자사주취득',
      sentiment: 'positive',
      ai_one_liner: `${corp_name} 자사주 매입 결정. 주가 부양 의지 확인.`,
    };
  }

  // 자기주식 처분 (매도 = 악재)
  if (t.includes('자기주식') && t.includes('처분')) {
    return {
      grade: 'A',
      disclosure_type: '자사주처분',
      sentiment: 'negative',
      ai_one_liner: `${corp_name} 자사주 처분 결정. 수급 부담 가능성.`,
    };
  }

  // 배당
  if (t.includes('배당') || t.includes('현금·현물배당')) {
    return {
      grade: 'A',
      disclosure_type: '배당',
      sentiment: 'positive',
      ai_one_liner: `${corp_name} 배당 결정 공시. 주주환원 정책 확인.`,
    };
  }

  // 실적 (매출/영업이익)
  if (t.includes('영업(잠정)') || t.includes('매출액') || t.includes('실적') ||
      t.includes('연결재무') || t.includes('반기보고') || t.includes('분기보고')) {
    // 정기보고서는 B등급으로
    if (t.includes('사업보고서') || t.includes('반기보고서') || t.includes('분기보고서')) {
      return {
        grade: 'B',
        disclosure_type: '정기보고서',
        sentiment: 'neutral',
        ai_one_liner: `${corp_name} 정기보고서 제출.`,
      };
    }
    return {
      grade: 'A',
      disclosure_type: '실적발표',
      sentiment: 'neutral',
      ai_one_liner: `${corp_name} 실적 공시. 어닝 서프라이즈/쇼크 확인 필요.`,
    };
  }

  // 임원 변동/지분 변동
  if (t.includes('임원') && (t.includes('소유상황') || t.includes('특정증권'))) {
    return {
      grade: 'A',
      disclosure_type: '임원매매',
      sentiment: 'neutral',
      ai_one_liner: `${corp_name} 임원/대주주 지분 변동. 매수/매도 확인 필요.`,
    };
  }

  // 대주주 지분변동
  if (t.includes('주식등의대량보유') || t.includes('대량보유')) {
    return {
      grade: 'A',
      disclosure_type: '대량보유',
      sentiment: 'neutral',
      ai_one_liner: `${corp_name} 대량보유 변동. 경영권 이슈 가능성.`,
    };
  }

  // 유상증자/무상증자
  if (t.includes('유상증자') || t.includes('신주발행')) {
    return {
      grade: 'A',
      disclosure_type: '유상증자',
      sentiment: 'negative',
      ai_one_liner: `${corp_name} 유상증자 결정. 지분 희석 우려.`,
    };
  }

  if (t.includes('무상증자')) {
    return {
      grade: 'A',
      disclosure_type: '무상증자',
      sentiment: 'positive',
      ai_one_liner: `${corp_name} 무상증자 결정. 주주친화 정책.`,
    };
  }

  // 합병/인수/분할
  if (t.includes('합병') || t.includes('인수') || t.includes('분할')) {
    return {
      grade: 'A',
      disclosure_type: 'M&A',
      sentiment: 'neutral',
      ai_one_liner: `${corp_name} M&A/분할 관련 공시. 기업가치 변동 가능.`,
    };
  }

  // 기업가치 제고
  if (t.includes('기업가치') && t.includes('제고')) {
    return {
      grade: 'A',
      disclosure_type: '기업가치제고',
      sentiment: 'positive',
      ai_one_liner: `${corp_name} 기업가치 제고 계획 공시. 밸류업 프로그램.`,
    };
  }

  // 해명/정정
  if (t.includes('해명') || t.includes('정정')) {
    return {
      grade: 'A',
      disclosure_type: '해명정정',
      sentiment: 'neutral',
      ai_one_liner: `${corp_name} 해명/정정 공시. 이전 공시 내용 변경.`,
    };
  }

  // CB/BW 발행
  if (t.includes('전환사채') || t.includes('신주인수권부사채') || t.includes('cb') || t.includes('bw')) {
    return {
      grade: 'A',
      disclosure_type: 'CB/BW',
      sentiment: 'negative',
      ai_one_liner: `${corp_name} CB/BW 발행. 향후 전환 시 지분 희석 우려.`,
    };
  }

  // 상장폐지/관리종목
  if (t.includes('상장폐지') || t.includes('관리종목')) {
    return {
      grade: 'A',
      disclosure_type: '상장폐지위험',
      sentiment: 'negative',
      ai_one_liner: `${corp_name} 상장폐지/관리종목 관련 공시. 주의 필요.`,
    };
  }

  // ========== B등급: 참고할 만한 정보 ==========

  // 주요사항보고
  if (t.includes('주요사항보고') || t.includes('타법인주식') || t.includes('채권발행')) {
    return {
      grade: 'B',
      disclosure_type: '주요사항',
      sentiment: 'neutral',
      ai_one_liner: `${corp_name} 주요사항 보고.`,
    };
  }

  // 소송/분쟁
  if (t.includes('소송') || t.includes('분쟁') || t.includes('제재')) {
    return {
      grade: 'B',
      disclosure_type: '소송분쟁',
      sentiment: 'negative',
      ai_one_liner: `${corp_name} 소송/분쟁 관련 공시.`,
    };
  }

  // 사외이사/감사 선임
  if (t.includes('이사') && (t.includes('선임') || t.includes('해임'))) {
    return {
      grade: 'B',
      disclosure_type: '임원변동',
      sentiment: 'neutral',
      ai_one_liner: `${corp_name} 이사/감사 인사 변동.`,
    };
  }

  // ========== C등급: 일반 공시 ==========
  return {
    grade: 'C',
    disclosure_type: '일반',
    sentiment: 'neutral',
    ai_one_liner: `${corp_name} 일반 공시.`,
  };
}

// ============================================
// 4. Supabase 저장
// ============================================

async function saveToSupabase(disclosures: DartDisclosure[]): Promise<number> {
  let savedCount = 0;
  
  // 상장사만 필터 (stock_code가 있는 것)
  const listed = disclosures.filter(d => d.stock_code && d.stock_code.trim() !== '');
  
  if (listed.length === 0) {
    console.log('상장사 공시 없음, 스킵');
    return 0;
  }

  // Supabase에 upsert
  const rows = listed.map(d => {
    const grade = classifyDisclosure(d.report_nm, d.corp_name);
    
    return {
      dart_id: d.rcept_no,
      stock_code: d.stock_code,
      corp_name: d.corp_name,
      title: d.report_nm,
      disclosure_type: grade.disclosure_type,
      grade: grade.grade,
      sentiment: grade.sentiment,
      ai_one_liner: grade.ai_one_liner,
      report_url: `https://dart.fss.or.kr/dsaf001/main.do?rcpNo=${d.rcept_no}`,
      submitted_at: formatDate(d.rcept_dt),
      corp_cls: d.corp_cls,
    };
  });

  // 배치로 나눠서 저장 (50개씩)
  const BATCH_SIZE = 50;
  for (let i = 0; i < rows.length; i += BATCH_SIZE) {
    const batch = rows.slice(i, i + BATCH_SIZE);
    
    const res = await fetch(`${CONFIG.SUPABASE_URL}/rest/v1/disclosures`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': CONFIG.SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${CONFIG.SUPABASE_ANON_KEY}`,
        'Prefer': 'resolution=merge-duplicates',  // upsert (dart_id UNIQUE)
      },
      body: JSON.stringify(batch),
    });

    if (res.ok) {
      savedCount += batch.length;
      console.log(`  저장 ${i + 1}~${i + batch.length} / ${rows.length}`);
    } else {
      const err = await res.text();
      console.error(`  저장 실패: ${res.status} - ${err}`);
    }
  }

  return savedCount;
}

// ============================================
// 5. 유틸리티
// ============================================

function formatDate(yyyymmdd: string): string {
  // YYYYMMDD → YYYY-MM-DD
  return `${yyyymmdd.slice(0, 4)}-${yyyymmdd.slice(4, 6)}-${yyyymmdd.slice(6, 8)}`;
}

function getToday(): string {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  const d = String(now.getDate()).padStart(2, '0');
  return `${y}${m}${d}`;
}

function getDaysAgo(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${y}${m}${dd}`;
}

// ============================================
// 6. 메인 파이프라인
// ============================================

interface CrawlResult {
  total_fetched: number;
  total_saved: number;
  a_grade: number;
  b_grade: number;
  c_grade: number;
  date_range: string;
}

// 실시간 크롤링 (오늘 ~ 어제)
async function crawlRecent(): Promise<CrawlResult> {
  console.log('=== DART 실시간 크롤링 시작 ===');
  const today = getToday();
  const yesterday = getDaysAgo(1);
  
  return await crawlDateRange(yesterday, today);
}

// 백데이터 크롤링 (특정 기간)
async function crawlBackfill(bgn_de: string, end_de: string): Promise<CrawlResult> {
  console.log(`=== DART 백데이터 크롤링: ${bgn_de} ~ ${end_de} ===`);
  return await crawlDateRange(bgn_de, end_de);
}

// 날짜 범위 크롤링 (코어 로직)
async function crawlDateRange(bgn_de: string, end_de: string): Promise<CrawlResult> {
  let totalFetched = 0;
  let totalSaved = 0;
  let aGrade = 0, bGrade = 0, cGrade = 0;
  let page = 1;

  while (true) {
    console.log(`  페이지 ${page} 조회 중... (${bgn_de} ~ ${end_de})`);
    
    const data = await fetchDisclosures(bgn_de, end_de, page);
    
    if (data.status !== '000' || !data.list || data.list.length === 0) {
      console.log(`  조회 완료 또는 데이터 없음 (status: ${data.status})`);
      break;
    }

    totalFetched += data.list.length;
    
    // 등급별 카운트
    for (const d of data.list) {
      if (d.stock_code && d.stock_code.trim() !== '') {
        const { grade } = classifyDisclosure(d.report_nm, d.corp_name);
        if (grade === 'A') aGrade++;
        else if (grade === 'B') bGrade++;
        else cGrade++;
      }
    }

    // Supabase 저장
    const saved = await saveToSupabase(data.list);
    totalSaved += saved;

    // 다음 페이지
    if (page >= data.total_page) {
      console.log(`  전체 ${data.total_page}페이지 완료`);
      break;
    }
    
    page++;
    
    // API 부하 방지 (0.3초 대기)
    await new Promise(r => setTimeout(r, 300));
  }

  const result: CrawlResult = {
    total_fetched: totalFetched,
    total_saved: totalSaved,
    a_grade: aGrade,
    b_grade: bGrade,
    c_grade: cGrade,
    date_range: `${bgn_de} ~ ${end_de}`,
  };

  console.log('\n=== 크롤링 결과 ===');
  console.log(`  기간: ${result.date_range}`);
  console.log(`  수집: ${result.total_fetched}건`);
  console.log(`  저장: ${result.total_saved}건 (상장사만)`);
  console.log(`  A등급: ${result.a_grade}건 | B등급: ${result.b_grade}건 | C등급: ${result.c_grade}건`);

  return result;
}

// ============================================
// 7. 백데이터 스케줄러 (남은 API 한도로 과거 수집)
// ============================================

async function crawlBackfillScheduled(): Promise<CrawlResult[]> {
  // 3개월씩 나눠서 수집 (corp_code 없으면 최대 3개월 제한)
  const results: CrawlResult[] = [];
  
  // 오늘 기준 1년 전부터 수집
  const periods = [
    // 최근부터 과거순으로
    { bgn: getDaysAgo(90), end: getDaysAgo(2) },    // 3개월 전 ~ 2일 전
    { bgn: getDaysAgo(180), end: getDaysAgo(91) },   // 6개월 전 ~ 3개월 전
    { bgn: getDaysAgo(270), end: getDaysAgo(181) },   // 9개월 전 ~ 6개월 전
    { bgn: getDaysAgo(365), end: getDaysAgo(271) },   // 1년 전 ~ 9개월 전
  ];

  for (const period of periods) {
    console.log(`\n--- 백필 기간: ${period.bgn} ~ ${period.end} ---`);
    const result = await crawlBackfill(period.bgn, period.end);
    results.push(result);
    
    // 기간 사이 1초 대기
    await new Promise(r => setTimeout(r, 1000));
  }

  return results;
}

// ============================================
// 8. Export (Supabase Edge Function / 로컬 실행)
// ============================================

// 로컬 실행용
async function main() {
  const mode = (typeof Deno !== 'undefined') ? 'edge' : 'local';
  console.log(`실행 모드: ${mode}`);
  
  // 실시간 크롤링
  const recentResult = await crawlRecent();
  
  // 남은 API 한도가 있으면 백데이터도 수집
  // (실시간에 ~500건 쓰고 나머지로 백필)
  if (recentResult.total_fetched < 2000) {
    console.log('\n남은 API 한도로 백데이터 수집 시작...');
    // 주의: 백필은 API 한도 많이 씀. 필요할 때만 활성화
    // await crawlBackfillScheduled();
  }
}

// Supabase Edge Function용 핸들러
// Deno.serve() 에서 호출
async function handleRequest(req: Request): Promise<Response> {
  try {
    const url = new URL(req.url);
    const mode = url.searchParams.get('mode') || 'recent';
    
    let result;
    
    if (mode === 'recent') {
      // 실시간: 어제~오늘
      result = await crawlRecent();
    } else if (mode === 'backfill') {
      // 백데이터: 파라미터로 기간 지정
      const bgn = url.searchParams.get('bgn') || getDaysAgo(90);
      const end = url.searchParams.get('end') || getDaysAgo(2);
      result = await crawlBackfill(bgn, end);
    } else if (mode === 'full') {
      // 전체: 실시간 + 백데이터
      const recent = await crawlRecent();
      const backfill = await crawlBackfillScheduled();
      result = { recent, backfill };
    }

    return new Response(JSON.stringify(result, null, 2), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: String(error) }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

// Edge Function 진입점 (Deno 환경에서만)
declare const Deno: any;
if (typeof Deno !== 'undefined') {
  Deno.serve(handleRequest);
} else {
  // Node.js 로컬 실행
  main().catch(console.error);
}

export { crawlRecent, crawlBackfill, crawlBackfillScheduled, classifyDisclosure, handleRequest };
