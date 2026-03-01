const {createClient}=require('@supabase/supabase-js');const fs=require('fs');
const env=fs.readFileSync('.env.local','utf8');const vars={};
env.split('\n').forEach(l=>{const [k,...v]=l.split('=');if(k)vars[k.trim()]=v.join('=').trim()});
const sb=createClient(vars.NEXT_PUBLIC_SUPABASE_URL,vars.NEXT_PUBLIC_SUPABASE_ANON_KEY);
(async()=>{
  // 엔비디아 시그널 전부
  const {data:nv}=await sb.from('influencer_signals').select('id,stock,signal,key_quote,speakers(name)').ilike('stock','%엔비디아%');
  console.log('=== 엔비디아 시그널 ('+nv.length+'개) ===');
  nv.forEach(s=>console.log(s.signal+' | '+s.speakers?.name+' | key_quote:['+(s.key_quote?s.key_quote.substring(0,40):'NULL')+']'));
  
  // 삼성전자 매수 시그널
  const {data:ss}=await sb.from('influencer_signals').select('id,stock,signal,key_quote,speakers(name)').eq('stock','삼성전자').eq('signal','매수');
  console.log('\n=== 삼성전자 매수 ('+ss.length+'개) ===');
  ss.forEach(s=>console.log(s.speakers?.name+' | key_quote:['+(s.key_quote?s.key_quote.substring(0,50):'NULL')+']'));
  
  // 전체 시그널 중 key_quote가 NULL인 것
  const {data:all}=await sb.from('influencer_signals').select('id,stock,signal,key_quote,speakers(name)').is('key_quote',null);
  console.log('\n=== key_quote NULL ('+all.length+'개) ===');
  all.forEach(s=>console.log(s.signal+' | '+s.stock+' | '+s.speakers?.name));
})();
