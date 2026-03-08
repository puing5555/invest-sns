// Generate video summaries for existing videos using their subtitles
// Uses Claude API via fetch to generate summaries

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A';

// Video IDs to process (遺?쎈궓TV + ?댄슚??
const VIDEOS = [
  { id: 'ffc64461-4859-4f38-898e-519b6ecaf2b2', videoId: 'Xv-wNA91EPE', title: '?쇱꽦?꾩옄 ?덈? ?붿? 留덉꽭??[議곗쭊?????2遺]', channel: '遺?쎈궓TV' },
  { id: 'cfc9e60f-5bae-45c5-8e57-8f624f79298c', videoId: 'fDZnPoK5lyc', title: '諛섎룄泥??ㅼ쓬 臾댁꽠寃?移섍퀬?섍컝 異⑷꺽??4醫낅ぉ', channel: '?댄슚?앹븘移대뜲誘? },
  { id: '94ff3a67-01d6-49da-89ff-d461a810774c', videoId: 'tSXkj2Omz34', title: '肄붿뒪??6000 ?뚰뙆??7,900 ?쇰━源뚯?', channel: '?댄슚?앹븘移대뜲誘? },
];

async function getTranscript(videoId) {
  const { execSync } = require('child_process');
  try {
    const result = execSync(`python -c "
from youtube_transcript_api import YouTubeTranscriptApi
try:
    ytt_api = YouTubeTranscriptApi()
    fetched = ytt_api.fetch(video_id='${videoId}', languages=['ko'])
    for snippet in fetched:
        print(snippet.text)
except Exception as e:
    print(f'ERROR: {e}')
"`, { encoding: 'utf-8', timeout: 30000 });
    if (result.includes('ERROR:')) {
      console.log(`  Transcript error for ${videoId}: ${result.trim()}`);
      return null;
    }
    return result.trim();
  } catch (e) {
    console.log(`  Failed to get transcript for ${videoId}: ${e.message?.slice(0, 100)}`);
    return null;
  }
}

async function generateSummary(title, channel, transcript) {
  // Estimate video length by transcript length
  const charCount = transcript.length;
  let lineTarget;
  if (charCount < 3000) lineTarget = '3-5以?;
  else if (charCount < 10000) lineTarget = '7-10以?;
  else lineTarget = '10-15以?;

  const prompt = `?ㅼ쓬? "${channel}" 梨꾨꼸??"${title}" ?곸긽 ?먮쭑?낅땲??

???곸긽???듭떖 ?댁슜??${lineTarget}濡??붿빟?댁＜?몄슂.
- ?곸긽????遊먮룄 ?듭떖???뚯븙?????덉쓣 ?뺣룄濡?援ъ껜?곸쑝濡?
- 二쇱슂 ?쇱젏, 寃곕줎, 異붿쿇 醫낅ぉ, ?쒖옣 ?꾨쭩 ???ы븿
- ?쒓뎅?대줈 ?묒꽦

?먮쭑:
${transcript.slice(0, 15000)}`;

  // Use Anthropic API
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    console.log('  No ANTHROPIC_API_KEY found, trying OpenClaw config...');
    return null;
  }

  const resp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
      'content-type': 'application/json',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-6',
      max_tokens: 1024,
      messages: [{ role: 'user', content: prompt }],
    }),
  });

  if (!resp.ok) {
    console.log(`  Claude API error: ${resp.status} ${await resp.text()}`);
    return null;
  }

  const data = await resp.json();
  return data.content[0].text;
}

async function updateVideo(dbId, summary) {
  const resp = await fetch(`${SUPABASE_URL}/rest/v1/influencer_videos?id=eq.${dbId}`, {
    method: 'PATCH',
    headers: {
      apikey: SUPABASE_KEY,
      Authorization: `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json',
      Prefer: 'return=minimal',
    },
    body: JSON.stringify({ video_summary: summary }),
  });
  return resp.status;
}

async function main() {
  console.log('=== Video Summary Generator ===\n');

  for (const video of VIDEOS) {
    console.log(`Processing: ${video.title} (${video.channel})`);
    
    // 1. Get transcript
    console.log('  Fetching transcript...');
    const transcript = await getTranscript(video.videoId);
    if (!transcript) {
      console.log('  Skipped (no transcript)\n');
      continue;
    }
    console.log(`  Transcript: ${transcript.length} chars`);

    // 2. Generate summary
    console.log('  Generating summary...');
    const summary = await generateSummary(video.title, video.channel, transcript);
    if (!summary) {
      console.log('  Skipped (summary generation failed)\n');
      continue;
    }
    console.log(`  Summary: ${summary.slice(0, 100)}...`);

    // 3. Update DB
    console.log('  Updating DB...');
    const status = await updateVideo(video.id, summary);
    console.log(`  DB update status: ${status}\n`);
  }

  console.log('Done!');
}

main().catch(console.error);

