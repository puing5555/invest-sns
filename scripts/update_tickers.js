const { createClient } = require('@supabase/supabase-js');
const s = createClient(
  'https://arypzhotxflimroprmdk.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
);

const TICKER_MAP = {
  '삼성전자': '005930', 'SK하이닉스': '000660', '현대차': '005380',
  'LG화학': '051910', '현대건설': '000720', '신세계': '004170',
  '효성중공업': '298040', '솔브레인': '357780', '삼성전기': '009150',
  'NC소프트': '036570', 'HD현대일렉트릭': '267260', '아이덴': '284620',
  '엔비디아': 'NVDA',
};

async function main() {
  for (const [stock, ticker] of Object.entries(TICKER_MAP)) {
    const { data, error } = await s
      .from('influencer_signals')
      .update({ ticker })
      .eq('stock', stock)
      .is('ticker', null);
    if (error) console.log(`ERROR ${stock}:`, error.message);
    else console.log(`Updated ${stock} → ${ticker}`);
  }
}
main();
