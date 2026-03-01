const {createClient} = require('@supabase/supabase-js');
const fs = require('fs');
const {execSync} = require('child_process');

const sb = createClient(
  'https://arypzhotxflimroprmdk.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
);

// Manual ticker mapping for sector/generic signals
const MANUAL_MAP = {
  '78b3f927-0ecb-49a7-93df-2dea1ea4d630': { ticker: 'QQQ', note: '테크 기업 → QQQ' },
  'e33133c1-cd42-4a51-975e-f092c50f3f46': { ticker: 'SOXX', note: '반도체 → SOXX' },
  'bac042bc-8a78-4397-ab71-ba1755fc3d79': { ticker: '010140.KS', note: '조선 → 한국조선해양(HD한국조선해양)' },
  'fee2af81-2e4b-4d1b-a31b-6c194e482b74': { ticker: 'SOXX', note: '반도체 → SOXX' },
  '87f3fa04-503b-4cb5-9000-ee39bd0ce907': { ticker: 'QQQ', note: '빅테크 → QQQ' },
  '9aeda838-cd78-49c4-afe0-779fe6924305': { ticker: 'ARKG', note: '바이오 AI 기업 → ARKG' },
  '0b1207d3-8144-4e27-b5b6-adad57709e27': { ticker: null, note: 'HM파마 - 비상장/찾을수없음' },
  'dd2bbc57-c6ed-4168-b84a-305e0b832e7f': { ticker: '373220.KS', note: '2차전지 → LG에너지솔루션' },
  '332a5809-ad05-4697-89f2-1a8e2f6cb359': { ticker: '009830.KS', note: 'SMR/원전 → 한화솔루션' },
  '720aef52-2d6a-45f1-b8bd-b888a96813ae': { ticker: 'IGV', note: '소프트웨어 섹터 → IGV' },
  'f6d397de-1c5d-47f3-bf75-02abc2f3e8f4': { ticker: 'NVDA', note: 'AI 인프라 섹터 → NVDA' },
  '9d79c0a4-7e2a-4852-b303-b24f05a980fd': { ticker: '005380.KS', note: '현대차그룹주 → 현대차' },
  '90524688-c8f2-4640-9614-61f79ec3ce58': { ticker: null, note: 'HCM파마 - 비상장/찾을수없음' },
  '2d5d8a4b-a6e1-425a-98f5-8767a142193e': { ticker: '454910.KS', note: '로봇 섹터 → 레인보우로보틱스' },
};

// Ticker conversion for yfinance
function toYFinanceTicker(ticker) {
  if (!ticker) return null;
  // Already has suffix or is US ticker
  if (ticker.includes('.') || /^[A-Z]+$/.test(ticker)) return ticker;
  // Korean 6-digit code
  if (/^\d{6}$/.test(ticker)) return ticker + '.KS';
  // Index
  if (ticker === 'KS11') return '^KS11';
  return ticker;
}

async function main() {
  const {data} = await sb.from('influencer_signals').select('id,stock,ticker,created_at');
  const prices = JSON.parse(fs.readFileSync('data/signal_prices.json', 'utf8'));
  const covered = new Set(Object.keys(prices));
  const missing = data.filter(d => !covered.has(d.id));
  
  console.log(`Missing ${missing.length} signals from prices`);
  
  // Build list of (signal_id, yfinance_ticker, date) to fetch
  const toFetch = [];
  for (const m of missing) {
    let ticker = m.ticker;
    const manual = MANUAL_MAP[m.id];
    if (manual) {
      ticker = manual.ticker;
      if (!ticker) {
        console.log(`SKIP: ${m.stock} - ${manual.note}`);
        continue;
      }
    }
    if (!ticker) {
      console.log(`SKIP: ${m.stock} - no ticker`);
      continue;
    }
    const yfTicker = toYFinanceTicker(ticker);
    const date = m.created_at.slice(0, 10);
    toFetch.push({ id: m.id, stock: m.stock, ticker: yfTicker, date });
  }
  
  console.log(`\nFetching prices for ${toFetch.length} signals...`);
  
  // Build python script to fetch all at once
  const tickers = [...new Set(toFetch.map(t => t.ticker))];
  const pyScript = `
import yfinance as yf
import json
import sys

tickers = ${JSON.stringify(tickers)}
result = {}
for t in tickers:
    try:
        stock = yf.Ticker(t)
        hist = stock.history(period='5d')
        if len(hist) > 0:
            result[t] = {
                'current': round(float(hist.iloc[-1]['Close']), 2),
                'prices': {str(d.date()): round(float(r['Close']), 2) for d, r in hist.iterrows()}
            }
            print(f"OK {t}: {result[t]['current']}", file=sys.stderr)
        else:
            print(f"NO DATA {t}", file=sys.stderr)
    except Exception as e:
        print(f"ERROR {t}: {e}", file=sys.stderr)

print(json.dumps(result))
`;
  
  fs.writeFileSync('scripts/_fetch_prices.py', pyScript);
  
  let priceData;
  try {
    const out = execSync('python scripts/_fetch_prices.py', { 
      timeout: 60000, 
      encoding: 'utf8',
      cwd: process.cwd()
    });
    priceData = JSON.parse(out.trim());
  } catch(e) {
    console.error('Python error:', e.stderr || e.message);
    return;
  }
  
  console.log(`\nGot price data for ${Object.keys(priceData).length} tickers`);
  
  // Now build price entries
  let added = 0;
  for (const item of toFetch) {
    const pd = priceData[item.ticker];
    if (!pd) {
      console.log(`NO PRICE: ${item.stock} (${item.ticker})`);
      continue;
    }
    
    // Find signal date price (or closest)
    let signalPrice = pd.prices[item.date];
    if (!signalPrice) {
      // Try nearby dates
      const dates = Object.keys(pd.prices).sort();
      const closest = dates.reduce((prev, curr) => 
        Math.abs(new Date(curr) - new Date(item.date)) < Math.abs(new Date(prev) - new Date(item.date)) ? curr : prev
      );
      signalPrice = pd.prices[closest];
    }
    
    prices[item.id] = {
      price_at_signal: signalPrice,
      price_current: pd.current,
      return_pct: parseFloat(((pd.current - signalPrice) / signalPrice * 100).toFixed(2))
    };
    console.log(`ADDED: ${item.stock} (${item.ticker}) signal=${signalPrice} current=${pd.current} return=${prices[item.id].return_pct}%`);
    added++;
  }
  
  fs.writeFileSync('data/signal_prices.json', JSON.stringify(prices, null, 2));
  console.log(`\nDone! Added ${added} entries. Total: ${Object.keys(prices).length}`);
  
  // Clean up
  fs.unlinkSync('scripts/_fetch_prices.py');
}

main().catch(console.error);
