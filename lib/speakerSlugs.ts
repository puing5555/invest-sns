// Speaker name ↔ English slug mapping
const SPEAKER_SLUGS: Record<string, string> = {
  '이효석': 'lee-hyoseok',
  '조진표': 'cho-jinpyo',
  '코린이아빠': 'korini-appa',
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
};

const SLUG_TO_SPEAKER: Record<string, string> = {};
Object.entries(SPEAKER_SLUGS).forEach(([name, slug]) => {
  SLUG_TO_SPEAKER[slug] = name;
});

export function speakerToSlug(name: string): string {
  return SPEAKER_SLUGS[name] || encodeURIComponent(name);
}

export function slugToSpeaker(slug: string): string | null {
  return SLUG_TO_SPEAKER[slug] || null;
}

export function getAllSpeakerSlugs(): string[] {
  return Object.values(SPEAKER_SLUGS);
}

export function getAllSpeakers(): { name: string; slug: string }[] {
  return Object.entries(SPEAKER_SLUGS).map(([name, slug]) => ({ name, slug }));
}
