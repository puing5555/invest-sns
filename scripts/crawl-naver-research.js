/**
 * 네이버증권 리서치 크롤링 → JSON 파일 저장
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

function parseTargetPrice(text) {
  // 목표가는 보통 만원 단위 이상 (10,000원~)이고 "목표가" 키워드가 포함되거나
  // "원" 단위로 명시되어야 함. 단순 숫자는 조회수일 가능성이 높음
  if (!text.includes('목표') && !text.includes('원')) return null;
  
  const cleaned = text.replace(/,/g, '').replace(/원/g, '').trim();
  const num = parseInt(cleaned, 10);
  
  // 목표가는 최소 1만원 이상이어야 함 (조회수와 구분)
  if (isNaN(num) || num < 10000) return null;
  
  return num;
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
    
    // Split by <tr> and parse each row
    const rows = html.split(/<tr[^>]*>/gi);
    
    for (const row of rows) {
      if (!row.includes('company_read')) continue;
      
      // Extract title from link
      const titleMatch = row.match(/company_read\.naver[^"]*"[^>]*>\s*([\s\S]*?)\s*<\/a>/i);
      const title = titleMatch ? titleMatch[1].replace(/<[^>]*>/g, '').trim() : '';
      if (!title) continue;
      
      // Extract all td contents with proper indexing
      const tds = [];
      const tdRegex = /<td[^>]*>([\s\S]*?)<\/td>/gi;
      let m;
      while ((m = tdRegex.exec(row)) !== null) {
        tds.push(m[1].replace(/<[^>]*>/g, '').trim());
      }
      
      // Parse based on known table structure:
      // [0]: 종목명, [1]: 제목, [2]: 증권사, [3]: PDF링크, [4]: 날짜, [5]: 조회수
      let firm = '', date = null, targetPrice = null, opinion = 'BUY', analyst = null;
      
      if (tds.length >= 5) {
        // 증권사 (TD[2])
        firm = tds[2] || 'Unknown';
        
        // 날짜 (TD[4])  
        const d = parseDate(tds[4]);
        if (d) date = d;
        
        // 목표가는 일단 null로 설정 (네이버 리스트에서는 제공되지 않음)
        // PDF 내부를 파싱해야 실제 목표가를 얻을 수 있음
        targetPrice = null;
        
        // 애널리스트명도 네이버 리스트에서는 제공되지 않음
        analyst = null;
      }
      
      // Opinion detection from title and row content
      const rowLower = row.toLowerCase();
      const titleLower = title.toLowerCase();
      
      if (rowLower.includes('buy') || row.includes('매수') || 
          titleLower.includes('매수') || titleLower.includes('강력추천')) {
        opinion = 'BUY';
      } else if (rowLower.includes('hold') || row.includes('중립') || row.includes('보유') ||
                 titleLower.includes('중립') || titleLower.includes('보유')) {
        opinion = 'HOLD';  
      } else if (rowLower.includes('sell') || row.includes('매도') ||
                 titleLower.includes('매도')) {
        opinion = 'SELL';
      } else {
        // 기본값은 BUY (대부분 긍정적 리포트)
        opinion = 'BUY';
      }
      
      // PDF URL
      const pdfMatch = row.match(/href="(https?:\/\/[^"]*\.pdf[^"]*)"/i);
      const pdfUrl = pdfMatch ? pdfMatch[1] : null;
      
      if (title && date && firm) {
        reports.push({ 
          ticker, 
          firm, 
          analyst, 
          title, 
          target_price: targetPrice, 
          opinion, 
          published_at: date, 
          pdf_url: pdfUrl 
        });
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
    if (count >= 20) break;
    
    console.log(`[${count+1}/${Math.min(KR_TICKERS.length,20)}] ${ticker}...`);
    const reports = await crawlTicker(ticker);
    console.log(`  → ${reports.length} reports`);
    
    if (reports.length > 0) {
      allReports[ticker] = reports;
    }
    
    count++;
    await sleep(2000 + Math.random() * 1000);
  }
  
  const outPath = path.join(__dirname, '..', 'data', 'analyst_reports.json');
  fs.writeFileSync(outPath, JSON.stringify(allReports, null, 2), 'utf-8');
  
  const total = Object.values(allReports).reduce((s, r) => s + r.length, 0);
  console.log(`\nDone! ${total} reports for ${Object.keys(allReports).length} tickers → ${outPath}`);
}

main().catch(console.error);
