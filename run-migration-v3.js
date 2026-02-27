const fs = require('fs');
const { Client } = require('pg');

const sql = fs.readFileSync('invest-sns/supabase/influencer-complete-migration-v3.sql', 'utf8');

const client = new Client({
  host: 'aws-1-ap-southeast-1.pooler.supabase.com',
  port: 5432,
  database: 'postgres',
  user: 'postgres.arypzhotxflimroprmdk',
  password: 'WKWKRSKAN12#',
  ssl: { rejectUnauthorized: false }
});

async function run() {
  console.log('Connecting to Supabase DB...');
  await client.connect();
  console.log('Connected! Executing migration...');
  
  try {
    await client.query(sql);
    console.log('✅ Migration complete!');
    
    // Verify
    const speakers = await client.query('SELECT count(*) FROM public.speakers');
    const channels = await client.query('SELECT count(*) FROM public.influencer_channels');
    const videos = await client.query('SELECT count(*) FROM public.influencer_videos');
    const signals = await client.query('SELECT count(*) FROM public.influencer_signals');
    
    console.log(`\nVerification:`);
    console.log(`  speakers: ${speakers.rows[0].count}`);
    console.log(`  channels: ${channels.rows[0].count}`);
    console.log(`  videos: ${videos.rows[0].count}`);
    console.log(`  signals: ${signals.rows[0].count}`);
  } catch(e) {
    console.error('❌ Error:', e.message);
    if (e.detail) console.error('Detail:', e.detail);
  } finally {
    await client.end();
  }
}

run();
