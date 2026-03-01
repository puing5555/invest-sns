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
  const cleaned = text.replace(/,/g, '').replace(/원/g, '').trim();
  const num = parseInt(cleaned, 10);
  return isNaN(num) ? null : num;
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
      
      // Extract all td contents
      const tds = [];
      const tdRegex = /<td[^>]*>([\s\S]*?)<\/td>/gi;
      let m;
      while ((m = tdRegex.exec(row)) !== null) {
        tds.push(m[1].replace(/<[^>]*>/g, '').trim());
      }
      
      let firm = '', date = null, targetPrice = null, opinion = 'BUY';
      
      for (const td of tds) {
        if (!firm && (td.includes('증권') || td.includes('투자') || td.includes('캐피탈') || 
            td.includes('리서치') || td.includes('파이낸셜') || td.includes('Securities') ||
            td.includes('자산운용') || td.includes('금융'))) {
          firm = td;
        }
        if (!date) {
          const d = parseDate(td);
          if (d) date = d;
        }
        const tp = parseTargetPrice(td);
        if (tp && tp > 500) targetPrice = tp;
      }
      
      // Opinion detection
      const rowLower = row.toLowerCase();
      if (rowLower.includes('buy') || row.includes('매수')) opinion = 'BUY';
      if (rowLower.includes('hold') || row.includes('중립') || rowLower.includes('neutral') || rowLower.includes('marketperform')) opinion = 'HOLD';
      if (rowLower.includes('sell') || row.includes('매도') || rowLower.includes('underperform')) opinion = 'SELL';
      
      // PDF URL
      const pdfMatch = row.match(/href="(https?:\/\/[^"]*\.pdf[^"]*)"/i);
      const pdfUrl = pdfMatch ? pdfMatch[1] : null;
      
      if (title && date) {
        reports.push({ ticker, firm: firm || 'Unknown', title, target_price: targetPrice, opinion, published_at: date, pdf_url: pdfUrl });
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
