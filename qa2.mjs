const url='https://arypzhotxflimroprmdk.supabase.co';
const key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const h={apikey:key,Authorization:'Bearer '+key};

async function count(path){
  const r=await fetch(url+'/rest/v1/'+path,{headers:{...h,'Prefer':'count=exact','Range':'0-0'}});
  const cr=r.headers.get('content-range');
  if(!cr) { const d=await r.json(); console.log('ERR:',path,d); return -1; }
  return parseInt(cr.split('/')[1]);
}

// List tables first
const r0=await fetch(url+'/rest/v1/',{headers:h});
console.log('Tables status:',r0.status);
const tables=await r0.json();
// Show available table/view names
if(Array.isArray(tables)){
  console.log('Definitions count:',tables.length);
} else {
  console.log('Tables response:',JSON.stringify(tables).slice(0,500));
}

// Try different table names
for(const t of ['signals','signal','investment_signals','posts']){
  const r=await fetch(url+'/rest/v1/'+t+'?select=id&limit=1',{headers:h});
  console.log(`Table "${t}":`,r.status);
}

const a1=await count('signals?select=id');
console.log('A-1 signals:',a1);
const a2=await count('channels?select=id');
console.log('A-2 channels:',a2);
const a5=await count('signals?select=id&published_at=is.null');
console.log('A-5 null pub:',a5);
const f3=await count('signals?select=id&or=(ticker_symbol.is.null,signal_type.is.null,channel_id.is.null)');
console.log('F-3 missing:',f3);
