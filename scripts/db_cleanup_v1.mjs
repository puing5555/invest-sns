// db_cleanup_v1.mjs - DB 정리 스크립트
// 작업 1: 잘못된 시그널 삭제, 작업 2: 추가 정리

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

const headers = {
  'apikey': SUPABASE_KEY,
  'Authorization': `Bearer ${SUPABASE_KEY}`,
  'Content-Type': 'application/json',
  'Prefer': 'return=minimal'
};

async function supabaseDelete(filter) {
  const url = `${SUPABASE_URL}/rest/v1/influencer_signals?${filter}`;
  const res = await fetch(url, { method: 'DELETE', headers });
  if (!res.ok) throw new Error(`DELETE failed: ${res.status} ${await res.text()}`);
  return res;
}

async function supabasePatch(filter, body) {
  const url = `${SUPABASE_URL}/rest/v1/influencer_signals?${filter}`;
  const res = await fetch(url, { method: 'PATCH', headers, body: JSON.stringify(body) });
  if (!res.ok) throw new Error(`PATCH failed: ${res.status} ${await res.text()}`);
  return res;
}

async function supabaseGet(select, filter = '') {
  const url = `${SUPABASE_URL}/rest/v1/influencer_signals?select=${select}${filter ? '&' + filter : ''}`;
  const res = await fetch(url, { headers: { 'apikey': SUPABASE_KEY, 'Authorization': `Bearer ${SUPABASE_KEY}` } });
  if (!res.ok) throw new Error(`GET failed: ${res.status} ${await res.text()}`);
  return res.json();
}

async function main() {
  console.log('=== 작업 1: 잘못된 시그널 23개 삭제 ===');
  
  const idsToDelete = [
    '8d2f77b1', 'ddfdd2be', '0677feb9', '4e4fa2e2', '9fdc229d', '9a53dd26', 'e9dd9043',
    '239ebae9', 'cd61cc91', 'c140ce9c', 'f902ccc3', '1aa6d95d', '76f45ef5', '3bf35ea8',
    'a1c13310', 'b17cd1fb', '35df36b0',
    '67eebb6f', 'd7747984', 'eaf6db56', 'dd2bbc57',
    '4e9a038d', 'c78cc714'
  ];
  
  // Fetch all to match partial IDs
  const allData = await supabaseGet('id,stock');
  let deleteCount = 0;
  for (const partialId of idsToDelete) {
    const matches = allData.filter(r => r.id.startsWith(partialId));
    if (matches.length === 0) {
      console.log(`  ⚠️ ${partialId}: 찾을 수 없음`);
      continue;
    }
    for (const row of matches) {
      await supabaseDelete(`id=eq.${row.id}`);
      console.log(`  ✅ 삭제: ${row.id.substring(0,8)} (${row.stock})`);
      deleteCount++;
    }
  }
  console.log(`  총 ${deleteCount}개 삭제`);
  
  console.log('\n=== 작업 2: 추가 정리 ===');
  
  // stock="없음" 삭제
  let data = await supabaseGet('id,stock', 'stock=eq.없음');
  console.log(`  없음: ${data.length}개 발견`);
  if (data.length > 0) {
    await supabaseDelete('stock=eq.없음');
    console.log('  ✅ 삭제 완료');
  }
  
  // stock="N/A" 삭제
  data = await supabaseGet('id,stock', 'stock=eq.N/A');
  console.log(`  N/A: ${data.length}개 발견`);
  if (data.length > 0) {
    await supabaseDelete('stock=eq.N/A');
    console.log('  ✅ 삭제 완료');
  }
  
  // 팔라티어 → 팔란티어
  data = await supabaseGet('id', 'stock=eq.팔라티어');
  console.log(`  팔라티어: ${data.length}개 발견`);
  if (data.length > 0) {
    await supabasePatch('stock=eq.팔라티어', { stock: '팔란티어' });
    console.log('  ✅ 팔란티어로 수정');
  }
  
  // 마이크로스트라이즈 → 마이크로스트래티지
  data = await supabaseGet('id', 'stock=eq.마이크로스트라이즈');
  console.log(`  마이크로스트라이즈: ${data.length}개 발견`);
  if (data.length > 0) {
    await supabasePatch('stock=eq.마이크로스트라이즈', { stock: '마이크로스트래티지', ticker: 'MSTR' });
    console.log('  ✅ 마이크로스트래티지/MSTR로 수정');
  }
  
  // Rocket Lab → 로켓랩
  data = await supabaseGet('id', 'stock=eq.Rocket Lab');
  console.log(`  Rocket Lab: ${data.length}개 발견`);
  if (data.length > 0) {
    await supabasePatch('stock=eq.Rocket Lab', { stock: '로켓랩', ticker: 'RKLB' });
    console.log('  ✅ 로켓랩/RKLB로 수정');
  }
  
  // 로켓랩 ticker 통일
  data = await supabaseGet('id,ticker', 'stock=eq.로켓랩');
  const noTicker = data.filter(d => !d.ticker || d.ticker !== 'RKLB');
  if (noTicker.length > 0) {
    await supabasePatch('stock=eq.로켓랩', { ticker: 'RKLB' });
    console.log(`  ✅ 로켓랩 ticker RKLB 통일 (${noTicker.length}개)`);
  }
  
  // 스톤리지 확인
  data = await supabaseGet('id,stock,ticker,key_quote', 'stock=eq.스톤리지');
  console.log(`  스톤리지: ${data.length}개 발견`);
  if (data.length > 0) {
    for (const d of data) {
      console.log(`    - ${(d.key_quote || '').substring(0, 100)}`);
      console.log(`      ticker: ${d.ticker}`);
    }
    // Stoneridge Inc (SRI) is a real company - auto electronics
    // But "스토니리지" doesn't match. Let's check if ticker exists
    if (data[0].ticker) {
      console.log('  → ticker 있음, 유지');
    } else {
      console.log('  → 모호함, 삭제');
      await supabaseDelete('stock=eq.스톤리지');
      console.log('  ✅ 삭제 완료');
    }
  }
  
  console.log('\n=== 현재 DB 상태 확인 ===');
  const allSignals = await supabaseGet('id,stock,ticker', '');
  console.log(`총 시그널 수: ${allSignals.length}`);
  
  const uniqueStocks = [...new Set(allSignals.map(s => s.stock))].sort();
  console.log(`고유 종목 수: ${uniqueStocks.length}`);
  console.log('종목 목록:');
  for (const s of uniqueStocks) {
    const tickers = [...new Set(allSignals.filter(x => x.stock === s).map(x => x.ticker).filter(Boolean))];
    console.log(`  ${s} (${tickers.join(', ') || 'no ticker'})`);
  }
}

main().catch(console.error);
