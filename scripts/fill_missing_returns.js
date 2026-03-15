/**
 * 수익률 누락 시그널 118개에 대해 가격 조회 + return_pct 계산 + DB UPDATE
 * - ticker가 있으면 signal_prices.json의 ticker 엔트리에서 current_price 사용
 * - published_at 기준 시점가는 yfinance 대안으로 signal_prices.json에서 조회
 * - 없으면 skip (null 유지)
 */
const fs = require('fs');
const https = require('https');

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

function supabaseRequest(method, path, body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, SUPABASE_URL);
    const options = {
      method,
      hostname: url.hostname,
      path: url.pathname + url.search,
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': method === 'PATCH' ? 'return=minimal' : 'count=exact',
      },
    };
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, data: data ? JSON.parse(data) : null, headers: res.headers });
        } catch {
          resolve({ status: res.statusCode, data, headers: res.headers });
        }
      });
    });
    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

async function main() {
  // Load signal_prices.json for ticker→current_price mapping
  const priceJson = JSON.parse(fs.readFileSync('public/signal_prices.json', 'utf-8'));
  
  // Build ticker→current_price map from non-UUID entries
  const tickerPrices = {};
  for (const [key, val] of Object.entries(priceJson)) {
    if (!key.includes('-') || key.length < 30) {
      tickerPrices[key] = val;
    }
  }
  
  // Also build UUID→price_data for fallback
  const signalPrices = {};
  for (const [key, val] of Object.entries(priceJson)) {
    if (key.includes('-') && key.length > 30) {
      signalPrices[key] = val;
    }
  }

  // Get all signals with null return_pct
  let offset = 0;
  let allMissing = [];
  while (true) {
    const resp = await supabaseRequest('GET', 
      `/rest/v1/influencer_signals?return_pct=is.null&select=id,stock,ticker,signal,created_at,influencer_videos(published_at)&order=created_at.desc&limit=100&offset=${offset}`
    );
    if (!resp.data || resp.data.length === 0) break;
    allMissing.push(...resp.data);
    if (resp.data.length < 100) break;
    offset += 100;
  }
  
  console.log(`Found ${allMissing.length} signals missing return_pct`);
  
  let updated = 0;
  let skipped = 0;
  let errors = [];
  
  for (const sig of allMissing) {
    // Skip 중립 signals
    if (sig.signal === '중립') {
      skipped++;
      continue;
    }
    
    const ticker = sig.ticker;
    if (!ticker) {
      skipped++;
      errors.push({ id: sig.id, stock: sig.stock, reason: 'no ticker' });
      continue;
    }
    
    // Get current price from ticker map
    const tickerData = tickerPrices[ticker];
    if (!tickerData || !tickerData.current_price) {
      skipped++;
      errors.push({ id: sig.id, stock: sig.stock, ticker, reason: 'no current_price in ticker map' });
      continue;
    }
    
    // For price_at_signal: check if there's already a UUID entry in the JSON
    let priceAtSignal = null;
    if (signalPrices[sig.id]) {
      priceAtSignal = signalPrices[sig.id].price_at_signal;
    }
    
    // If no price_at_signal from JSON, we can't calculate return - just set current price
    const priceCurrent = tickerData.current_price;
    
    if (priceAtSignal && priceCurrent) {
      const returnPct = Math.round(((priceCurrent - priceAtSignal) / priceAtSignal) * 10000) / 100;
      
      const patchResp = await supabaseRequest('PATCH',
        `/rest/v1/influencer_signals?id=eq.${sig.id}`,
        { price_at_signal: priceAtSignal, price_current: priceCurrent, return_pct: returnPct }
      );
      
      if (patchResp.status < 300) {
        updated++;
        console.log(`✅ ${sig.stock} (${ticker}): ${priceAtSignal} → ${priceCurrent} = ${returnPct}%`);
      } else {
        errors.push({ id: sig.id, stock: sig.stock, reason: `PATCH failed: ${patchResp.status}` });
      }
    } else {
      // Set just current price, no return calc possible
      const patchResp = await supabaseRequest('PATCH',
        `/rest/v1/influencer_signals?id=eq.${sig.id}`,
        { price_current: priceCurrent }
      );
      skipped++;
      errors.push({ id: sig.id, stock: sig.stock, ticker, reason: 'no price_at_signal' });
    }
    
    // Rate limit: 50ms between requests
    await new Promise(r => setTimeout(r, 50));
  }
  
  console.log(`\n=== Summary ===`);
  console.log(`Total missing: ${allMissing.length}`);
  console.log(`Updated with return_pct: ${updated}`);
  console.log(`Skipped: ${skipped}`);
  if (errors.length > 0) {
    console.log(`\nErrors/Skips:`);
    errors.forEach(e => console.log(`  ${e.stock || '?'} (${e.ticker || '?'}): ${e.reason}`));
  }
}

main().catch(console.error);
