const { Client } = require('pg');
const client = new Client({
  host: 'aws-1-ap-southeast-1.pooler.supabase.com',
  port: 5432, database: 'postgres',
  user: 'postgres.arypzhotxflimroprmdk',
  password: 'WKWKRSKAN12#',
  ssl: { rejectUnauthorized: false }
});

async function run() {
  await client.connect();
  
  // Check influencer_calls (might have old 177 signals)
  const calls = await client.query(`SELECT count(*) FROM public.influencer_calls`);
  console.log('influencer_calls:', calls.rows[0].count, 'rows');
  
  if (parseInt(calls.rows[0].count) > 0) {
    const cols = await client.query(`SELECT column_name FROM information_schema.columns WHERE table_name='influencer_calls' ORDER BY ordinal_position`);
    console.log('Columns:', cols.rows.map(r=>r.column_name).join(', '));
    
    const sample = await client.query(`SELECT * FROM public.influencer_calls LIMIT 3`);
    sample.rows.forEach(r => console.log(JSON.stringify(r).substring(0, 300)));
    
    // Check by influencer
    const byInf = await client.query(`SELECT influencer_id, count(*) FROM public.influencer_calls GROUP BY influencer_id`);
    console.log('\nBy influencer_id:', byInf.rows);
  }

  // Check influencers table
  const inf = await client.query(`SELECT * FROM public.influencers LIMIT 10`);
  console.log('\n=== influencers ===');
  inf.rows.forEach(r => console.log(JSON.stringify(r).substring(0, 200)));

  await client.end();
}
run();
