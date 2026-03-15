const{createClient}=require('@supabase/supabase-js');
const s=createClient('https://arypzhotxflimroprmdk.supabase.co','eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8');

async function main() {
  const [sigR, vidR, spkR, chR] = await Promise.all([
    s.from('influencer_signals').select('id,video_id,speaker_id,stock,signal'),
    s.from('influencer_videos').select('id,video_id,title,channel_id'),
    s.from('speakers').select('id,name'),
    s.from('influencer_channels').select('id,channel_name'),
  ]);

  const spkMap = Object.fromEntries(spkR.data.map(x => [x.id, x.name]));
  const spkByName = Object.fromEntries(spkR.data.map(x => [x.name, x.id]));
  const vidMap = Object.fromEntries(vidR.data.map(x => [x.id, x]));
  const chMap = Object.fromEntries(chR.data.map(x => [x.id, x.channel_name]));

  const roles = '교수|대표|위원|세무사|작가|애널리스트|전문가|본부장|사무사|이사|팀장|센터장|부사장|사장|PD|박사';
  const guestRe = new RegExp('([가-힣]{2,4})\\s*(' + roles + ')');

  // Find all signals where speaker = channel host but video has a guest
  const fixes = [];

  for (const sig of sigR.data) {
    const vid = vidMap[sig.video_id];
    if (!vid) continue;
    const chName = chMap[vid.channel_id] || '';
    const spkName = spkMap[sig.speaker_id] || '';
    const title = vid.title || '';

    // Check if speaker matches channel name (host attribution)
    const isHostAttrib = (spkName === chName) || 
      (chName === '달란트투자' && spkName === '달란트투자') ||
      (chName === '슈카월드' && spkName === '슈카월드') ||
      (chName === '슈카월드' && spkName === '슈카');

    if (!isHostAttrib) continue;

    // Check title for guest name
    const m = title.match(guestRe);
    if (m) {
      const guestName = m[1];
      const guestRole = m[2];
      if (guestName !== spkName && !spkName.includes(guestName)) {
        fixes.push({
          sigId: sig.id,
          currentSpk: spkName,
          guestName,
          guestRole,
          stock: sig.stock,
          title: title.substring(0, 60),
          videoId: vid.video_id,
        });
      }
    }
  }

  console.log('=== 화자 수정 필요:', fixes.length, '건 ===');
  for (const f of fixes) {
    console.log(`${f.sigId} | ${f.currentSpk} → ${f.guestName} ${f.guestRole} | ${f.stock} | ${f.title}`);
  }

  if (fixes.length === 0) {
    console.log('\n제목 패턴 매칭 안 됨. 달란트투자 전체 영상 제목 확인:');
    for (const vid of vidR.data) {
      if (chMap[vid.channel_id] === '달란트투자') {
        console.log(`  ${vid.video_id} | ${vid.title}`);
      }
    }
    return;
  }

  // Apply fixes
  console.log('\n=== 수정 적용 ===');
  for (const f of fixes) {
    // Get or create speaker
    let speakerId = spkByName[f.guestName];
    if (!speakerId) {
      const { data } = await s.from('speakers').insert({ name: f.guestName }).select('id');
      if (data && data[0]) {
        speakerId = data[0].id;
        spkByName[f.guestName] = speakerId;
        console.log(`  NEW speaker: ${f.guestName} (${speakerId})`);
      }
    }
    if (speakerId) {
      const { error } = await s.from('influencer_signals').update({ speaker_id: speakerId }).eq('id', f.sigId);
      if (error) console.log(`  ERROR: ${f.sigId} - ${error.message}`);
      else console.log(`  OK: ${f.currentSpk} → ${f.guestName} | ${f.stock}`);
    }
  }
  console.log('\nDone!');
}

main().catch(console.error);
