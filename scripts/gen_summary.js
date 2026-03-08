// Generate video summaries from transcript files using Claude API
const fs = require('fs');
const path = require('path');

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A';

const VIDEOS = [
  {
    dbId: 'ffc64461-4859-4f38-898e-519b6ecaf2b2',
    transcriptFile: 'C:/Users/Mario/work/subs/booreadman_Xv-wNA91EPE_transcript.json',
    title: '?쇱꽦?꾩옄 ?덈? ?붿? 留덉꽭??[議곗쭊?????2遺]',
    channel: '遺?쎈궓TV'
  },
  {
    dbId: 'cfc9e60f-5bae-45c5-8e57-8f624f79298c',
    transcriptFile: 'C:/Users/Mario/work/subs/hyoseok_fDZnPoK5lyc.json',
    title: '諛섎룄泥??ㅼ쓬 臾댁꽠寃?移섍퀬?섍컝 異⑷꺽??4醫낅ぉ',
    channel: '?댄슚?앹븘移대뜲誘?
  },
  {
    dbId: '94ff3a67-01d6-49da-89ff-d461a810774c',
    transcriptFile: 'C:/Users/Mario/work/subs/hyoseok_tSXkj2Omz34.json',
    title: '肄붿뒪??6000 ?뚰뙆??7,900 ?쇰━源뚯?',
    channel: '?댄슚?앹븘移대뜲誘?
  },
];

async function generateSummary(title, channel, transcript) {
  const charCount = transcript.length;
  let lineTarget;
  if (charCount < 3000) lineTarget = '3-5以?;
  else if (charCount < 10000) lineTarget = '7-10以?;
  else lineTarget = '10-15以?;

  const resp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': process.env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
      'content-type': 'application/json',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-6',
      max_tokens: 1024,
      messages: [{
        role: 'user',
        content: `?ㅼ쓬? "${channel}" 梨꾨꼸??"${title}" ?곸긽 ?먮쭑?낅땲??

???곸긽???듭떖 ?댁슜??${lineTarget}濡??붿빟?댁＜?몄슂.
- ?곸긽????遊먮룄 ?듭떖???뚯븙?????덉쓣 ?뺣룄濡?援ъ껜?곸쑝濡?
- 二쇱슂 ?쇱젏, 寃곕줎, 異붿쿇 醫낅ぉ, ?쒖옣 ?꾨쭩 ???ы븿
- ?쒓뎅?대줈 ?묒꽦
- 以꾨컮轅덉쑝濡?援щ텇

?먮쭑:
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

