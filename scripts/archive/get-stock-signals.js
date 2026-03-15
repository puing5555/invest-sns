/**
 * 종목별 시그널 데이터 추출 함수
 */
const fs = require('fs');

// 종목별 시그널 추출 함수를 JS로 구현
function getStockSignalsForCode(stockCode, stockName) {
  // 인플루언서 데이터에서 해당 종목의 시그널 찾기
  const influencerData = JSON.parse(fs.readFileSync('./data/influencerData.ts', 'utf-8'));
  
  // TypeScript 파일에서 데이터 추출 (influencers 배열)
  const dataMatch = influencerData.match(/export const influencers: Influencer\[\] = (\[[\s\S]*?\]);/);
  if (!dataMatch) {
    console.log('인플루언서 데이터를 찾을 수 없습니다');
    return [];
  }

  const influencers = JSON.parse(dataMatch[1]);
  
  // 종목 이름 매핑
  const stockMapping = {
    '005930': ['삼성전자', '삼성'],
    '000660': ['SK하이닉스', 'SK하이닉스', '하이닉스'],
    '035420': ['네이버', 'NAVER'],
    '051910': ['LG화학', 'LG화학'],
    '005380': ['현대차', '현대자동차'],
    '005490': ['POSCO홀딩스', '포스코'],
    'BTC': ['비트코인', 'Bitcoin'],
    'ETH': ['이더리움', 'Ethereum']
  };

  const possibleNames = stockMapping[stockCode] || [stockName];
  
  // 해당 종목의 시그널 찾기
  const signals = [];
  
  influencers.forEach(influencer => {
    influencer.recentCalls.forEach(call => {
      // 종목명 매칭 (부분 문자열 포함)
      const isMatch = possibleNames.some(name => 
        call.stock.includes(name) || name.includes(call.stock)
      );
      
      if (isMatch) {
        signals.push({
          id: `${influencer.id}-${call.stock}`,
          stock: call.stock,
          signal_type: call.direction,
          speaker: influencer.name,
          content_snippet: `${call.stock} ${call.direction} 추천`,
          date: call.date,
          accuracy_rate: influencer.accuracy,
          return_rate: call.returnRate,
          status: call.status,
          callPrice: call.callPrice,
          currentPrice: call.currentPrice
        });
      }
    });
  });

  return signals;
}

// 테스트용
const signals = getStockSignalsForCode('005930', '삼성전자');
console.log(`삼성전자 시그널 ${signals.length}개 발견:`);
signals.forEach(signal => {
  console.log(`  - ${signal.speaker}: ${signal.signal_type} (${signal.date})`);
});

module.exports = { getStockSignalsForCode };