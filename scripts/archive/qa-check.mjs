const url='https://arypzhotxflimroprmdk.supabase.co';
const key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const h={apikey:key,Authorization:'Bearer '+key,'Prefer':'count=exact'};

async function q(path,range='0-0'){
  const r=await fetch(url+'/rest/v1/'+path,{headers:{...h,'Range':range}});
  const cr=r.headers.get('content-range');
  const total=cr?cr.split('/')[1]:'?';
  return {total:parseInt(total),data:await r.json()};
}

const a1=await q('signals?select=id');
console.log('A-1 signals total:',a1.total);

const a2=await q('channels?select=id','0-99');
console.log('A-2 channels:',a2.total);

const a5=await q('signals?select=id&published_at=is.null','0-99');
console.log('A-5 null published_at:',a5.total);

const f3=await q('signals?select=id&or=(ticker_symbol.is.null,signal_type.is.null,channel_id.is.null)','0-99');
console.log('F-3 missing fields:',f3.total);

// unique tickers via RPC or just get all ticker_symbol
const tr=await fetch(url+'/rest/v1/rpc/get_unique_tickers',{method:'POST',headers:{...h,'Content-Type':'application/json'},body:'{}'});
if(tr.ok){const d=await tr.json();console.log('Unique tickers (rpc):',d.length);}
else{
  // fallback: paginate
  let all=[];let page=0;
  while(true){
    const r=await fetch(url+'/rest/v1/signals?select=ticker_symbol&limit=1000&offset='+(page*1000),{headers:{apikey:key,Authorization:'Bearer '+key}});
    const d=await r.json();
    all.push(...d);
    if(d.length<1000)break;
    page++;
  }
  console.log('Unique tickers:',new Set(all.map(x=>x.ticker_symbol)).size);
}
