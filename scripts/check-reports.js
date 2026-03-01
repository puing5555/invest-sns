const {createClient}=require('@supabase/supabase-js');const fs=require('fs');
const env=fs.readFileSync('.env.local','utf8');const vars={};
env.split('\n').forEach(l=>{const [k,...v]=l.split('=');if(k)vars[k.trim()]=v.join('=').trim()});

// anon key
const sb1=createClient(vars.NEXT_PUBLIC_SUPABASE_URL,vars.NEXT_PUBLIC_SUPABASE_ANON_KEY);
// service role key
const sb2=createClient(vars.NEXT_PUBLIC_SUPABASE_URL,vars.SUPABASE_SERVICE_ROLE_KEY);

(async()=>{
  console.log('=== anon key로 조회 ===');
  const {data:d1,error:e1}=await sb1.from('signal_reports').select('*');
  console.log('data:',d1?.length,'개, error:',e1);
  if(d1)d1.forEach(r=>console.log(r.id,r.reason,r.status,r.created_at));

  console.log('\n=== service role key로 조회 ===');
  const {data:d2,error:e2}=await sb2.from('signal_reports').select('*');
  console.log('data:',d2?.length,'개, error:',e2);
  if(d2)d2.forEach(r=>console.log(r.id,r.reason,r.status,r.created_at));
})();
