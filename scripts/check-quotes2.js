const {createClient}=require('@supabase/supabase-js');const fs=require('fs');
const env=fs.readFileSync('.env.local','utf8');const vars={};
env.split('\n').forEach(l=>{const [k,...v]=l.split('=');if(k)vars[k.trim()]=v.join('=').trim()});
const sb=createClient(vars.NEXT_PUBLIC_SUPABASE_URL,vars.NEXT_PUBLIC_SUPABASE_ANON_KEY);
(async()=>{
  // 박명성 전체, 김장열 전체, 박병창 전체
  const {data:speakers}=await sb.from('speakers').select('id,name').in('name',['박명성','김장열','박병창']);
  console.log('speakers:', speakers.map(s=>s.name+':'+s.id).join(', '));
  
  for(const sp of speakers){
    const {data:sigs}=await sb.from('influencer_signals')
      .select('id,stock,signal,key_quote')
      .eq('speaker_id',sp.id);
    console.log('\n=== '+sp.name+' ('+sigs.length+'개) ===');
    sigs.forEach(s=>console.log(s.signal+' | '+s.stock+' | quote:['+(s.key_quote||'NULL')+'] | id:'+s.id));
  }
})();
