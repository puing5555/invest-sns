const { Client } = require('pg');
const fs = require('fs');

// Try different connection formats
async function tryConnect(label, connStr) {
  const client = new Client({ connectionString: connStr });
  try {
    await client.connect();
    console.log(`${label}: Connected!`);
    
    const sql = fs.readFileSync('./supabase/influencer-signals-migration.sql', 'utf8');
    await client.query(sql);
    console.log('Migration executed successfully!');
    
    const res = await client.query(`
      SELECT table_name FROM information_schema.tables 
      WHERE table_schema = 'public' AND table_name LIKE 'influencer_%'
      ORDER BY table_name
    `);
    console.log('Influencer tables:', res.rows.map(r => r.table_name));
    await client.end();
    return true;
  } catch (err) {
    console.log(`${label}: ${err.message}`);
    try { await client.end(); } catch(e) {}
    return false;
  }
}

async function run() {
  const pw = 'sb_secret_9kg3BIXTZUaDwD1zBbgEZw_qOfOlUgB';
  const ref = 'arypzhotxflimroprmdk';
  
  // Try pooler with project ref user
  if (await tryConnect('pooler-project', 
    `postgresql://postgres.${ref}:${pw}@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres`)) return;
  
  // Try direct connection  
  if (await tryConnect('direct',
    `postgresql://postgres:${pw}@db.${ref}.supabase.co:5432/postgres`)) return;
    
  // Try pooler with plain postgres user
  if (await tryConnect('pooler-plain',
    `postgresql://postgres:${pw}@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres`)) return;

  // Try port 6543 (transaction mode)
  if (await tryConnect('pooler-6543',
    `postgresql://postgres.${ref}:${pw}@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres`)) return;

  console.log('All connection attempts failed. This might be an API access token, not a DB password.');
}

run();
