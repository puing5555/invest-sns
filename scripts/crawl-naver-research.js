/**
 * 네이버증권 리서치 크롤링 → JSON 파일 저장
 * 수정: 상세 페이지에서 목표가/투자의견/애널리스트명 추출
 * EUC-KR 인코딩 처리 포함
 */
const fs = require('fs');
const path = require('path');

const KR_TICKERS = [
  '090430','240810','000660','079160','005380','005930','036930',
  '042700','403870','006400','352820','298040','000720','284620',
  '005940','016360','039490','051910','036570','071050','004170',
  '267260','357780','095610','084370'
];

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function parseDate(text) {
  const match = text.trim().match(/(\d{2,4})\.(\d{2})\.(\d{2})/);
  if (!match) return null;
  let year = parseInt(match[1]);
  if (year < 100) year += 2000;
  return `${year}-${match[2]}-${match[3]}`;
}

function normalizeOpinion(text) {
  const lower = text.toLowerCase();
  if (lower.includes('매수') || lower.includes('buy') || lower.includes('trading buy')) return 'BUY';
  if (lower.includes('outperform')) return 'BUY';
  if (lower.includes('중립') || lower.includes('hold') || lower.includes('marketperform')) return 'HOLD';
  if (lower.includes('매도') || lower.includes('sell')) return 'SELL';
  if (lower.includes('not rated')) return null;
  return 'BUY'; // 기본값
}

async function fetchDetailPage(nid, ticker, retryCount = 0) {
  const url = `https://finance.naver.com/research/company_read.naver?nid=${nid}&page=1&searchType=itemCode&itemCode=${ticker}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9',
      }
    });
    
    if (response.status === 429) {
      if (retryCount < 3) {
        console.log(`    Rate limited, waiting 60s... (retry ${retryCount + 1}/3)`);
        await sleep(60000);
        return fetchDetailPage(nid, ticker, retryCount + 1);
      }
      throw new Error('Too many retries for rate limiting');
    }
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const buffer = await response.arrayBuffer();
    const html = new TextDecoder('euc-kr').decode(new Uint8Array(buffer));
    
    let targetPrice = null;
    let opinion = null;
    let analyst = null;
    
    // 목표가 추출: "목표가 300,000" 형태
    const targetPriceMatch = html.match(/목표가[^\d]*?([\d,]+)/i);
    if (targetPriceMatch) {
      const priceStr = targetPriceMatch[1].replace(/,/g, '');
      const price = parseInt(priceStr, 10);
      if (!isNaN(price) && price >= 10000) { // 최소 1만원 이상
        targetPrice = price;
      }
    }
    
    // 투자의견 추출: "투자의견 매수" 형태
    const opinionMatch = html.match(/투자의견[^\w가-힣]*?([가-힣\w\s]+)/i);
    if (opinionMatch) {
      opinion = normalizeOpinion(opinionMatch[1].trim());
    }
    
    // 애널리스트명 추출 시도 (다양한 패턴 확인)
    const analystPatterns = [
      /애널리스트[^\w가-힣]*?([가-힣]{2,4})/i,
      /분석가[^\w가-힣]*?([가-힣]{2,4})/i,
      /작성자[^\w가-힣]*?([가-힣]{2,4})/i
    ];
    
    for (const pattern of analystPatterns) {
      const match = html.match(pattern);
      if (match) {
        analyst = match[1].trim();
        break;
      }
    }
    
    return { targetPrice, opinion, analyst };
    
  } catch (err) {
    console.log(`    Detail fetch error: ${err.message}`);
    return { targetPrice: null, opinion: null, analyst: null };
  }
}

async function crawlTicker(ticker) {
  const url = `https://finance.naver.com/research/company_list.naver?searchType=itemCode&itemCode=${ticker}&page=1`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9',
      }
    });
    
    if (!response.ok) return [];
    
    const buffer = await response.arrayBuffer();
    const html = new TextDecoder('euc-kr').decode(new Uint8Array(buffer));
    
    const reports = [];
    
    // Extract NID from links: company_read.naver?nid=XXXXX
    const linkMatches = [...html.matchAll(/company_read\.naver\?[^"']*?nid=(\d+)/gi)];
    const rows = html.split(/<tr[^>]*>/gi);
    
    let processedCount = 0;
    
    for (const row of rows) {
      if (!row.includes('company_read') || processedCount >= 30) continue; // 최대 30개만
      
      // Extract NID
      const nidMatch = row.match(/company_read\.naver\?[^"']*?nid=(\d+)/i);
      if (!nidMatch) continue;
      const nid = nidMatch[1];
      
      // Extract title
      const titleMatch = row.match(/company_read\.naver[^"]*"[^>]*>\s*([\s\S]*?)\s*<\/a>/i);
      const title = titleMatch ? titleMatch[1].replace(/<[^>]*>/g, '').trim() : '';
      if (!title) continue;
      
      // Extract table data
      const tds = [];
      const tdRegex = /<td[^>]*>([\s\S]*?)<\/td>/gi;
      let m;
      while ((m = tdRegex.exec(row)) !== null) {
        tds.push(m[1].replace(/<[^>]*>/g, '').trim());
      }
      
      if (tds.length < 5) continue;
      
      // Basic info from list page
      const firm = tds[2] || 'Unknown';
      const date = parseDate(tds[4]);
      if (!date) continue;
      
      // PDF URL
      const pdfMatch = row.match(/href="(https?:\/\/[^"]*\.pdf[^"]*)"/i);
      const pdfUrl = pdfMatch ? pdfMatch[1] : null;
      
      console.log(`    Fetching detail for nid=${nid}...`);
      
      // Fetch detail page for target price, opinion, analyst
      const details = await fetchDetailPage(nid, ticker);
      
      // Random delay between requests (1.5-2.5 seconds)
      await sleep(1500 + Math.random() * 1000);
      
      if (title && date && firm) {
        reports.push({ 
          ticker, 
          firm, 
          analyst: details.analyst, 
          title, 
          target_price: details.targetPrice, 
          opinion: details.opinion || 'BUY', // 기본값 BUY
          published_at: date, 
          pdf_url: pdfUrl 
        });
        processedCount++;
      }
    }
    
    return reports;
  } catch (err) {
    console.log(`  [${ticker}] Error: ${err.message}`);
    return [];
  }
}

async function main() {
  console.log(`Crawling ${KR_TICKERS.length} tickers...`);
  const allReports = {};
  let count = 0;
  
  for (const ticker of KR_TICKERS) {
    if (count >= 20) break; // 최대 20개 티커만 처리
    
    console.log(`[${count+1}/${Math.min(KR_TICKERS.length,20)}] ${ticker}...`);
    const reports = await crawlTicker(ticker);
    console.log(`  → ${reports.length} reports`);
    
    if (reports.length > 0) {
      allReports[ticker] = reports;
    }
    
    count++;
    
    // Delay between tickers
    await sleep(2000 + Math.random() * 1000);
  }
  
  const outPath = path.join(__dirname, '..', 'data', 'analyst_reports.json');
  fs.writeFileSync(outPath, JSON.stringify(allReports, null, 2), 'utf-8');
  
  const total = Object.values(allReports).reduce((s, r) => s + r.length, 0);
  console.log(`\nDone! ${total} reports for ${Object.keys(allReports).length} tickers → ${outPath}`);
}

main().catch(console.error);