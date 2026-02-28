// Generate video summaries from transcript files using Claude API
const fs = require('fs');
const path = require('path');

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A';

const VIDEOS = [
  {
    dbId: 'ffc64461-4859-4f38-898e-519b6ecaf2b2',
    transcriptFile: 'C:/Users/Mario/work/subs/booreadman_Xv-wNA91EPE_transcript.json',
    title: '삼성전자 절대 팔지 마세요 [조진표 대표 2부]',
    channel: '부읽남TV'
  },
  {
    dbId: 'cfc9e60f-5bae-45c5-8e57-8f624f79298c',
    transcriptFile: 'C:/Users/Mario/work/subs/hyoseok_fDZnPoK5lyc.json',
    title: '반도체 다음 무섭게 치고나갈 충격적 4종목',
    channel: '이효석아카데미'
  },
  {
    dbId: '94ff3a67-01d6-49da-89ff-d461a810774c',
    transcriptFile: 'C:/Users/Mario/work/subs/hyoseok_tSXkj2Omz34.json',
    title: '코스피 6000 돌파… 7,900 논리까지',
    channel: '이효석아카데미'
  },
];

async function generateSummary(title, channel, transcript) {
  const charCount = transcript.length;
  let lineTarget;
  if (charCount < 3000) lineTarget = '3-5줄';
  else if (charCount < 10000) lineTarget = '7-10줄';
  else lineTarget = '10-15줄';

  const resp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': process.env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
      'content-type': 'application/json',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1024,
      messages: [{
        role: 'user',
        content: `다음은 "${channel}" 채널의 "${title}" 영상 자막입니다.

이 영상의 핵심 내용을 ${lineTarget}로 요약해주세요.
- 영상을 안 봐도 핵심을 파악할 수 있을 정도로 구체적으로
- 주요 논점, 결론, 추천 종목, 시장 전망 등 포함
- 한국어로 작성
- 줄바꿈으로 구분

자막:
${transcript.slice(0, 15000)}`
      }],
    }),
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`Claude API ${resp.status}: ${err.slice(0, 200)}`);
  }
  const data = await resp.json();
  return data.content[0].text;
}

async function main() {
  const summaries = {};
  
  for (const video of VIDEOS) {
    console.log(`\n=== ${video.title} (${video.channel}) ===`);
    
    const raw = JSON.parse(fs.readFileSync(video.transcriptFile, 'utf-8'));
    const items = raw.segments || raw.subtitles || raw.transcript || [];
    const transcript = Array.isArray(items) ? items.map(s => s.text).join(' ') : (typeof items === 'string' ? items : '');
    console.log(`Transcript: ${transcript.length} chars`);
    
    if (!transcript) { console.log('Skip - no transcript'); continue; }
    
    console.log('Generating summary...');
    const summary = await generateSummary(video.title, video.channel, transcript);
    console.log(`Summary:\n${summary}\n`);
    
    summaries[video.dbId] = summary;
  }
  
  // Save summaries to file for later DB update
  fs.writeFileSync('scripts/video_summaries.json', JSON.stringify(summaries, null, 2));
  console.log('\nSaved to scripts/video_summaries.json');
  console.log('\nTo update DB, run the ALTER TABLE first, then the update script.');
}

main().catch(console.error);
