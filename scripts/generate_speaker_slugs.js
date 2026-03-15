#!/usr/bin/env node
/**
 * data/speaker_slugs.json 자동 생성
 *
 * Supabase speakers 테이블에서 전체 화자 목록을 가져와
 * lib/speakerSlugs.ts의 매핑 로직과 동일하게 slug을 생성합니다.
 *
 * 사용법: node scripts/generate_speaker_slugs.js
 * 실행 시점: 채널 추가 후 빌드 전 (auto_pipeline.py에서 자동 호출 가능)
 */

const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

// .env.local 로드
const envPath = path.join(__dirname, '..', '.env.local');
const env = {};
fs.readFileSync(envPath, 'utf-8').split('\n').forEach(line => {
  const idx = line.indexOf('=');
  if (idx > 0) env[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
});

// lib/speakerSlugs.ts의 매핑 로드 (정규식으로 추출)
const slugsPath = path.join(__dirname, '..', 'lib', 'speakerSlugs.ts');
const slugsContent = fs.readFileSync(slugsPath, 'utf-8');
const SPEAKER_SLUGS = {};
const re = /'([^']+)':\s*'([^']+)'/g;
let m;
while ((m = re.exec(slugsContent)) !== null) {
  SPEAKER_SLUGS[m[1]] = m[2];
}

// hash 기반 slug (lib/speakerSlugs.ts의 koreanToSlug과 동일)
function koreanToSlug(name) {
  if (/^[a-zA-Z0-9_-]+$/.test(name)) return name.toLowerCase();
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = ((hash << 5) - hash) + name.charCodeAt(i);
    hash |= 0;
  }
  return `speaker-${Math.abs(hash).toString(36)}`;
}

function speakerToSlug(name) {
  return SPEAKER_SLUGS[name] || koreanToSlug(name);
}

(async () => {
  const supabase = createClient(
    env.NEXT_PUBLIC_SUPABASE_URL,
    env.SUPABASE_SERVICE_ROLE_KEY || env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  );

  // 1) speakers 테이블에서 화자명
  const { data: speakerData, error: speakerErr } = await supabase
    .from('speakers')
    .select('name')
    .limit(1000);

  if (speakerErr) {
    console.error('Supabase error (speakers):', speakerErr.message);
    process.exit(1);
  }

  const speakerNames = speakerData.map(d => d.name).filter(Boolean);

  // 2) speaker_id가 null인 시그널 → 채널명을 화자로 사용하는 케이스
  //    프론트엔드가 channel_name으로 speakerToSlug() 호출하여 링크 생성
  const { data: channelData } = await supabase
    .from('influencer_channels')
    .select('channel_name')
    .limit(100);

  const channelNames = (channelData || []).map(d => d.channel_name).filter(Boolean);

  const names = [...new Set([...speakerNames, ...channelNames])].sort();
  console.log(`[INFO] speakers: ${speakerNames.length}명, channels: ${channelNames.length}개`);

  // slug 목록 생성 (매핑 + 해시 모두 포함)
  const slugEntries = names.map(name => ({
    name,
    slug: speakerToSlug(name)
  }));

  // slug → name 역매핑 (가장 짧은 이름 우선)
  const slugToName = {};
  slugEntries.forEach(({ name, slug }) => {
    if (!slugToName[slug] || name.length < slugToName[slug].length) {
      slugToName[slug] = name;
    }
  });

  // 저장: { slug: name } 형태 (역매핑 포함)
  const outPath = path.join(__dirname, '..', 'data', 'speaker_slugs.json');
  fs.writeFileSync(outPath, JSON.stringify(slugToName, null, 2), 'utf-8');

  console.log(`[OK] data/speaker_slugs.json 생성: ${Object.keys(slugToName).length}개 slug`);

  // 매핑 안 된 화자 리포트
  const unmapped = slugEntries.filter(e => !SPEAKER_SLUGS[e.name]);
  if (unmapped.length > 0) {
    console.log(`[INFO] 매핑 없는 화자 ${unmapped.length}명 (hash slug 사용):`);
    unmapped.forEach(e => console.log(`  ${e.name} → ${e.slug}`));
  }
})();
