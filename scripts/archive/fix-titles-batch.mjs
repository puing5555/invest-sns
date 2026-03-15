import { execSync } from 'child_process';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';

const headers = {
  'apikey': SERVICE_KEY,
  'Authorization': `Bearer ${SERVICE_KEY}`,
  'Content-Type': 'application/json',
  'Prefer': 'return=minimal'
};

async function supaFetch(path, opts = {}) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1${path}`, { ...opts, headers: { ...headers, ...opts.headers } });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return opts.method === 'PATCH' ? null : res.json();
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
  // 1. Get all videos
  const videos = await supaFetch('/influencer_videos?select=id,video_id,title&order=id');
  console.log(`Found ${videos.length} videos in DB\n`);

  const BATCH_SIZE = 10;
  const changes = [];
  const errors = [];
  let processed = 0;

  // Process in batches of 10
  for (let batchStart = 0; batchStart < videos.length; batchStart += BATCH_SIZE) {
    const batchEnd = Math.min(batchStart + BATCH_SIZE, videos.length);
    const batch = videos.slice(batchStart, batchEnd);
    
    console.log(`\n=== Batch ${Math.floor(batchStart/BATCH_SIZE) + 1}: Processing videos ${batchStart + 1}-${batchEnd} ===`);

    for (let i = 0; i < batch.length; i++) {
      const v = batch[i];
      processed++;
      console.log(`[${processed}/${videos.length}] ${v.video_id} - current: ${v.title?.substring(0, 50)}...`);
      
      try {
        const ytTitle = execSync(`chcp 65001 >nul & python -m yt_dlp --get-title "https://youtube.com/watch?v=${v.video_id}"`, 
          { encoding: 'utf-8', timeout: 30000, env: { ...process.env, PYTHONIOENCODING: 'utf-8' } }).trim();
        
        if (ytTitle && ytTitle !== v.title) {
          changes.push({ id: v.id, video_id: v.video_id, oldTitle: v.title, newTitle: ytTitle });
          console.log(`  → CHANGED: ${ytTitle.substring(0, 60)}`);
        } else {
          console.log(`  → OK (same)`);
        }
      } catch (e) {
        console.log(`  → ERROR: ${e.message?.substring(0, 80)}`);
        errors.push({ video_id: v.video_id, error: e.message?.substring(0, 100) });
      }

      // 3초 딜레이 (마지막 영상이 아닌 경우)
      if (processed < videos.length) await sleep(3000);
    }

    // Batch 완료 후 진행상황 보고
    console.log(`\nBatch ${Math.floor(batchStart/BATCH_SIZE) + 1} completed. Progress: ${processed}/${videos.length} (${Math.round(processed/videos.length*100)}%)`);
    console.log(`Changes found so far: ${changes.length}, Errors: ${errors.length}`);
  }

  // 3. Update changed ones
  console.log(`\n=== Updating ${changes.length} videos ===\n`);
  for (const c of changes) {
    try {
      await supaFetch(`/influencer_videos?id=eq.${c.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ title: c.newTitle })
      });
      console.log(`✅ ${c.video_id}: "${c.oldTitle?.substring(0,40)}" → "${c.newTitle.substring(0,40)}"`);
    } catch (e) {
      console.log(`❌ ${c.video_id}: ${e.message}`);
    }
    await sleep(500);
  }

  // 4. Summary
  console.log(`\n=== FINAL SUMMARY ===`);
  console.log(`Total: ${videos.length}, Changed: ${changes.length}, Errors: ${errors.length}`);
  if (errors.length) {
    console.log(`\nErrors (${errors.length}):`);
    errors.forEach(e => console.log(`  ${e.video_id}: ${e.error}`));
  }
  if (changes.length) {
    console.log(`\nChanged videos (${changes.length}):`);
    changes.forEach(c => console.log(`  ${c.video_id}: "${c.oldTitle?.substring(0,50)}" → "${c.newTitle.substring(0,50)}"`));
  }
}

main().catch(console.error);