const {createClient}=require('@supabase/supabase-js');
require('dotenv').config({path:'.env.local'});
const sb=createClient(process.env.NEXT_PUBLIC_SUPABASE_URL,process.env.SUPABASE_SERVICE_ROLE_KEY);

async function main(){
  const {data,error}=await sb.from('influencer_signals').select('id,stock,ticker,signal,reasoning,speaker_id,video_id').order('id');
  if(error){console.error(error);return;}
  console.log('Total signals:', data.length);
  
  // Suspicious stocks (person names, vague categories)
  const badKeywords = ['라울 팔','피델리티','프랑키','블랙베어드','권앰버핏','마이클버리','MrBeast','Airen'];
  const vagueStocks = ['현금','레버리지','배당주','금융주','국내 배당주','가상자산','리츠','부동산','금'];
  
  const suspicious = data.filter(s => 
    badKeywords.some(n => s.stock.includes(n)) ||
    s.stock.includes('관련 기업') || s.stock.includes('프로토콜') ||
    vagueStocks.includes(s.stock)
  );
  
  console.log('\nSuspicious stocks (' + suspicious.length + '):');
  suspicious.forEach(s => console.log(`  id=${s.id} | ${s.stock} | ${s.ticker||'no ticker'} | ${s.signal}`));
  
  // reasoning < 80 chars
  const shortR = data.filter(s => !s.reasoning || s.reasoning.length < 80);
  console.log('\nShort reasoning (<80):', shortR.length);
  
  // All unique stocks
  const stocks = [...new Set(data.map(s=>s.stock))].sort();
  console.log('\nUnique stocks (' + stocks.length + '):');
  stocks.forEach(s => console.log('  ' + s));
}
main();
