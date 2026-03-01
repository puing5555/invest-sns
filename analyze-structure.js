const fs = require('fs');

async function analyzeNaverStructure() {
  const url = 'https://finance.naver.com/research/company_list.naver?searchType=itemCode&itemCode=005930&page=1';
  
  try {
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9',
      }
    });
    
    const buffer = await response.arrayBuffer();
    const html = new TextDecoder('euc-kr').decode(new Uint8Array(buffer));
    
    // 테이블 헤더 찾기
    const headerMatch = html.match(/<table[^>]*class="type_1"[^>]*>([\s\S]*?)<\/table>/i);
    if (headerMatch) {
      console.log('=== TABLE HEADER ===');
      const theadMatch = headerMatch[1].match(/<thead[^>]*>([\s\S]*?)<\/thead>/i);
      if (theadMatch) {
        const headerRow = theadMatch[1];
        const thRegex = /<th[^>]*>([\s\S]*?)<\/th>/gi;
        let m;
        let colIndex = 0;
        while ((m = thRegex.exec(headerRow)) !== null) {
          const headerText = m[1].replace(/<[^>]*>/g, '').trim();
          console.log(`Column ${colIndex}: "${headerText}"`);
          colIndex++;
        }
      }
    }
    
    console.log('\n=== SAMPLE ROWS ===');
    const rows = html.split(/<tr[^>]*>/gi);
    let sampleCount = 0;
    
    for (const row of rows) {
      if (!row.includes('company_read') || sampleCount >= 3) continue;
      
      console.log(`\n--- Sample ${sampleCount + 1} ---`);
      
      // 제목 추출
      const titleMatch = row.match(/company_read\.naver[^"]*"[^>]*>\s*([\s\S]*?)\s*<\/a>/i);
      const title = titleMatch ? titleMatch[1].replace(/<[^>]*>/g, '').trim() : '';
      console.log('Title:', title);
      
      // 모든 td 내용 추출
      const tds = [];
      const tdRegex = /<td[^>]*>([\s\S]*?)<\/td>/gi;
      let m;
      while ((m = tdRegex.exec(row)) !== null) {
        const content = m[1].replace(/<[^>]*>/g, '').trim();
        tds.push(content);
      }
      
      console.log('TD Contents:');
      tds.forEach((td, i) => {
        if (td) console.log(`  [${i}]: "${td.substring(0, 100)}"`);
      });
      
      sampleCount++;
    }
    
  } catch (err) {
    console.error('Error:', err.message);
  }
}

analyzeNaverStructure();