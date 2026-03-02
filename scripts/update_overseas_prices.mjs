// 해외 종목 시그널 가격 데이터 업데이트 스크립트 (Yahoo Finance 통합)
import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

// Yahoo Finance ticker 매핑
const YAHOO_MAP = {
  'BTC': 'BTC-USD', 'ETH': 'ETH-USD', 'SOL': 'SOL-USD', 'DOGE': 'DOGE-USD', 'KLAY': 'KLAY-USD',
  'NVDA': 'NVDA', 'TSLA': 'TSLA', 'PLTR': 'PLTR', 'AMD': 'AMD',
  'TSM': 'TSM', 'ASML': 'ASML', 'GOOGL': 'GOOGL', 'MSTR': 'MSTR',
  'RKLB': 'RKLB', 'SQ': 'SQ', 'RIOT': 'RIOT', 'GBTC': 'GBTC',
  'COIN': 'COIN', 'IREN': 'IREN', 'GME': 'GME', 'SOXX': 'SOXX',
  'MU': 'MU', 'KS11': '^KS11',
};

const headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' };

// 현재가 캐시
const currentCache = {};
async function getCurrentPrice(ticker) {
  const yt = YAHOO_MAP[ticker];
  if (!yt) return null;
  if (currentCache[ticker]) return currentCache[ticker];
  try {
    const r = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${yt}?range=1d&interval=1d`, { headers });
    const d = await r.json();
    const p = d.chart?.result?.[0]?.meta?.regularMarketPrice;
    if (p) currentCache[ticker] = p;
    return p || null;
  } catch { return null; }
}

// 과거가 캐시
const histCache = {};
async function getHistoricalPrice(ticker, dateStr) {
  const yt = YAHOO_MAP[ticker];
  if (!yt) return null;
  const key = `${ticker}_${dateStr}`;
  if (histCache[key]) return histCache[key];
  
  const date = new Date(dateStr);
  const p1 = Math.floor(date.getTime() / 1000) - 86400 * 2;
  const p2 = Math.floor(date.getTime() / 1000) + 86400 * 2;
  try {
    const r = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${yt}?period1=${p1}&period2=${p2}&interval=1d`, { headers });
    const d = await r.json();
    const closes = d.chart?.result?.[0]?.indicators?.quote?.[0]?.close?.filter(v => v != null);
    if (closes?.length) {
      // Pick the close nearest to the target date
      const timestamps = d.chart?.result?.[0]?.timestamp || [];
      const targetTs = date.getTime() / 1000;
      let bestIdx = 0, bestDiff = Infinity;
      timestamps.forEach((ts, i) => {
        const diff = Math.abs(ts - targetTs);
        if (diff < bestDiff) { bestDiff = diff; bestIdx = i; }
      });
      const price = d.chart?.result?.[0]?.indicators?.quote?.[0]?.close?.[bestIdx];
      if (price) { histCache[key] = price; return price; }
      histCache[key] = closes[0];
      return closes[0];
    }
    return null;
  } catch { return null; }
}

async function main() {
  console.log('📊 해외 종목 시그널 가격 데이터 업데이트 시작...');

  const { data: signals, error } = await supabase
    .from('influencer_signals')
    .select('id, ticker, signal, video_id, influencer_videos(published_at)');

  if (error) { console.error('Supabase 에러:', error); return; }
  console.log(`총 ${signals.length}개 시그널 조회됨`);

  const overseasSignals = signals.filter(s => s.ticker && /^[A-Z]+$/.test(s.ticker));
  console.log(`해외 종목 시그널: ${overseasSignals.length}개`);

  const pricesPath = path.join(__dirname, '..', 'data', 'signal_prices.json');
  let prices = {};
  try { prices = JSON.parse(fs.readFileSync(pricesPath, 'utf-8')); } catch {}

  let updated = 0, failed = 0;

  // Group by ticker to batch API calls
  const byTicker = {};
  overseasSignals.forEach(s => {
    if (!byTicker[s.ticker]) byTicker[s.ticker] = [];
    byTicker[s.ticker].push(s);
  });

  for (const [ticker, sigs] of Object.entries(byTicker)) {
    console.log(`\n🔍 ${ticker} (${sigs.length}개 시그널)`);
    
    const currPrice = await getCurrentPrice(ticker);
    if (!currPrice) {
      console.log(`  ❌ 현재가 조회 실패`);
      failed += sigs.length;
      continue;
    }
    console.log(`  현재가: $${currPrice.toFixed(2)}`);
    
    for (const signal of sigs) {
      const pubDate = signal.influencer_videos?.published_at;
      if (!pubDate) { failed++; continue; }
      
      const histPrice = await getHistoricalPrice(ticker, pubDate);
      await new Promise(r => setTimeout(r, 300));
      
      if (histPrice) {
        const returnPct = Math.round((currPrice - histPrice) / histPrice * 10000) / 100;
        prices[signal.id] = {
          price_at_signal: Math.round(histPrice * 100) / 100,
          price_current: Math.round(currPrice * 100) / 100,
          return_pct: returnPct,
        };
        updated++;
        console.log(`  ✅ ${pubDate.split('T')[0]}: $${histPrice.toFixed(2)} → $${currPrice.toFixed(2)} (${returnPct}%)`);
      } else {
        failed++;
        console.log(`  ❌ ${pubDate.split('T')[0]}: 과거가 조회 실패`);
      }
    }
  }

  fs.writeFileSync(pricesPath, JSON.stringify(prices, null, 2));
  console.log(`\n📊 완료: ${updated}개 업데이트, ${failed}개 실패`);
  console.log(`총 ${Object.keys(prices).length}개 시그널 가격 데이터`);
}

main().catch(console.error);
