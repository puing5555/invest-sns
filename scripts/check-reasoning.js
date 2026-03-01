const {createClient} = require('@supabase/supabase-js');
const fs = require('fs');
const env = fs.readFileSync('.env.local','utf8');
const vars = {};
env.split('\n').forEach(l=>{const [k,...v]=l.split('=');if(k)vars[k.trim()]=v.join('=').trim()});
const sb = createClient(vars.NEXT_PUBLIC_SUPABASE_URL, vars.NEXT_PUBLIC_SUPABASE_ANON_KEY);
(async()=>{
  const {data} = await sb.from('influencer_signals').select('id,stock,reasoning');
  const short = data.filter(s => !s.reasoning || s.reasoning.length < 80);
  console.log('짧은 reasoning (<80자): '+short.length+'/'+data.length+'개');
  short.forEach(s => {
    const r = s.reasoning || 'null';
    console.log('- ' + s.stock + ' (' + r.length + '자): ' + r);
  });
})();
