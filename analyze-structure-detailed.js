const fs = require('fs');

async function analyzeDetailedStructure() {
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
    
    console.log('=== DETAILED TABLE ANALYSIS ===');
    const rows = html.split(/<tr[^>]*>/gi);
    let sampleCount = 0;
    
    for (const row of rows) {
      if (!row.includes('company_read') || sampleCount >= 2) continue;
      
      console.log(`\n--- Sample ${sampleCount + 1} ---`);
      
      // 제목 추출
      const titleMatch = row.match(/company_read\.naver[^"]*"[^>]*>\s*([\s\S]*?)\s*<\/a>/i);
      const title = titleMatch ? titleMatch[1].replace(/<[^>]*>/g, '').trim() : '';
      console.log('Title:', title);
      
      // 모든 td 원본 HTML과 텍스트 추출
      const tdRegex = /<td[^>]*>([\s\S]*?)<\/td>/gi;
      let m;
      let tdIndex = 0;
      while ((m = tdRegex.exec(row)) !== null) {
        const rawHtml = m[1];
        const cleanText = rawHtml.replace(/<[^>]*>/g, '').trim();
        
        if (rawHtml || cleanText) {
          console.log(`TD[${tdIndex}]:`);
          console.log(`  Raw HTML: ${rawHtml.substring(0, 200)}`);
          console.log(`  Clean Text: "${cleanText}"`);
          
          // 숫자 패턴 체크
          const numbers = cleanText.match(/\d+/g);
          if (numbers) {
            console.log(`  Numbers found: ${numbers.join(', ')}`);
          }
          
          // 목표가 관련 키워드 체크
          if (cleanText.includes('목표') || cleanText.includes('원') || 
              /\d{1,3}(,\d{3})*원?/.test(cleanText)) {
            console.log(`  ** POTENTIAL TARGET PRICE **`);
          }
        }
        tdIndex++;
      }
      
      sampleCount++;
    }
    
  } catch (err) {
    console.error('Error:', err.message);
  }
}

analyzeDetailedStructure();