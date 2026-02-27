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
  
  // Check if 코린이 아빠 signals exist in our new tables
  const newSignals = await client.query(`
    SELECT count(*), pipeline_version 
    FROM public.influencer_signals 
    GROUP BY pipeline_version
  `);
  console.log('=== influencer_signals (new v3 tables) ===');
  console.log(newSignals.rows);

  // Check for any other tables that might have old signals
  const tables = await client.query(`
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name
  `);
  console.log('\n=== All public tables ===');
  tables.rows.forEach(r => console.log(' ', r.table_name));

  // Look for old signal data in other tables
  for (const t of tables.rows) {
    if (t.table_name.includes('signal') && t.table_name !== 'influencer_signals') {
      const count = await client.query(`SELECT count(*) FROM public."${t.table_name}"`);
      const sample = await client.query(`SELECT * FROM public."${t.table_name}" LIMIT 3`);
      console.log(`\n=== ${t.table_name}: ${count.rows[0].count} rows ===`);
      if (sample.rows.length > 0) {
        console.log('Columns:', Object.keys(sample.rows[0]).join(', '));
        sample.rows.forEach(r => console.log(JSON.stringify(r).substring(0, 200)));
      }
    }
  }

  await client.end();
}
run();
