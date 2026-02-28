// Generate video summaries for existing videos using their subtitles
// Uses Claude API via fetch to generate summaries

const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A';

// Video IDs to process (부읽남TV + 이효석)
const VIDEOS = [
  { id: 'ffc64461-4859-4f38-898e-519b6ecaf2b2', videoId: 'Xv-wNA91EPE', title: '삼성전자 절대 팔지 마세요 [조진표 대표 2부]', channel: '부읽남TV' },
  { id: 'cfc9e60f-5bae-45c5-8e57-8f624f79298c', videoId: 'fDZnPoK5lyc', title: '반도체 다음 무섭게 치고나갈 충격적 4종목', channel: '이효석아카데미' },
  { id: '94ff3a67-01d6-49da-89ff-d461a810774c', videoId: 'tSXkj2Omz34', title: '코스피 6000 돌파… 7,900 논리까지', channel: '이효석아카데미' },
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
  if (charCount < 3000) lineTarget = '3-5줄';
  else if (charCount < 10000) lineTarget = '7-10줄';
  else lineTarget = '10-15줄';

  const prompt = `다음은 "${channel}" 채널의 "${title}" 영상 자막입니다.

이 영상의 핵심 내용을 ${lineTarget}로 요약해주세요.
- 영상을 안 봐도 핵심을 파악할 수 있을 정도로 구체적으로
- 주요 논점, 결론, 추천 종목, 시장 전망 등 포함
- 한국어로 작성

자막:
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
      model: 'claude-sonnet-4-20250514',
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
