// Speaker name ↔ English slug mapping
const SPEAKER_SLUGS: Record<string, string> = {
  '이효석': 'lee-hyoseok',
  '조진표': 'cho-jinpyo',
  '코린이아빠': 'korini-appa',
  '코린이 아빠': 'korini-appa',
  '박지훈': 'park-jihoon',
  '배재원': 'bae-jaewon',
  '김동훈': 'kim-donghoon',
  '김장년': 'kim-jangnyeon',
  '고연수': 'ko-yeonsu',
  '이건희': 'lee-gunhee',
  '장우진': 'jang-woojin',
  '김장열': 'kim-jangyeol',
  '박병창': 'park-byungchang',
  '박명성': 'park-myungsung',
  '달란트투자': 'dalant-invest',
  'syuka': 'syuka',
  '이영수': 'lee-youngsu',
  '이정윤': 'lee-jungyoon',
  '배재규': 'bae-jaegyu',
  '배제기': 'bae-jegi',
  '김학주': 'kim-hakju',
};

// 한글 → hash 기반 slug (매핑에 없는 발언자 fallback용)
function koreanToSlug(name: string): string {
  if (/^[a-zA-Z0-9_-]+$/.test(name)) return name.toLowerCase();
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = ((hash << 5) - hash) + name.charCodeAt(i);
    hash |= 0;
  }
  return `speaker-${Math.abs(hash).toString(36)}`;
}

// 역방향 매핑 (slug → speaker name)
const SLUG_TO_SPEAKER: Record<string, string> = {};
Object.entries(SPEAKER_SLUGS).forEach(([name, slug]) => {
  SLUG_TO_SPEAKER[slug] = name;
  const hashSlug = koreanToSlug(name);
  if (hashSlug !== slug) SLUG_TO_SPEAKER[hashSlug] = name;
});

export function speakerToSlug(name: string): string {
  return SPEAKER_SLUGS[name] || koreanToSlug(name);
}

export function slugToSpeaker(slug: string): string | null {
  return SLUG_TO_SPEAKER[slug] || null;
}

export function getAllSpeakerSlugs(): string[] {
  return [...new Set(Object.values(SPEAKER_SLUGS))];
}

export function getAllSpeakers(): { name: string; slug: string }[] {
  return Object.entries(SPEAKER_SLUGS).map(([name, slug]) => ({ name, slug }));
}
