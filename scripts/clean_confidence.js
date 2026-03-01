const {createClient} = require('@supabase/supabase-js');
const fs = require('fs');

const sb = createClient(
  'https://arypzhotxflimroprmdk.supabase.co',
  fs.readFileSync('.env.local','utf8').match(/SUPABASE_SERVICE_ROLE_KEY=(.+)/)[1].trim()
);

const CONFIDENCE_MAP = {
  'high': 8,
  'medium': 5,
  'low': 3,
  'very high': 9,
  'very low': 2,
  'moderate': 5,
};

(async()=>{
  // Get all signals
  const {data, error} = await sb.from('influencer_signals').select('id,confidence,timestamp');
  if(error){console.error(error);return;}
  
  let fixes = [];
  
  for(const sig of data) {
    const conf = sig.confidence;
    // Check if confidence is text
    if(conf && typeof conf === 'string' && isNaN(Number(conf))) {
      const num = CONFIDENCE_MAP[conf.toLowerCase().trim()] || 5;
      fixes.push({id: sig.id, field: 'confidence', old: conf, new: num});
    }
    
    // Check timestamp 0:00
    if(sig.timestamp === '0:00' || sig.timestamp === '00:00' || sig.timestamp === '0:00:00') {
      fixes.push({id: sig.id, field: 'timestamp', old: sig.timestamp, new: null});
    }
  }
  
  console.log(`Found ${fixes.length} issues to fix:`);
  const confFixes = fixes.filter(f=>f.field==='confidence');
  const tsFixes = fixes.filter(f=>f.field==='timestamp');
  console.log(`  Confidence text→number: ${confFixes.length}`);
  console.log(`  Timestamp 0:00: ${tsFixes.length}`);
  
  // Show samples
  confFixes.slice(0,5).forEach(f=>console.log(`    ${f.id.slice(0,8)}.. "${f.old}" → ${f.new}`));
  
  // Apply fixes
  let updated = 0;
  for(const fix of fixes) {
    const update = {};
    update[fix.field] = fix.new;
    const {error: err} = await sb.from('influencer_signals').update(update).eq('id', fix.id);
    if(err) {
      console.error(`Failed ${fix.id}: ${err.message}`);
    } else {
      updated++;
    }
  }
  
  console.log(`\nUpdated ${updated}/${fixes.length} records`);
})();
