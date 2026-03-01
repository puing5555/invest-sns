const {createClient}=require('@supabase/supabase-js');const fs=require('fs');
const env=fs.readFileSync('.env.local','utf8');const vars={};
env.split('\n').forEach(l=>{const [k,...v]=l.split('=');if(k)vars[k.trim()]=v.join('=').trim()});
const sb=createClient(vars.NEXT_PUBLIC_SUPABASE_URL,vars.NEXT_PUBLIC_SUPABASE_ANON_KEY);
(async()=>{
  const {data,error}=await sb.from('influencer_signals')
    .select('id,stock,signal,key_quote,speaker_id,speakers(name)')
    .eq('signal','매수');
  if(error){console.log('error:',error);return;}
  const targets = data.filter(s => {
    const name = s.speakers?.name;
    return (name==='박명성' && s.stock==='엔비디아') ||
           (name==='김장열' && s.stock==='삼성전자') ||
           (name==='박병창' && s.stock==='삼성전자');
  });
  if(targets.length===0){
    console.log('직접 매칭 실패. 매수 시그널 전체:');
    data.forEach(s=>console.log(s.speakers?.name+' | '+s.stock+' | quote:['+(s.key_quote||'NULL')+'] | id:'+s.id));
  } else {
    targets.forEach(s=>console.log(s.id+' | '+s.speakers?.name+' | '+s.stock+' | key_quote: ['+(s.key_quote||'NULL')+']'));
  }
})();
