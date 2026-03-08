#!/usr/bin/env node
/**
 * 세상학개론 V11.1 시그널 재분석 스크립트
 * 기존 pending 시그널 삭제 후 V11.1 프롬프트로 재분석
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// ====== 설정 ======
const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
// openclaw.json에서 실제 API 키 읽기 (env는 구버전 키일 수 있음)
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

// V11.1 프롬프트 로드
const PROMPT_FILE = path.join(__dirname, '..', 'prompts', 'pipeline_v11.md');
const SYSTEM_PROMPT = fs.readFileSync(PROMPT_FILE, 'utf-8');

// ====== API 헬퍼 ======
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
  const userMessage = `영상 제목: ${videoTitle}\n\n자막:\n${subtitleText}`;
  
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
          // JSON 추출 - 마크다운 코드블록 우선, 그 다음 단순 JSON 매칭
          let jsonStr = null;
          // 1. ```json ... ``` 블록 추출
          const codeBlockMatch = content.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/);
          if (codeBlockMatch) {
            jsonStr = codeBlockMatch[1];
          } else {
            // 2. 첫 번째 { 에서 시작하는 JSON 객체 추출 (depth counting)
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

// ====== 메인 ======
async function main() {
  console.log('🔧 세상학개론 V11.1 시그널 재분석 시작\n');
  
  // Step 1: 영상 목록 조회
  console.log('📋 Step 1: 영상 목록 조회...');
  const videos = await sbFetch(
    `/rest/v1/influencer_videos?channel_id=eq.${CHANNEL_ID}&select=id,video_id,title,subtitle_text,has_subtitle&order=published_at.asc`,
    { headers: { 'Range': '0-199' } }
  );
  console.log(`총 ${videos.length}개 영상 확인`);
  
  const videosWithSubtitle = videos.filter(v => v.subtitle_text);
  const videosNoSubtitle = videos.filter(v => !v.subtitle_text);
  console.log(`자막 있음: ${videosWithSubtitle.length}개 / 없음: ${videosNoSubtitle.length}개`);
  
  // Step 2: 기존 pending 시그널 조회
  console.log('\n📊 Step 2: 기존 시그널 현황 조회...');
  const videoIds = videos.map(v => v.id).join(',');
  const existingSignals = await sbFetch(
    `/rest/v1/influencer_signals?video_id=in.(${videoIds})&select=id,video_id,stock,signal,review_status&order=created_at.asc`,
    { headers: { 'Range': '0-499' } }
  );
  
  const pendingSignals = existingSignals.filter(s => s.review_status !== 'rejected');
  const rejectedSignals = existingSignals.filter(s => s.review_status === 'rejected');
  
  console.log(`기존 시그널: ${existingSignals.length}개 (pending: ${pendingSignals.length}, rejected: ${rejectedSignals.length})`);
  
  const oldTypeCounts = {};
  existingSignals.forEach(s => {
    oldTypeCounts[s.signal] = (oldTypeCounts[s.signal] || 0) + 1;
  });
  console.log('기존 분포:', JSON.stringify(oldTypeCounts));
  
  // Step 3: 각 영상 V11.1 분석
  console.log('\n🤖 Step 3: V11.1 분석 시작...');
  const newSignals = [];
  const skipped = [];
  const errors = [];
  
  for (let i = 0; i < videosWithSubtitle.length; i++) {
    const video = videosWithSubtitle[i];
    const videoNum = i + 1;
    
    // 20개마다 5초 휴식
    if (i > 0 && i % BATCH_SIZE === 0) {
      console.log(`  ⏸️  ${i}개 완료, 5초 휴식...`);
      await sleep(BATCH_REST_MS);
    }
    
    console.log(`  [${videoNum}/${videosWithSubtitle.length}] "${video.title.slice(0, 40)}..."`);
    
    try {
      const result = await claudeAnalyze(video.title, video.subtitle_text);
      const signals = result.signals || [];
      
      if (signals.length === 0) {
        console.log(`    → 시그널 없음 (매크로/교육 영상)`);
      } else {
        console.log(`    → ${signals.length}개 시그널 추출`);
        for (const sig of signals) {
          newSignals.push({
            video_id: video.id,
            speaker_id: SPEAKER_ID,
            stock: sig.stock,
            ticker: sig.ticker || null,
            market: detectMarket(sig.ticker),
            mention_type: sig.signal_type === '매수' || sig.signal_type === '매도' ? '결론' : '논거',
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
      console.error(`    ❌ 오류: ${e.message}`);
      errors.push({ video: video.title, error: e.message });
    }
    
    // 딜레이
    if (i < videosWithSubtitle.length - 1) {
      await sleep(DELAY_MS);
    }
  }
  
  // 자막 없는 영상 기록
  for (const v of videosNoSubtitle) {
    skipped.push(v.title);
  }
  
  console.log(`\n✅ 분석 완료: ${newSignals.length}개 신규 시그널 추출`);
  console.log(`⏭️  건너뜀: ${skipped.length}개 (자막 없음)`);
  if (errors.length > 0) console.log(`❌ 오류: ${errors.length}개`);
  
  // Step 4: DB 업데이트
  console.log('\n💾 Step 4: DB 업데이트...');
  
  // 기존 pending 시그널 DELETE (이미 없으면 skip)
  if (pendingSignals.length > 0) {
    const pendingIds = pendingSignals.map(s => s.id).join(',');
    await sbFetch(
      `/rest/v1/influencer_signals?id=in.(${pendingIds})`,
      { method: 'DELETE', headers: { 'Prefer': 'return=minimal' } }
    );
    console.log(`  🗑️  기존 pending 시그널 ${pendingSignals.length}개 삭제 완료`);
  } else {
    console.log(`  ℹ️  삭제할 pending 시그널 없음 (이미 삭제됨)`);
  }
  
  // 새 시그널 INSERT (배치)
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
    console.log(`  ✅ INSERT ${insertedCount}/${newSignals.length} 완료`);
  }
  
  // Step 5: 결과 집계
  const newTypeCounts = {};
  newSignals.forEach(s => {
    newTypeCounts[s.signal] = (newTypeCounts[s.signal] || 0) + 1;
  });
  
  console.log('\n📈 최종 결과:');
  console.log(`  기존: ${pendingSignals.length}개 → 신규: ${newSignals.length}개`);
  console.log(`  기존 분포: ${JSON.stringify(oldTypeCounts)}`);
  console.log(`  신규 분포: ${JSON.stringify(newTypeCounts)}`);
  console.log(`  Rejected 유지: ${rejectedSignals.length}개`);
  if (errors.length > 0) {
    console.log(`  오류 목록:`);
    errors.forEach(e => console.log(`    - ${e.video}: ${e.error}`));
  }
  
  // 결과 저장
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
  console.log('\n🎉 완료!');
  process.exit(0);
}).catch(e => {
  console.error('💥 치명적 오류:', e);
  process.exit(1);
});
