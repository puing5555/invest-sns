// update_prices_and_pages_v1.mjs
// 작업 3: signal_prices.json 업데이트
// 작업 4: generateStaticParams에 해외 ticker 포함

import { readFileSync, writeFileSync } from 'fs';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

// Known ticker mappings for stocks without tickers in DB
const TICKER_MAP = {
  '비트코인': 'BTC-USD',
  '이더리움': 'ETH-USD',
  '솔라나': 'SOL-USD',
  '도지코인': 'DOGE-USD',
  '네이버': '035420.KS',
  'SpaceX': null, // private
  '코인베이스': 'COIN',
  '게임스톱': 'GME',
  '구글(알파벳)': 'GOOGL',
  '팔란티어': 'PLTR',
  '엔비디아': 'NVDA',
  '테슬라': 'TSLA',
  'TSMC': 'TSM',
  'AMD': 'AMD',
  'ASML': 'ASML',
  '마이크론': 'MU',
  '마이크로스트래티지': 'MSTR',
  '로켓랩': 'RKLB',
  'SOXX': 'SOXX',
  'IREN': 'IREN',
  'Riot Blockchain': 'RIOT',
  '스퀘어': 'SQ',
  '서클': null, // private
  '그레이스케일 비트코인 투자 신탁': 'GBTC',
  '클레이튼': 'KLAY-USD',
  // Categories/sectors - no ticker
  'AI 에이전트': null,
  'AI 인프라 섹터': null,
  'CRYPTO': null,
  'DeFi': null,
  'NFT': null,
  'SMR/원전': null,
  '로봇 섹터': null,
  '반도체': null,
  '반도체 섹터': null,
  '빅테크': null,
  '바이오 AI 기업': null,
  '소프트웨어 섹터': null,
  '스테이블코인': null,
  '자신의 포트폴리오': null,
  '조선': null,
  '테크 기업': null,
  '현대차그룹주': null,
  'HCM파마': null,
  'HM파마': null,
};

async function fetchYahooPrice(ticker) {
  try {
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(ticker)}?range=1d&interval=1d`;
    const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
    if (!res.ok) return null;
    const data = await res.json();
    const meta = data.chart?.result?.[0]?.meta;
    if (!meta) return null;
    return meta.regularMarketPrice || meta.previousClose;
  } catch {
    return null;
  }
}

async function main() {
  // Get all signals from DB
  const res = await fetch(`${SUPABASE_URL}/rest/v1/influencer_signals?select=id,stock,ticker,created_at`, {
    headers: { 'apikey': SUPABASE_KEY, 'Authorization': `Bearer ${SUPABASE_KEY}` }
  });
  const signals = await res.json();
  
  // Load existing prices
  const pricesPath = 'data/signal_prices.json';
  const existingPrices = JSON.parse(readFileSync(pricesPath, 'utf8'));
  
  // Find signals without price data
  const missingPrices = signals.filter(s => !existingPrices[s.id]);
  console.log(`총 시그널: ${signals.length}, 가격 없는 시그널: ${missingPrices.length}`);
  
  // Group missing by stock to batch price lookups
  const stockGroups = {};
  for (const s of missingPrices) {
    if (!stockGroups[s.stock]) stockGroups[s.stock] = [];
    stockGroups[s.stock].push(s);
  }
  
  console.log('가격 없는 종목들:', Object.keys(stockGroups).join(', '));
  
  // Also update DB tickers where missing
  const headersAuth = {
    'apikey': SUPABASE_KEY,
    'Authorization': `Bearer ${SUPABASE_KEY}`,
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
  };
  
  // Update missing tickers in DB
  for (const s of signals) {
    if (!s.ticker && TICKER_MAP[s.stock] !== undefined && TICKER_MAP[s.stock] !== null) {
      const yahooTicker = TICKER_MAP[s.stock];
      // Convert Yahoo ticker to display ticker
      let displayTicker = yahooTicker.replace('-USD', '').replace('.KS', '');
      if (s.stock === '네이버') displayTicker = '035420';
      
      await fetch(`${SUPABASE_URL}/rest/v1/influencer_signals?id=eq.${s.id}`, {
        method: 'PATCH',
        headers: headersAuth,
        body: JSON.stringify({ ticker: displayTicker })
      });
      console.log(`  DB ticker 업데이트: ${s.stock} → ${displayTicker}`);
    }
  }
  
  // Fetch prices for missing signals
  const tickerPriceCache = {};
  for (const [stock, sigs] of Object.entries(stockGroups)) {
    let yahooTicker = null;
    
    // Determine Yahoo ticker
    if (sigs[0].ticker) {
      // Check if Korean (6-digit)
      if (/^\d{6}$/.test(sigs[0].ticker)) {
        yahooTicker = sigs[0].ticker + '.KS';
      } else if (['BTC', 'ETH', 'SOL', 'DOGE', 'KLAY'].includes(sigs[0].ticker)) {
        yahooTicker = sigs[0].ticker + '-USD';
      } else {
        yahooTicker = sigs[0].ticker;
      }
    } else if (TICKER_MAP[stock]) {
      yahooTicker = TICKER_MAP[stock];
    }
    
    if (!yahooTicker) {
      console.log(`  ⏭️ ${stock}: ticker 없음 (카테고리/비상장), 스킵`);
      continue;
    }
    
    if (!(yahooTicker in tickerPriceCache)) {
      const price = await fetchYahooPrice(yahooTicker);
      tickerPriceCache[yahooTicker] = price;
      if (price) {
        console.log(`  💰 ${stock} (${yahooTicker}): $${price}`);
      } else {
        console.log(`  ❌ ${stock} (${yahooTicker}): 가격 조회 실패`);
      }
    }
    
    const currentPrice = tickerPriceCache[yahooTicker];
    if (currentPrice) {
      for (const sig of sigs) {
        existingPrices[sig.id] = {
          price_at_signal: currentPrice,
          price_current: currentPrice,
          return_pct: 0
        };
      }
    }
  }
  
  // Write updated prices
  writeFileSync(pricesPath, JSON.stringify(existingPrices, null, 2));
  console.log(`\n✅ signal_prices.json 업데이트 완료 (${Object.keys(existingPrices).length}개 엔트리)`);
  
  // 작업 4: Check generateStaticParams
  // Get all unique tickers for stock pages
  const allTickers = [...new Set(signals.map(s => s.ticker).filter(Boolean))];
  const koreanTickers = allTickers.filter(t => /^\d{6}$/.test(t));
  const globalTickers = allTickers.filter(t => !/^\d{6}$/.test(t));
  
  console.log(`\n=== 종목 페이지 ===`);
  console.log(`한국 종목 코드: ${koreanTickers.length}개`);
  console.log(`해외/코인 ticker: ${globalTickers.length}개 - ${globalTickers.join(', ')}`);
}

main().catch(console.error);
