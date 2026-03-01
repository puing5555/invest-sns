const {createClient} = require('@supabase/supabase-js');
const fs = require('fs');

const sb = createClient(
  'https://arypzhotxflimroprmdk.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
);

(async()=>{
  const {data,error} = await sb.from('influencer_signals').select('id,stock,ticker,created_at');
  if(error){console.log('ERROR',error);return;}
  console.log('Total signals:', data.length);
  
  const prices = JSON.parse(fs.readFileSync('data/signal_prices.json','utf8'));
  const covered = new Set(Object.keys(prices));
  console.log('Covered:', covered.size);
  
  const missing = data.filter(d=>!covered.has(d.id));
  console.log('Missing:', missing.length);
  missing.forEach(m=>console.log('  '+m.id.slice(0,8)+'.. | '+m.stock+' | '+m.ticker+' | '+m.created_at.slice(0,10)));
  
  // Also check covered ones that might have issues (no signal_price or current_price = 0)
  let badData = 0;
  for(const [id, p] of Object.entries(prices)) {
    if(!p.signal_price || p.signal_price === 0) badData++;
  }
  console.log('\nCovered but signal_price=0 or null:', badData);
  
  // unique tickers
  const tickers = {};
  data.forEach(d=>{if(d.ticker) tickers[d.ticker]=d.stock;});
  console.log('\nUnique tickers ('+Object.keys(tickers).length+'):');
  Object.keys(tickers).sort().forEach(t=>console.log('  '+t+' -> '+tickers[t]));
})();
