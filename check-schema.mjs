import { createClient } from '@supabase/supabase-js';
const s = createClient('https://arypzhotxflimroprmdk.supabase.co','eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8');

const {data: v} = await s.from('influencer_videos').select('*').limit(1);
console.log('columns:', Object.keys(v[0]));

const {data: vids} = await s.from('influencer_videos').select('id, title').eq('channel_id', '12facb47-407d-4fd3-a310-12dd5a802d1f');
console.log(`\n부읽남TV videos: ${vids?.length}`);

if (vids?.length) {
  const videoIds = vids.map(v => v.id);
  const {data: sigs} = await s.from('influencer_signals').select('id, video_id, speaker_id').in('video_id', videoIds);
  console.log(`Signals: ${sigs?.length}\n`);
  
  const titleMap = Object.fromEntries(vids.map(v => [v.id, v.title]));
  
  for (const sig of (sigs || [])) {
    console.log(`${sig.id} | ${sig.speaker_id?.substring(0,8)} | ${titleMap[sig.video_id]}`);
  }
}
