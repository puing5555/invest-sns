import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  'https://arypzhotxflimroprmdk.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
);

const CHANNEL_ID = '12facb47-407d-4fd3-a310-12dd5a802d1f';

// Known speakers
const SPEAKERS = {
  '조진표': '6b2696ff',
  '배재규': 'd5ea4443',
  '이정윤': 'fcc6738d',
  '김학주': '289de288',
  '한정수': 'd4219d6b',
  '이영수': '81dd42e4',
  '배제기': '01b70353',
};

function extractGuestName(title) {
  // Match [게스트명 직함 부수] pattern at end
  const match = title.match(/\[([^\]]+)\]\s*$/);
  if (!match) return null;
  const bracket = match[1];
  // First word is usually the name (2-3 Korean chars)
  const nameMatch = bracket.match(/^([가-힣]{2,3})/);
  return nameMatch ? nameMatch[1] : null;
}

async function main() {
  // 1. Get all signals for 부읽남TV
  const { data: signals, error } = await supabase
    .from('influencer_signals')
    .select('id, title, speaker_id')
    .eq('channel_id', CHANNEL_ID);

  if (error) { console.error(error); return; }
  console.log(`Total signals: ${signals.length}`);

  const changes = [];

  for (const sig of signals) {
    const guest = extractGuestName(sig.title);
    if (!guest) {
      console.log(`NO MATCH: "${sig.title}" → keeping 조진표`);
      continue;
    }

    let speakerId = SPEAKERS[guest];
    if (!speakerId) {
      // Need to create new speaker
      console.log(`NEW SPEAKER NEEDED: ${guest}`);
      const { data: existing } = await supabase
        .from('speakers')
        .select('id')
        .eq('name', guest)
        .single();
      
      if (existing) {
        speakerId = existing.id;
      } else {
        const { data: created, error: createErr } = await supabase
          .from('speakers')
          .insert({ name: guest })
          .select('id')
          .single();
        if (createErr) { console.error(`Failed to create ${guest}:`, createErr); continue; }
        speakerId = created.id;
        console.log(`Created speaker ${guest}: ${speakerId}`);
      }
      SPEAKERS[guest] = speakerId;
    }

    if (sig.speaker_id !== speakerId) {
      changes.push({ id: sig.id, title: sig.title, guest, oldSpeaker: sig.speaker_id, newSpeaker: speakerId });
    }
  }

  console.log(`\n=== Changes to make: ${changes.length} ===\n`);
  for (const c of changes) {
    console.log(`"${c.title}" → ${c.guest} (${c.oldSpeaker} → ${c.newSpeaker})`);
  }

  // Apply updates
  for (const c of changes) {
    const { error: upErr } = await supabase
      .from('influencer_signals')
      .update({ speaker_id: c.newSpeaker })
      .eq('id', c.id);
    if (upErr) console.error(`Failed to update ${c.id}:`, upErr);
  }

  console.log(`\nDone! Updated ${changes.length} signals.`);
}

main();
