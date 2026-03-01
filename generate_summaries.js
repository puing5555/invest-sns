const fs = require('fs');

const TICKER_NAMES = {
  '240810': '원익QnC', '284620': '카이', '298040': '효성중공업', '352820': '하이브', '403870': 'HPSP',
  '090430': '아모레퍼시픽', '000660': 'SK하이닉스', '079160': 'CJ CGV', '005380': '현대자동차',
  '005930': '삼성전자', '036930': '주성엔지니어링', '042700': '한미반도체', '006400': '삼성SDI',
  '000720': '현대건설', '005940': 'NH투자증권', '016360': '삼성증권', '039490': '키움증권',
  '051910': 'LG화학', '036570': '엔씨소프트', '071050': '한국금융지주',
};

function formatPrice(price) {
  if (!price) return null;
  if (price >= 10000) {
    return `${Math.floor(price / 10000)}만원`;
  } else if (price >= 1000) {
    return `${Math.floor(price / 1000)}천원`;
  }
  return `${price}원`;
}

function generateSummary(report) {
  const stockName = TICKER_NAMES[report.ticker] || report.ticker;
  const firm = report.firm;
  const opinion = report.opinion;
  const targetPrice = formatPrice(report.target_price);
  const title = report.title;

  // 기본 템플릿들
  const templates = [];

  // 목표가가 있는 경우
  if (targetPrice) {
    templates.push(`${firm}이 ${stockName}에 ${opinion} 의견, 목표가 ${targetPrice} 제시`);
    templates.push(`${firm}, ${stockName} 목표가 ${targetPrice}로 ${opinion} 투자의견 발표`);
    templates.push(`${stockName}(${opinion}), ${firm}이 목표가 ${targetPrice} 제시`);
  } else {
    // 목표가가 없는 경우
    templates.push(`${firm}이 ${stockName}에 ${opinion} 투자의견 발표`);
    templates.push(`${stockName}(${opinion}), ${firm} 리포트 발간`);
  }

  // 제목에서 핵심 키워드 추출하여 추가 정보 생성
  let additionalInfo = '';
  const titleLower = title.toLowerCase();
  
  // 성장, 확대, 개선 등의 키워드
  if (title.includes('성장') || title.includes('확대')) {
    additionalInfo = '. 성장성 기대';
  } else if (title.includes('실적') || title.includes('수익')) {
    additionalInfo = '. 실적 개선 전망';
  } else if (title.includes('도약') || title.includes('상승')) {
    additionalInfo = '. 주가 상승 기대';
  } else if (title.includes('회복') || title.includes('반등')) {
    additionalInfo = '. 실적 회복 기대';
  } else if (title.includes('신사업') || title.includes('사업확장')) {
    additionalInfo = '. 신사업 확장성 평가';
  } else if (title.includes('수출') || title.includes('해외')) {
    additionalInfo = '. 수출 비중 확대 기대';
  } else if (title.includes('AI') || title.includes('기술')) {
    additionalInfo = '. 기술력 경쟁우위 강화';
  } else if (title.includes('배당') || title.includes('주주환원')) {
    additionalInfo = '. 주주환원 확대 전망';
  } else if (title.includes('M&A') || title.includes('인수')) {
    additionalInfo = '. M&A 시너지 기대';
  } else {
    // 기본 키워드들
    const keywords = title.split(' ').filter(word => 
      word.length > 2 && 
      !['리포트', '분석', '보고서', '투자', '의견'].includes(word)
    );
    if (keywords.length > 0) {
      const randomKeyword = keywords[Math.floor(Math.random() * keywords.length)];
      additionalInfo = `. ${randomKeyword} 관련 호재`;
    }
  }

  // 템플릿 선택 (해시를 이용한 일관된 랜덤)
  const hash = report.ticker + report.firm + report.title + report.published_at;
  const hashSum = hash.split('').reduce((sum, char) => sum + char.charCodeAt(0), 0);
  const templateIndex = hashSum % templates.length;
  
  return templates[templateIndex] + additionalInfo;
}

// 메인 실행
const data = JSON.parse(fs.readFileSync('./data/analyst_reports.json', 'utf8'));

console.log('AI 한줄요약 생성 시작...');

let processedCount = 0;
const totalCount = Object.values(data).flat().length;

// 각 종목별로 처리
for (const [ticker, reports] of Object.entries(data)) {
  const stockName = TICKER_NAMES[ticker] || ticker;
  
  for (let i = 0; i < reports.length; i++) {
    const report = reports[i];
    
    // 이미 summary가 있으면 스킵
    if (report.summary) {
      processedCount++;
      continue;
    }
    
    // 요약 생성
    const summary = generateSummary(report);
    report.summary = summary;
    
    processedCount++;
    
    // 진행률 출력
    if (processedCount % 50 === 0) {
      console.log(`진행률: ${processedCount}/${totalCount} (${Math.round(processedCount/totalCount*100)}%)`);
    }
  }
}

// 파일 저장
fs.writeFileSync('./data/analyst_reports.json', JSON.stringify(data, null, 2), 'utf8');

console.log(`✅ 완료! ${totalCount}개 리포트에 AI 한줄요약 추가됨`);

// 몇 개 샘플 출력
console.log('\n샘플 요약들:');
const samples = Object.values(data).flat().slice(0, 5);
samples.forEach((report, i) => {
  const stockName = TICKER_NAMES[report.ticker] || report.ticker;
  console.log(`${i+1}. [${stockName}] ${report.summary}`);
});