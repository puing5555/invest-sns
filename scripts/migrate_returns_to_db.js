const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

const client = new Client({
  host: 'aws-1-ap-southeast-1.pooler.supabase.com',
  port: 5432,
  database: 'postgres',
  user: 'postgres.arypzhotxflimroprmdk',
  password: 'WKWKRSKAN12#',
  ssl: { rejectUnauthorized: false }
});

async function main() {
  await client.connect();
  console.log('Connected to Supabase DB');

  // 1단계: 컬럼 확인 및 추가
  const colCheck = await client.query(`
    SELECT column_name FROM information_schema.columns 
    WHERE table_name='influencer_signals' 
    AND column_name IN ('price_at_signal', 'price_current', 'return_pct')
  `);
  const existingCols = colCheck.rows.map(r => r.column_name);
  console.log('Existing columns:', existingCols);

  if (!existingCols.includes('price_at_signal')) {
    await client.query('ALTER TABLE influencer_signals ADD COLUMN IF NOT EXISTS price_at_signal NUMERIC');
    console.log('✅ price_at_signal column added');
  } else {
    console.log('⏭️ price_at_signal already exists');
  }

  if (!existingCols.includes('price_current')) {
    await client.query('ALTER TABLE influencer_signals ADD COLUMN IF NOT EXISTS price_current NUMERIC');
    console.log('✅ price_current column added');
  } else {
    console.log('⏭️ price_current already exists');
  }

  if (!existingCols.includes('return_pct')) {
    await client.query('ALTER TABLE influencer_signals ADD COLUMN IF NOT EXISTS return_pct NUMERIC');
    console.log('✅ return_pct column added');
  } else {
    console.log('⏭️ return_pct already exists');
  }

  // 2단계: signal_prices.json 로드
  const jsonPath = path.join(__dirname, '..', 'public', 'signal_prices.json');
  const priceData = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
  const entries = Object.entries(priceData);
  console.log(`\n📊 Total entries in signal_prices.json: ${entries.length}`);

  // 3단계: 배치 업데이트 (50개씩)
  const BATCH_SIZE = 50;
  let updated = 0;
  let skipped = 0;
  let errors = 0;

  for (let i = 0; i < entries.length; i += BATCH_SIZE) {
    const batch = entries.slice(i, i + BATCH_SIZE);
    
    for (const [uuid, pd] of batch) {
      if (!pd || pd.price_at_signal == null) {
        skipped++;
        continue;
      }
      try {
        const res = await client.query(
          'UPDATE influencer_signals SET price_at_signal=$1, price_current=$2, return_pct=$3 WHERE id=$4',
          [pd.price_at_signal, pd.price_current, pd.return_pct, uuid]
        );
        if (res.rowCount > 0) {
          updated++;
        } else {
          skipped++;
        }
      } catch (e) {
        console.error(`Error updating ${uuid}:`, e.message);
        errors++;
      }
    }

    const progress = Math.min(i + BATCH_SIZE, entries.length);
    process.stdout.write(`\rProgress: ${progress}/${entries.length} (updated: ${updated}, skipped: ${skipped}, errors: ${errors})`);
  }

  console.log(`\n\n✅ Migration complete!`);
  console.log(`   Updated: ${updated}`);
  console.log(`   Skipped: ${skipped}`);
  console.log(`   Errors:  ${errors}`);

  // 4단계: 검증
  const verifyResult = await client.query(`
    SELECT 
      COUNT(*) as total,
      COUNT(price_at_signal) as with_price,
      COUNT(return_pct) as with_return
    FROM influencer_signals
  `);
  const v = verifyResult.rows[0];
  console.log(`\n📈 Verification:`);
  console.log(`   Total signals: ${v.total}`);
  console.log(`   With price_at_signal: ${v.with_price}`);
  console.log(`   With return_pct: ${v.with_return}`);

  await client.end();
  console.log('\n🏁 Done!');
}

main().catch(e => { 
  console.error('Fatal error:', e.message); 
  process.exit(1); 
});
