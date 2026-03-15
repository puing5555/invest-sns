/**
 * Migrate signal_prices.json → DB columns via Supabase REST API (PATCH)
 * Uses service role key for full access
 */
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '..', '.env.local') });

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://arypzhotxflimroprmdk.supabase.co';
const SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SERVICE_KEY) {
  console.error('ERROR: SUPABASE_SERVICE_ROLE_KEY not found in .env.local');
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SERVICE_KEY);

async function main() {
  // Load signal_prices.json from public/
  const jsonPath = path.join(__dirname, '..', 'public', 'signal_prices.json');
  const priceData = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
  const entries = Object.entries(priceData);
  console.log(`Total entries in signal_prices.json: ${entries.length}`);

  const BATCH_SIZE = 50;
  let updated = 0;
  let skipped = 0;
  let errors = 0;

  for (let i = 0; i < entries.length; i += BATCH_SIZE) {
    const batch = entries.slice(i, i + BATCH_SIZE);

    // Use Promise.all for batch parallelism within each batch
    const results = await Promise.all(
      batch.map(async ([uuid, pd]) => {
        if (!pd || pd.price_at_signal == null) {
          return { status: 'skipped', uuid };
        }
        try {
          const { error } = await supabase
            .from('influencer_signals')
            .update({
              price_at_signal: pd.price_at_signal,
              price_current: pd.price_current,
              return_pct: pd.return_pct,
            })
            .eq('id', uuid);

          if (error) {
            return { status: 'error', uuid, error: error.message };
          }
          return { status: 'updated', uuid };
        } catch (e) {
          return { status: 'error', uuid, error: e.message };
        }
      })
    );

    for (const r of results) {
      if (r.status === 'updated') updated++;
      else if (r.status === 'skipped') skipped++;
      else { errors++; if (errors <= 5) console.error(`Error ${r.uuid}: ${r.error}`); }
    }

    const progress = Math.min(i + BATCH_SIZE, entries.length);
    process.stdout.write(`\rProgress: ${progress}/${entries.length} | updated: ${updated} | skipped: ${skipped} | errors: ${errors}`);

    // Small delay between batches to avoid rate limiting
    if (i + BATCH_SIZE < entries.length) {
      await new Promise(r => setTimeout(r, 200));
    }
  }

  console.log(`\n\n✅ Migration complete!`);
  console.log(`   Updated: ${updated}`);
  console.log(`   Skipped: ${skipped}`);
  console.log(`   Errors:  ${errors}`);

  // Verify
  const { data: sample, error: verifyErr } = await supabase
    .from('influencer_signals')
    .select('id, price_at_signal, price_current, return_pct')
    .not('return_pct', 'is', null)
    .limit(5);

  if (!verifyErr && sample) {
    console.log(`\n📈 Sample of migrated data (${sample.length} rows with return_pct):`);
    sample.forEach(r => console.log(`   ${r.id.slice(0,8)}.. | price_at=${r.price_at_signal} | current=${r.price_current} | return=${r.return_pct}%`));
  }

  // Count stats
  const { count: totalCount } = await supabase.from('influencer_signals').select('*', { count: 'exact', head: true });
  const { count: withPrice } = await supabase.from('influencer_signals').select('*', { count: 'exact', head: true }).not('price_at_signal', 'is', null);
  const { count: withReturn } = await supabase.from('influencer_signals').select('*', { count: 'exact', head: true }).not('return_pct', 'is', null);

  console.log(`\n📊 Final DB stats:`);
  console.log(`   Total signals: ${totalCount}`);
  console.log(`   With price_at_signal: ${withPrice}`);
  console.log(`   With return_pct: ${withReturn}`);

  console.log('\n🏁 Done!');
}

main().catch(e => {
  console.error('Fatal error:', e.message);
  process.exit(1);
});
