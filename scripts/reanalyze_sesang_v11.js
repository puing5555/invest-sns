#!/usr/bin/env node
/**
 * ?몄긽?숆컻濡?V11.1 ?쒓렇???щ텇???ㅽ겕由쏀듃
 * 湲곗〈 pending ?쒓렇????젣 ??V11.1 ?꾨＼?꾪듃濡??щ텇??
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// ====== ?ㅼ젙 ======
const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
// openclaw.json?먯꽌 ?ㅼ젣 API ???쎄린 (env??援щ쾭???ㅼ씪 ???덉쓬)
function getAnthropicKey() {
  try {
    const oclawPath = path.join(process.env.USERPROFILE || process.env.HOME, '.openclaw', 'openclaw.json');
    const config = JSON.parse(fs.readFileSync(oclawPath, 'utf-8'));
    return config.env?.ANTHROPIC_API_KEY;
  } catch {}
  return null;
}
const ANTHROPIC_API_KEY = getAnthropicKey() || 'YOUR_ANTHROPIC_API_KEY_HERE';
const CHANNEL_ID = 'd68f8efd-64c8-4c07-9d34-e98c2954f4e1';
const SPEAKER_ID = 'b9496a5f-06fa-47eb-bc2d-47060b095534';
const PIPELINE_VERSION = 'V11.1';
const DELAY_MS = 2500;
const BATCH_REST_MS = 5000;
const BATCH_SIZE = 20;

// V11.1 ?꾨＼?꾪듃 濡쒕뱶
const PROMPT_FILE = path.join(__dirname, '..', 'prompts', 'pipeline_v11.md');
const SYSTEM_PROMPT = fs.readFileSync(PROMPT_FILE, 'utf-8');

// ====== API ?ы띁 ======
async function sbFetch(endpoint, options = {}) {
  const url = SUPABASE_URL + endpoint;
  const headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': 'Bearer ' + SUPABASE_KEY,
    'Content-Type': 'application/json',
    ...options.headers
  };
  const resp = await fetch(url, { ...options, headers });
  const text = await resp.text();
  if (!resp.ok) {
    throw new Error(`Supabase error ${resp.status}: ${text}`);
  }
  return text ? JSON.parse(text) : null;
}

async function claudeAnalyze(videoTitle, subtitleText) {
  const userMessage = `?곸긽 ?쒕ぉ: ${videoTitle}\n\n?먮쭑:\n${subtitleText}`;
  
  const body = JSON.stringify({
    model: 'claude-sonnet-4-5',
    max_tokens: 4096,
    system: SYSTEM_PROMPT,
    messages: [{ role: 'user', content: userMessage }]
  });

  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'api.anthropic.com',
      path: '/v1/messages',
      method: 'POST',
      headers: {
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
        'content-length': Buffer.byteLength(body)
      }
    }, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.error) return reject(new Error(parsed.error.message));
          const content = parsed.content[0].text;
          // JSON 異붿텧 - 留덊겕?ㅼ슫 肄붾뱶釉붾줉 ?곗꽑, 洹??ㅼ쓬 ?⑥닚 JSON 留ㅼ묶
          let jsonStr = null;
          // 1. ```json ... ``` 釉붾줉 異붿텧
          const codeBlockMatch = content.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/);
          if (codeBlockMatch) {
            jsonStr = codeBlockMatch[1];
          } else {
            // 2. 泥?踰덉㎏ { ?먯꽌 ?쒖옉?섎뒗 JSON 媛앹껜 異붿텧 (depth counting)
            const start = content.indexOf('{');
            if (start === -1) return reject(new Error('No JSON in response: ' + content.slice(0, 200)));
            let depth = 0;
            let end = start;
            for (let i = start; i < content.length; i++) {
              if (content[i] === '{') depth++;
              else if (content[i] === '}') { depth--; if (depth === 0) { end = i; break; } }
            }
            jsonStr = content.slice(start, end + 1);
          }
          resolve(JSON.parse(jsonStr));
        } catch (e) {
          reject(new Error('Parse error: ' + e.message + ' | Raw: ' + data.slice(0, 200)));
        }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function confidenceToString(num) {
  if (num >= 8) return 'high';
  if (num >= 6) return 'medium';
  return 'low';
}

function detectMarket(ticker) {
  if (!ticker) return null;
  if (/^\d{6}$/.test(ticker)) return 'KR';
  if (/^[A-Z]+$/.test(ticker)) return 'US';
  return 'GLOBAL';
}

// ====== 硫붿씤 ======
async function main() {
  console.log('?뵩 ?몄긽?숆컻濡?V11.1 ?쒓렇???щ텇???쒖옉\n');
  
  // Step 1: ?곸긽 紐⑸줉 議고쉶
  console.log('?뱥 Step 1: ?곸긽 紐⑸줉 議고쉶...');
  const videos = await sbFetch(
    `/rest/v1/influencer_videos?channel_id=eq.${CHANNEL_ID}&select=id,video_id,title,subtitle_text,has_subtitle&order=published_at.asc`,
    { headers: { 'Range': '0-199' } }
  );
  console.log(`珥?${videos.length}媛??곸긽 ?뺤씤`);
  
  const videosWithSubtitle = videos.filter(v => v.subtitle_text);
  const videosNoSubtitle = videos.filter(v => !v.subtitle_text);
  console.log(`?먮쭑 ?덉쓬: ${videosWithSubtitle.length}媛?/ ?놁쓬: ${videosNoSubtitle.length}媛?);
  
  // Step 2: 湲곗〈 pending ?쒓렇??議고쉶
  console.log('\n?뱤 Step 2: 湲곗〈 ?쒓렇???꾪솴 議고쉶...');
  const videoIds = videos.map(v => v.id).join(',');
  const existingSignals = await sbFetch(
    `/rest/v1/influencer_signals?video_id=in.(${videoIds})&select=id,video_id,stock,signal,review_status&order=created_at.asc`,
    { headers: { 'Range': '0-499' } }
  );
  
  const pendingSignals = existingSignals.filter(s => s.review_status !== 'rejected');
  const rejectedSignals = existingSignals.filter(s => s.review_status === 'rejected');
  
  console.log(`湲곗〈 ?쒓렇?? ${existingSignals.length}媛?(pending: ${pendingSignals.length}, rejected: ${rejectedSignals.length})`);
  
  const oldTypeCounts = {};
  existingSignals.forEach(s => {
    oldTypeCounts[s.signal] = (oldTypeCounts[s.signal] || 0) + 1;
  });
  console.log('湲곗〈 遺꾪룷:', JSON.stringify(oldTypeCounts));
  
  // Step 3: 媛??곸긽 V11.1 遺꾩꽍
  console.log('\n?쨼 Step 3: V11.1 遺꾩꽍 ?쒖옉...');
  const newSignals = [];
  const skipped = [];
  const errors = [];
  
  for (let i = 0; i < videosWithSubtitle.length; i++) {
    const video = videosWithSubtitle[i];
    const videoNum = i + 1;
    
    // 20媛쒕쭏??5珥??댁떇
    if (i > 0 && i % BATCH_SIZE === 0) {
      console.log(`  ?몌툘  ${i}媛??꾨즺, 5珥??댁떇...`);
      await sleep(BATCH_REST_MS);
    }
    
    console.log(`  [${videoNum}/${videosWithSubtitle.length}] "${video.title.slice(0, 40)}..."`);
    
    try {
      const result = await claudeAnalyze(video.title, video.subtitle_text);
      const signals = result.signals || [];
      
      if (signals.length === 0) {
        console.log(`    ???쒓렇???놁쓬 (留ㅽ겕濡?援먯쑁 ?곸긽)`);
      } else {
        console.log(`    ??${signals.length}媛??쒓렇??異붿텧`);
        for (const sig of signals) {
          newSignals.push({
            video_id: video.id,
            speaker_id: SPEAKER_ID,
            stock: sig.stock,
            ticker: sig.ticker || null,
            market: detectMarket(sig.ticker),
            mention_type: sig.signal_type === '留ㅼ닔' || sig.signal_type === '留ㅻ룄' ? '寃곕줎' : '?쇨굅',
            signal: sig.signal_type,
            confidence: confidenceToString(sig.confidence),
            timestamp: sig.timestamp || null,
            key_quote: sig.key_quote,
            reasoning: sig.reasoning,
            pipeline_version: PIPELINE_VERSION,
            review_status: 'pending'
          });
        }
      }
    } catch (e) {
      console.error(`    ???ㅻ쪟: ${e.message}`);
      errors.push({ video: video.title, error: e.message });
    }
    
    // ?쒕젅??
    if (i < videosWithSubtitle.length - 1) {
      await sleep(DELAY_MS);
    }
  }
  
  // ?먮쭑 ?녿뒗 ?곸긽 湲곕줉
  for (const v of videosNoSubtitle) {
    skipped.push(v.title);
  }
  
  console.log(`\n??遺꾩꽍 ?꾨즺: ${newSignals.length}媛??좉퇋 ?쒓렇??異붿텧`);
  console.log(`??툘  嫄대꼫?: ${skipped.length}媛?(?먮쭑 ?놁쓬)`);
  if (errors.length > 0) console.log(`???ㅻ쪟: ${errors.length}媛?);
  
  // Step 4: DB ?낅뜲?댄듃
  console.log('\n?뮶 Step 4: DB ?낅뜲?댄듃...');
  
  // 湲곗〈 pending ?쒓렇??DELETE (?대? ?놁쑝硫?skip)
  if (pendingSignals.length > 0) {
    const pendingIds = pendingSignals.map(s => s.id).join(',');
    await sbFetch(
      `/rest/v1/influencer_signals?id=in.(${pendingIds})`,
      { method: 'DELETE', headers: { 'Prefer': 'return=minimal' } }
    );
    console.log(`  ?뿊截? 湲곗〈 pending ?쒓렇??${pendingSignals.length}媛???젣 ?꾨즺`);
  } else {
    console.log(`  ?뱄툘  ??젣??pending ?쒓렇???놁쓬 (?대? ??젣??`);
  }
  
  // ???쒓렇??INSERT (諛곗튂)
  let insertedCount = 0;
  const INSERT_BATCH = 50;
  for (let i = 0; i < newSignals.length; i += INSERT_BATCH) {
    const batch = newSignals.slice(i, i + INSERT_BATCH);
    await sbFetch(
      `/rest/v1/influencer_signals`,
      {
        method: 'POST',
        headers: { 'Prefer': 'return=minimal' },
        body: JSON.stringify(batch)
      }
    );
    insertedCount += batch.length;
    console.log(`  ??INSERT ${insertedCount}/${newSignals.length} ?꾨즺`);
  }
  
  // Step 5: 寃곌낵 吏묎퀎
  const newTypeCounts = {};
  newSignals.forEach(s => {
    newTypeCounts[s.signal] = (newTypeCounts[s.signal] || 0) + 1;
  });
  
  console.log('\n?뱢 理쒖쥌 寃곌낵:');
  console.log(`  湲곗〈: ${pendingSignals.length}媛????좉퇋: ${newSignals.length}媛?);
  console.log(`  湲곗〈 遺꾪룷: ${JSON.stringify(oldTypeCounts)}`);
  console.log(`  ?좉퇋 遺꾪룷: ${JSON.stringify(newTypeCounts)}`);
  console.log(`  Rejected ?좎?: ${rejectedSignals.length}媛?);
  if (errors.length > 0) {
    console.log(`  ?ㅻ쪟 紐⑸줉:`);
    errors.forEach(e => console.log(`    - ${e.video}: ${e.error}`));
  }
  
  // 寃곌낵 ???
  const resultFile = path.join(__dirname, 'reanalyze_sesang_v11_result.json');
  fs.writeFileSync(resultFile, JSON.stringify({
    timestamp: new Date().toISOString(),
    old: { total: existingSignals.length, pending: pendingSignals.length, rejected: rejectedSignals.length, distribution: oldTypeCounts },
    new: { total: newSignals.length, distribution: newTypeCounts },
    skipped: skipped.length,
    errors: errors
  }, null, 2));
  
  return { oldCount: pendingSignals.length, newCount: newSignals.length, oldDist: oldTypeCounts, newDist: newTypeCounts, errors };
}

main().then(result => {
  console.log('\n?럦 ?꾨즺!');
  process.exit(0);
}).catch(e => {
  console.error('?뮙 移섎챸???ㅻ쪟:', e);
  process.exit(1);
});

