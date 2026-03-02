import { execSync } from 'child_process';
import https from 'https';
import fs from 'fs';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const CHANNEL_ID = 'd68f8efd-64c8-4c07-9d34-e98c2954f4e1';

const MISSING = ['JzzXPN5v1BI','79PFFmQQjOw','4bClsFvaoLs','NlWaAL3SOxE','qkpmS6yfO_g','KvuATAaRxe8','CN_T1V1ocjg','zRGNYWXHfV4','oiAMDjdr334','YbbV60KVe_c','OadsiFLklsM'];

function supabasePost(data) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify(data);
    const req = https.request(`${SUPABASE_URL}/rest/v1/influencer_videos`, {
      method: 'POST',
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=representation',
      },
    }, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) resolve(JSON.parse(d));
        else reject(new Error(`${res.statusCode}: ${d}`));
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
  let success = 0, fail = 0;
  
  for (const vid of MISSING) {
    console.log(`\n[${success+fail+1}/${MISSING.length}] ${vid}...`);
    try {
      // Get metadata via yt-dlp
      const raw = execSync(`python -m yt_dlp --dump-json "https://www.youtube.com/watch?v=${vid}"`, {
        encoding: 'utf-8', timeout: 30000,
        env: { ...process.env }
      });
      const meta = JSON.parse(raw);
      
      const row = {
        channel_id: CHANNEL_ID,
        video_id: vid,
        title: meta.title || 'Unknown',
        published_at: meta.upload_date ? `${meta.upload_date.slice(0,4)}-${meta.upload_date.slice(4,6)}-${meta.upload_date.slice(6,8)}` : null,
        duration_seconds: meta.duration || null,
        has_subtitle: false,
        subtitle_language: null,
        subtitle_text: null,
      };
      
      console.log(`  Title: ${row.title}`);
      console.log(`  Date: ${row.published_at}, Duration: ${row.duration_seconds}s`);
      
      const result = await supabasePost(row);
      console.log(`  ✅ Inserted`);
      success++;
    } catch (e) {
      console.log(`  ❌ Error: ${e.message.slice(0, 200)}`);
      fail++;
    }
    
    await sleep(2000);
  }
  
  console.log(`\n${'='.repeat(40)}`);
  console.log(`Done! Success: ${success}, Fail: ${fail}`);
}

main();
