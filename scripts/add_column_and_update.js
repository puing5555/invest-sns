const { Client } = require('pg');
const fs = require('fs');

const client = new Client({
  host: 'aws-1-ap-southeast-1.pooler.supabase.com',
  port: 5432, database: 'postgres',
  user: 'postgres.arypzhotxflimroprmdk',
  password: 'WKWKRSKAN12#',
  ssl: { rejectUnauthorized: false }
});

async function main() {
  await client.connect();
  console.log('Connected to Supabase DB');

  // 1. Add column
  await client.query('ALTER TABLE influencer_videos ADD COLUMN IF NOT EXISTS video_summary TEXT');
  console.log('✅ video_summary column added');

  // 2. Verify
  const cols = await client.query(
    "SELECT column_name FROM information_schema.columns WHERE table_name='influencer_videos' AND column_name='video_summary'"
  );
  console.log('Verified:', cols.rows.length > 0 ? 'EXISTS' : 'MISSING');

  // 3. Load summaries and UPDATE
  const summaries = JSON.parse(fs.readFileSync('./scripts/video_summaries.json', 'utf-8'));
  
  for (const [videoDbId, summary] of Object.entries(summaries)) {
    const res = await client.query(
      'UPDATE influencer_videos SET video_summary = $1 WHERE id = $2',
      [summary, videoDbId]
    );
    console.log(`Updated ${videoDbId}: ${res.rowCount} row(s)`);
  }

  console.log('\n✅ All summaries updated!');
  await client.end();
}

main().catch(e => { console.error('Error:', e.message); process.exit(1); });
