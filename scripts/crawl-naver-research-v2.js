/**
 * 네이버증권 리서치 크롤링 V2
 * - 페이지네이션 지원 (3년치 전부 수집)
 * - target_price 파싱 강화
 * - 중단/재개 지원 (progress.json)
 * - 기존 데이터 머지
 * 
 * 사용법: node scripts/crawl-naver-research-v2.js
 * 옵션:  node scripts/crawl-naver-research-v2.js --resume  (이어하기)
 *        node scripts/crawl-naver-research-v2.js --fresh   (처음부터)
 */
const fs = require('fs');
const path = require('path');

// ============================================================
// 설정
// ============================================================
const THREE_YEARS_AGO = new Date();
THREE_YEARS_AGO.setFullYear(THREE_YEARS_AGO.getFullYear() - 3);
const CUTOFF_DATE = THREE_YEARS_AGO.toISOString().split('T')[0]; // 예: 2023-03-15

const MAX_PAGES_PER_TICKER = 30; // 안전장치 (3년치면 보통 5~15페이지)
const DELAY_BETWEEN_DETAIL = 1500; // 상세 페이지 간 딜레이 (ms)
const DELAY_BETWEEN_PAGES = 2000;  // 페이지 간 딜레이
const DELAY_BETWEEN_TICKERS = 3000; // 종목 간 딜레이

const KR_TICKERS = [
  // 기존 20종목
  '090430','240810','000660','079160','005380','005930','036930',
  '042700','403870','006400','352820','298040','000720','284620',
  '005940','016360','039490','051910','036570','071050',
  // 확장 종목 (시총 상위 + 리포트 많은 종목)
  '035420','055550','068270','105560','005490','012330','066570',
  '028260','000270','096770','003550','034730','032830','011200',
  '018260','009150','030200','086790','259960','035720',
  '004020','003670','010130','011170','017670',
];

const TICKER_NAMES = {
  '090430':'아모레퍼시픽','240810':'원익QnC','000660':'SK하이닉스','079160':'CJ CGV',
  '005380':'현대자동차','005930':'삼성전자','036930':'주성엔지니어링','042700':'한미반도체',
  '403870':'HPSP','006400':'삼성SDI','352820':'하이브','298040':'효성중공업',
  '000720':'현대건설','284620':'카이','005940':'NH투자증권','016360':'삼성증권',
  '039490':'키움증권','051910':'LG화학','036570':'엔씨소프트','071050':'한국금융지주',
  '035420':'NAVER','055550':'신한지주','068270':'셀트리온','105560':'KB금융',
  '005490':'POSCO홀딩스','012330':'현대모비스','066570':'LG전자','028260':'삼성물산',
  '000270':'기아','096770':'SK이노베이션','003550':'LG','034730':'SK',
  '032830':'삼성생명','011200':'HMM','018260':'삼성에스디에스','009150':'삼성전기',
  '030200':'KT','086790':'하나금융지주','259960':'크래프톤','035720':'카카오',
  '004020':'현대제철','003670':'포스코퓨처엠','010130':'고려아연','011170':'롯데케미칼',
  '017670':'SK텔레콤',
};

const OUT_DIR = path.join(__dirname, '..', 'data');
const PROGRESS_FILE = path.join(OUT_DIR, 'crawl_progress.json');
const OUT_FILE = path.join(OUT_DIR, 'analyst_reports.json');

// ============================================================
// 유틸
// ============================================================
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function parseDate(text) {
  const match = text.trim().match(/(\d{2,4})\.(\d{2})\.(\d{2})/);
  if (!match) return null;
  let year = parseInt(match[1]);
  if (year < 100) year += 2000;
  return `${year}-${match[2]}-${match[3]}`;
}

function normalizeOpinion(text) {
  if (!text) return null;
  const lower = text.toLowerCase().trim();
  if (lower.includes('매수') || lower.includes('buy') || lower.includes('trading buy') || lower.includes('outperform') || lower.includes('overweight')) return 'BUY';
  if (lower.includes('중립') || lower.includes('hold') || lower.includes('marketperform') || lower.includes('neutral') || lower.includes('market perform')) return 'HOLD';
  if (lower.includes('매도') || lower.includes('sell') || lower.includes('underperform') || lower.includes('underweight') || lower.includes('reduce')) return 'SELL';
  if (lower.includes('not rated') || lower.includes('n/r') || lower.includes('없음')) return null;
  return null;
}

function log(msg) {
  const ts = new Date().toLocaleTimeString('ko-KR');
  console.log(`[${ts}] ${msg}`);
}

// ============================================================
// 상세 페이지 크롤링 (목표가 / 투자의견 / 애널리스트)
// ============================================================
async function fetchDetailPage(nid, ticker, retryCount = 0) {
  const url = `https://finance.naver.com/research/company_read.naver?nid=${nid}&page=1&searchType=itemCode&itemCode=${ticker}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8',
        'Referer': 'https://finance.naver.com/research/company_list.naver',
      }
    });
    
    if (response.status === 429) {
      if (retryCount < 3) {
        log(`    ⏳ Rate limited, waiting 60s... (retry ${retryCount + 1}/3)`);
        await sleep(60000);
        return fetchDetailPage(nid, ticker, retryCount + 1);
      }
      throw new Error('Too many retries for rate limiting');
    }
    
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const buffer = await response.arrayBuffer();
    const html = new TextDecoder('euc-kr').decode(new Uint8Array(buffer));
    
    let targetPrice = null;
    let opinion = null;
    let analyst = null;
    
    // === 목표가 추출 (강화) ===
    // 패턴 1: 테이블 내 "목표가" 셀 다음 가격
    const tpPatterns = [
      /목표주가[^<\d]*?([\d,]+)\s*원?/i,
      /목표가[^<\d]*?([\d,]+)\s*원?/i,
      /Target\s*(?:Price)?[^<\d]*?([\d,]+)/i,
      /TP[^<\d]*?([\d,]+)/i,
      // 테이블 구조: <em>목표가</em> ... 숫자
      /목표가<\/em>[^<]*<[^>]*>([\d,]+)/i,
      // td 안에 목표가 + 숫자
      /목표가[^\d]{0,30}([\d,]+)/i,
    ];
    
    for (const pattern of tpPatterns) {
      const match = html.match(pattern);
      if (match) {
        const priceStr = match[1].replace(/,/g, '');
        const price = parseInt(priceStr, 10);
        if (!isNaN(price) && price >= 1000 && price < 100000000) {
          targetPrice = price;
          break;
        }
      }
    }
    
    // === 투자의견 추출 (강화) ===
    const opinionPatterns = [
      /투자의견[^가-힣\w]{0,10}(매수|Buy|Strong Buy|Trading Buy|Outperform|중립|Hold|Neutral|Market\s*Perform|매도|Sell|Underperform|Reduce)/i,
      /의견[^가-힣\w]{0,10}(매수|Buy|Strong Buy|중립|Hold|매도|Sell)/i,
      /Rating[^가-힣\w]{0,10}(Buy|Strong Buy|Outperform|Hold|Neutral|Sell|Underperform)/i,
    ];
    
    for (const pattern of opinionPatterns) {
      const match = html.match(pattern);
      if (match) {
        opinion = normalizeOpinion(match[1]);
        if (opinion) break;
      }
    }
    
    // === 애널리스트명 추출 (강화) ===
    const analystPatterns = [
      // 네이버 리서치 상세 페이지의 실제 구조
      /class="coment_name"[^>]*>([가-힣]{2,4})/i,
      /애널리스트[^가-힣]{0,20}([가-힣]{2,4})/i,
      /작성자[^가-힣]{0,20}([가-힣]{2,4})/i,
      /분석가[^가-힣]{0,20}([가-힣]{2,4})/i,
      // 리포트 본문에 자주 나오는 패턴
      /담당[^가-힣]{0,10}([가-힣]{2,4})/i,
    ];
    
    for (const pattern of analystPatterns) {
      const match = html.match(pattern);
      if (match) {
        const name = match[1].trim();
        // 흔한 비-이름 필터
        const blacklist = ['종목명','증권사','목표가','투자의견','리포트','애널리스트','작성자'];
        if (!blacklist.includes(name) && name.length >= 2) {
          analyst = name;
          break;
        }
      }
    }
    
    return { targetPrice, opinion, analyst };
    
  } catch (err) {
    if (retryCount < 2) {
      await sleep(5000);
      return fetchDetailPage(nid, ticker, retryCount + 1);
    }
    log(`    ❌ Detail fetch error (nid=${nid}): ${err.message}`);
    return { targetPrice: null, opinion: null, analyst: null };
  }
}

// ============================================================
// 목록 페이지 크롤링 (1페이지)
// ============================================================
async function crawlListPage(ticker, page) {
  const url = `https://finance.naver.com/research/company_list.naver?searchType=itemCode&itemCode=${ticker}&page=${page}`;
  
  const response = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Accept-Language': 'ko-KR,ko;q=0.9',
      'Referer': 'https://finance.naver.com/research/company_list.naver',
    }
  });
  
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  
  const buffer = await response.arrayBuffer();
  const html = new TextDecoder('euc-kr').decode(new Uint8Array(buffer));
  
  const reports = [];
  let hasOlderThanCutoff = false;
  
  const rows = html.split(/<tr[^>]*>/gi);
  
  for (const row of rows) {
    if (!row.includes('company_read')) continue;
    
    // NID 추출
    const nidMatch = row.match(/company_read\.naver\?[^"']*?nid=(\d+)/i);
    if (!nidMatch) continue;
    const nid = nidMatch[1];
    
    // 제목 추출
    const titleMatch = row.match(/company_read\.naver[^"]*"[^>]*>\s*([\s\S]*?)\s*<\/a>/i);
    const title = titleMatch ? titleMatch[1].replace(/<[^>]*>/g, '').trim() : '';
    if (!title) continue;
    
    // TD 데이터 추출
    const tds = [];
    const tdRegex = /<td[^>]*>([\s\S]*?)<\/td>/gi;
    let m;
    while ((m = tdRegex.exec(row)) !== null) {
      tds.push(m[1].replace(/<[^>]*>/g, '').trim());
    }
    
    if (tds.length < 5) continue;
    
    const firm = tds[2] || 'Unknown';
    const date = parseDate(tds[4]);
    if (!date) continue;
    
    // 3년 전보다 오래된 리포트면 중단 신호
    if (date < CUTOFF_DATE) {
      hasOlderThanCutoff = true;
      continue;
    }
    
    // PDF URL
    const pdfMatch = row.match(/href="(https?:\/\/[^"]*\.pdf[^"]*)"/i);
    const pdfUrl = pdfMatch ? pdfMatch[1] : null;
    
    // 목록 페이지에서 바로 추출 가능한 것들
    // 목표가: tds[3]에 가격이 있을 수 있음
    let listTargetPrice = null;
    if (tds[3]) {
      const priceStr = tds[3].replace(/,/g, '').trim();
      const price = parseInt(priceStr, 10);
      if (!isNaN(price) && price >= 1000) {
        listTargetPrice = price;
      }
    }
    
    // 투자의견: tds[1]에 있을 수 있음
    let listOpinion = null;
    if (tds[1]) {
      listOpinion = normalizeOpinion(tds[1]);
    }
    
    reports.push({
      nid,
      ticker,
      firm,
      title,
      published_at: date,
      pdf_url: pdfUrl,
      list_target_price: listTargetPrice,
      list_opinion: listOpinion,
    });
  }
  
  // 마지막 페이지 감지 (페이지네이션에 다음 페이지 없으면)
  const hasNextPage = html.includes(`page=${page + 1}`);
  
  return { reports, hasOlderThanCutoff, hasNextPage };
}

// ============================================================
// 종목 전체 크롤링 (페이지네이션)
// ============================================================
async function crawlTicker(ticker, existingNids = new Set()) {
  const allReports = [];
  let page = 1;
  
  while (page <= MAX_PAGES_PER_TICKER) {
    log(`    📄 Page ${page}...`);
    
    try {
      const { reports, hasOlderThanCutoff, hasNextPage } = await crawlListPage(ticker, page);
      
      if (reports.length === 0 && !hasNextPage) {
        log(`    → 빈 페이지, 종료`);
        break;
      }
      
      // 상세 페이지에서 추가 정보 수집
      for (const report of reports) {
        // 이미 수집된 리포트 스킵
        if (existingNids.has(report.nid)) {
          log(`    ⏭ nid=${report.nid} already exists, skip`);
          continue;
        }
        
        log(`    🔍 nid=${report.nid} "${report.title.slice(0, 30)}..."`);
        
        const details = await fetchDetailPage(report.nid, ticker);
        
        allReports.push({
          ticker: report.ticker,
          firm: report.firm,
          analyst: details.analyst,
          title: report.title,
          target_price: details.targetPrice || report.list_target_price,
          opinion: details.opinion || report.list_opinion || 'BUY',
          published_at: report.published_at,
          pdf_url: report.pdf_url,
          nid: report.nid,
        });
        
        await sleep(DELAY_BETWEEN_DETAIL + Math.random() * 1000);
      }
      
      // 3년 전 데이터 도달하면 중단
      if (hasOlderThanCutoff) {
        log(`    → 3년 전 데이터 도달 (cutoff: ${CUTOFF_DATE}), 종료`);
        break;
      }
      
      if (!hasNextPage) {
        log(`    → 마지막 페이지`);
        break;
      }
      
      page++;
      await sleep(DELAY_BETWEEN_PAGES + Math.random() * 1000);
      
    } catch (err) {
      log(`    ❌ Page ${page} error: ${err.message}`);
      // 에러 시 다음 페이지로 넘어가지 않고 중단
      break;
    }
  }
  
  return allReports;
}

// ============================================================
// 진행 상황 저장/로드
// ============================================================
function saveProgress(completedTickers, allReports) {
  const progress = {
    completedTickers,
    timestamp: new Date().toISOString(),
    totalReports: Object.values(allReports).reduce((s, r) => s + r.length, 0),
  };
  fs.writeFileSync(PROGRESS_FILE, JSON.stringify(progress, null, 2));
  
  // 중간 저장
  fs.writeFileSync(OUT_FILE, JSON.stringify(allReports, null, 2), 'utf-8');
  log(`💾 Progress saved: ${progress.totalReports} reports, ${completedTickers.length} tickers done`);
}

function loadProgress() {
  if (!fs.existsSync(PROGRESS_FILE)) return null;
  try {
    return JSON.parse(fs.readFileSync(PROGRESS_FILE, 'utf-8'));
  } catch {
    return null;
  }
}

// ============================================================
// 메인
// ============================================================
async function main() {
  const args = process.argv.slice(2);
  const isResume = args.includes('--resume');
  const isFresh = args.includes('--fresh');
  
  log(`🚀 네이버 리서치 크롤러 V2`);
  log(`📅 수집 범위: ${CUTOFF_DATE} ~ 현재`);
  log(`📊 대상 종목: ${KR_TICKERS.length}개`);
  
  // 기존 데이터 로드
  let allReports = {};
  let completedTickers = [];
  
  if (!isFresh && fs.existsSync(OUT_FILE)) {
    try {
      allReports = JSON.parse(fs.readFileSync(OUT_FILE, 'utf-8'));
      log(`📂 기존 데이터 로드: ${Object.values(allReports).reduce((s, r) => s + r.length, 0)}건`);
    } catch {
      allReports = {};
    }
  }
  
  if (isResume) {
    const progress = loadProgress();
    if (progress) {
      completedTickers = progress.completedTickers;
      log(`🔄 이어하기: ${completedTickers.length}개 종목 완료, 나머지부터 시작`);
    }
  }
  
  const tickersToProcess = KR_TICKERS.filter(t => !completedTickers.includes(t));
  log(`📋 처리할 종목: ${tickersToProcess.length}개\n`);
  
  let processedCount = completedTickers.length;
  
  for (const ticker of tickersToProcess) {
    const name = TICKER_NAMES[ticker] || ticker;
    processedCount++;
    log(`\n[${processedCount}/${KR_TICKERS.length}] ${name} (${ticker})`);
    
    // 기존 nid 목록 (중복 방지)
    const existingNids = new Set(
      (allReports[ticker] || []).map(r => r.nid).filter(Boolean)
    );
    
    try {
      const newReports = await crawlTicker(ticker, existingNids);
      
      if (newReports.length > 0) {
        // 기존 데이터와 머지 (nid 기준 중복 제거)
        const existing = allReports[ticker] || [];
        const existingNidSet = new Set(existing.map(r => r.nid).filter(Boolean));
        const merged = [
          ...existing,
          ...newReports.filter(r => !existingNidSet.has(r.nid))
        ];
        // 날짜순 정렬 (최신 먼저)
        merged.sort((a, b) => b.published_at.localeCompare(a.published_at));
        allReports[ticker] = merged;
      }
      
      log(`  ✅ ${name}: ${(allReports[ticker] || []).length}건 (신규 ${newReports.length}건)`);
      
    } catch (err) {
      log(`  ❌ ${name} 에러: ${err.message}`);
    }
    
    // 진행 상황 저장
    completedTickers.push(ticker);
    saveProgress(completedTickers, allReports);
    
    // 종목 간 딜레이
    await sleep(DELAY_BETWEEN_TICKERS + Math.random() * 2000);
  }
  
  // 최종 저장
  fs.writeFileSync(OUT_FILE, JSON.stringify(allReports, null, 2), 'utf-8');
  
  // 통계
  const total = Object.values(allReports).reduce((s, r) => s + r.length, 0);
  const nullTP = Object.values(allReports).flat().filter(r => !r.target_price).length;
  const nullAnalyst = Object.values(allReports).flat().filter(r => !r.analyst).length;
  
  log(`\n${'='.repeat(50)}`);
  log(`✅ 완료!`);
  log(`📊 총 ${total}건 / ${Object.keys(allReports).length}개 종목`);
  log(`❓ target_price NULL: ${nullTP}건 (${(nullTP/total*100).toFixed(1)}%)`);
  log(`❓ analyst NULL: ${nullAnalyst}건 (${(nullAnalyst/total*100).toFixed(1)}%)`);
  log(`📁 저장: ${OUT_FILE}`);
  
  // progress 파일 정리
  if (fs.existsSync(PROGRESS_FILE)) {
    fs.unlinkSync(PROGRESS_FILE);
  }
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
