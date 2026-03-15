import { createClient } from '@supabase/supabase-js';
import { exec } from 'child_process';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { config } from 'dotenv';
config({ path: '.env.local' });

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

const CHANNEL_ID = 'd153b75b-1843-4a99-b49f-c31081a8f566';
const PROGRESS_FILE = 'fix-published-at-progress.json';
const CONCURRENCY = 10;

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function getUploadDate(videoId) {
  return new Promise((resolve) => {
    const proc = exec(
      `python -m yt_dlp --skip-download --no-warnings --socket-timeout 15 --print upload_date "https://youtube.com/watch?v=${videoId}"`,
      { timeout: 45000 },
      (err, stdout, stderr) => {
        if (err) {
          if (stderr?.includes('429') || stderr?.includes('Too Many')) {
            resolve({ date: null, error: '429', retry: true });
          } else {
            resolve({ date: null, error: (stderr || err.message).slice(0, 200) });
          }
          return;
        }
        const result = stdout.trim();
        if (/^\d{8}$/.test(result)) {
          resolve({ date: `${result.slice(0,4)}-${result.slice(4,6)}-${result.slice(6,8)}T00:00:00Z` });
        } else {
          resolve({ date: null, error: `unexpected: ${result.slice(0,100)}` });
        }
      }
    );
  });
}

async function main() {
  console.log('Fetching videos from Supabase...');
  const allVideos = [];
  let from = 0;
  while (true) {
    const { data, error } = await supabase
      .from('influencer_videos')
      .select('id, video_id')
      .eq('channel_id', CHANNEL_ID)
      .is('published_at', null)
      .range(from, from + 999);
    if (error) { console.error(error); process.exit(1); }
    if (!data.length) break;
    allVideos.push(...data);
    from += 1000;
  }
  console.log(`Found ${allVideos.length} videos with null published_at`);

  let progress = {};
  if (existsSync(PROGRESS_FILE)) {
    progress = JSON.parse(readFileSync(PROGRESS_FILE, 'utf8'));
    console.log(`Resuming - already processed ${Object.keys(progress).length}`);
  }

  const toProcess = allVideos.filter(v => !(v.id in progress));
  console.log(`Need to process ${toProcess.length} remaining`);

  let successCount = Object.values(progress).filter(v => v.date).length;
  let failCount = Object.values(progress).filter(v => !v.date).length;
  let processed = 0;

  // Process in chunks of CONCURRENCY
  for (let i = 0; i < toProcess.length; i += CONCURRENCY) {
    const chunk = toProcess.slice(i, i + CONCURRENCY);
    const results = await Promise.all(chunk.map(async (v) => {
      const res = await getUploadDate(v.video_id);
      return { ...v, ...res };
    }));

    let gotRateLimit = false;
    for (const r of results) {
      if (r.retry) {
        gotRateLimit = true;
        continue; // will retry
      }
      if (r.date) {
        const { error } = await supabase
          .from('influencer_videos')
          .update({ published_at: r.date })
          .eq('id', r.id);
        if (error) {
          progress[r.id] = { video_id: r.video_id, date: null, error: 'db_error' };
          failCount++;
        } else {
          progress[r.id] = { video_id: r.video_id, date: r.date };
          successCount++;
        }
      } else {
        progress[r.id] = { video_id: r.video_id, date: null, error: r.error };
        failCount++;
      }
      processed++;
    }

    writeFileSync(PROGRESS_FILE, JSON.stringify(progress, null, 2));
    const total = successCount + failCount;
    console.log(`[${total}/${allVideos.length}] success=${successCount} fail=${failCount}`);

    if (gotRateLimit) {
      console.log('Rate limited! Waiting 60s...');
      await sleep(60000);
      i -= CONCURRENCY; // retry this chunk
      continue;
    }

    // Small delay between chunks
    await sleep(1000);
  }

  console.log(`\n=== DONE ===`);
  console.log(`Success: ${successCount}, Failed: ${failCount}`);

  const failures = Object.values(progress).filter(v => !v.date);
  if (failures.length) {
    console.log('\nFailed videos:');
    failures.forEach(f => console.log(`  ${f.video_id}: ${f.error}`));
  }

  const { count } = await supabase
    .from('influencer_videos')
    .select('id', { count: 'exact', head: true })
    .eq('channel_id', CHANNEL_ID)
    .is('published_at', null);
  console.log(`\nRemaining null published_at: ${count}`);
}

main().catch(console.error);
