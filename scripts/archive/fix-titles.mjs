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

  const changes = [];
  const errors = [];

  for (let i = 0; i < videos.length; i++) {
    const v = videos[i];
    console.log(`[${i+1}/${videos.length}] ${v.video_id} - current: ${v.title?.substring(0, 50)}...`);
    
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

    if (i < videos.length - 1) await sleep(2000);
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
  console.log(`\n=== SUMMARY ===`);
  console.log(`Total: ${videos.length}, Changed: ${changes.length}, Errors: ${errors.length}`);
  if (errors.length) console.log(`Errors:`, errors.map(e => e.video_id).join(', '));
  if (changes.length) {
    console.log(`\nChanged videos:`);
    changes.forEach(c => console.log(`  ${c.video_id}: "${c.oldTitle}" → "${c.newTitle}"`));
  }
}

main().catch(console.error);
