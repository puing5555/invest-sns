import fs from 'fs';
import path from 'path';

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const SUBS_DIR = 'C:\\Users\\Mario\\work\\subs\\sesang101';

async function supaFetch(endpoint, options = {}) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${endpoint}`, {
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': options.prefer || '',
    },
    ...options,
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`Supabase error: ${res.status} ${txt}`);
  }
  return options.method === 'PATCH' ? res : res.json();
}

// Get all signals with null timestamp
async function getNullTimestampSignals() {
  // Get all null timestamp signals (not just sesang101)
  const data = await supaFetch('influencer_signals?select=id,video_id,key_quote,speaker_id,timestamp&timestamp=is.null');
  return data;
}

// Get youtube_id from video UUID
async function getYoutubeIds(videoIds) {
  const unique = [...new Set(videoIds)];
  const chunks = [];
  for (let i = 0; i < unique.length; i += 50) {
    chunks.push(unique.slice(i, i + 50));
  }
  const results = {};
  for (const chunk of chunks) {
    const ids = chunk.map(id => `"${id}"`).join(',');
    const data = await supaFetch(`influencer_videos?select=id,video_id&id=in.(${ids})`);
    for (const row of data) {
      if (row.video_id) results[row.id] = row.video_id;
    }
  }
  return results;
}

function findTimestamp(subtitleSegments, keyQuote) {
  if (!keyQuote || !subtitleSegments?.length) return null;
  
  // Normalize Korean text
  const normalize = s => s.replace(/[^가-힣a-zA-Z0-9]/g, ' ').replace(/\s+/g, ' ').trim().toLowerCase();
  const quoteNorm = normalize(keyQuote);
  const quoteWords = quoteNorm.split(' ').filter(w => w.length > 1);
  
  if (quoteWords.length === 0) return null;
  
  let bestScore = 0;
  let bestStart = null;
  
  // Try individual segments and sliding windows of 2-3 segments
  for (let windowSize = 1; windowSize <= 3; windowSize++) {
    for (let i = 0; i <= subtitleSegments.length - windowSize; i++) {
      const combined = subtitleSegments.slice(i, i + windowSize).map(s => s.text).join(' ');
      const segNorm = normalize(combined);
      
      let matchCount = 0;
      for (const word of quoteWords) {
        if (segNorm.includes(word)) matchCount++;
      }
      
      const score = matchCount / quoteWords.length;
      if (score > bestScore) {
        bestScore = score;
        bestStart = subtitleSegments[i].start;
      }
    }
  }
  
  // Require at least 30% match
  if (bestScore < 0.3) return null;
  
  return bestStart;
}

function formatTimestamp(seconds) {
  const s = Math.floor(seconds);
  const min = Math.floor(s / 60);
  const sec = s % 60;
  return `${min}:${sec.toString().padStart(2, '0')}`;
}

async function main() {
  console.log('Fetching null timestamp signals...');
  const signals = await getNullTimestampSignals();
  console.log(`Found ${signals.length} signals with null timestamp`);
  
  if (signals.length === 0) return;
  
  const videoIds = signals.map(s => s.video_id).filter(Boolean);
  console.log('Fetching youtube IDs...');
  const ytMap = await getYoutubeIds(videoIds);
  console.log(`Mapped ${Object.keys(ytMap).length} video UUIDs to youtube IDs`);
  
  let updated = 0;
  let skipped = 0;
  let noSub = 0;
  let noMatch = 0;
  
  // Also check other subtitle directories
  const otherSubDirs = {};
  const subsRoot = 'C:\\Users\\Mario\\work\\subs';
  if (fs.existsSync(subsRoot)) {
    for (const dir of fs.readdirSync(subsRoot)) {
      const fullDir = path.join(subsRoot, dir);
      if (fs.statSync(fullDir).isDirectory()) {
        for (const file of fs.readdirSync(fullDir)) {
          if (file.endsWith('.json') && !file.startsWith('_')) {
            const ytId = file.replace('.json', '');
            otherSubDirs[ytId] = path.join(fullDir, file);
          }
        }
      }
    }
  }
  
  for (const signal of signals) {
    const ytId = ytMap[signal.video_id];
    if (!ytId) {
      skipped++;
      continue;
    }
    
    // Find subtitle file
    let subFile = path.join(SUBS_DIR, `${ytId}.json`);
    if (!fs.existsSync(subFile)) {
      subFile = otherSubDirs[ytId];
      if (!subFile || !fs.existsSync(subFile)) {
        noSub++;
        continue;
      }
    }
    
    const subs = JSON.parse(fs.readFileSync(subFile, 'utf8'));
    const segments = Array.isArray(subs) ? subs : subs.segments || subs.transcript || [];
    
    const startTime = findTimestamp(segments, signal.key_quote);
    if (startTime === null) {
      noMatch++;
      console.log(`NO MATCH: "${signal.key_quote?.substring(0, 50)}..." (${ytId})`);
      continue;
    }
    
    const ts = formatTimestamp(startTime);
    console.log(`MATCH: ${ts} <- "${signal.key_quote?.substring(0, 40)}..."`);
    
    // Update Supabase
    await supaFetch(`influencer_signals?id=eq.${signal.id}`, {
      method: 'PATCH',
      body: JSON.stringify({ timestamp: ts }),
      prefer: 'return=minimal',
    });
    updated++;
  }
  
  console.log(`\n=== RESULTS ===`);
  console.log(`Updated: ${updated}`);
  console.log(`No youtube mapping: ${skipped}`);
  console.log(`No subtitle file: ${noSub}`);
  console.log(`No match found: ${noMatch}`);
  console.log(`Total: ${signals.length}`);
}

main().catch(console.error);
