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
  '세상학개론': 'sesang101',
  '월가아재': 'wallstreet-uncle',
  '강동진': 'kang-dongjin',
  '강정수': 'kang-jungsu',
  '강하나': 'kang-hana',
  '거스 쿤': 'gus-kuhn',
  '권영화': 'kwon-younghwa',
  '김단테': 'kim-dante',
  '김대식': 'kim-daesik',
  '김도형': 'kim-dohyung',
  '김동환': 'kim-donghwan',
  '김민석': 'kim-minseok',
  '김수헌': 'kim-suheon',
  '김탁': 'kim-tak',
  '김현지': 'kim-hyunji',
  '김효식': 'kim-hyosik',
  '맹성준': 'maeng-sungjun',
  '박성진': 'park-sungjin',
  '박세익': 'park-seik',
  '박형근': 'park-hyunggeun',
  '배경율': 'bae-kyungyul',
  '배상수': 'bae-sangsu',
  '백수전': 'baek-sujeon',
  '변우철': 'byun-woochul',
  '송종호': 'song-jongho',
  '슈카': 'syuka',
  '슈카월드': 'syuka-world',
  '신형관': 'shin-hyunggwan',
  '안유화': 'ahn-yuhwa',
  '안희철': 'ahn-heechul',
  '양희창': 'yang-heechang',
  '엄민용': 'um-minyong',
  '오종태': 'oh-jongtae',
  '오태민': 'oh-taemin',
  '올랜도 킴': 'orlando-kim',
  '윤수목': 'yoon-sumok',
  '이선엽': 'lee-sunyup',
  '이승우': 'lee-seungwoo',
  '이용재': 'lee-yongjae',
  '이장우': 'lee-jangwoo',
  '이형수': 'lee-hyungsu',
  '장민환': 'jang-minhwan',
  '정주용': 'jung-jooyong',
  '정지훈': 'jung-jihoon',
  '조봉수': 'cho-bongsu',
  '주기영': 'joo-kiyoung',
  '최도연': 'choi-doyeon',
  '최준': 'choi-jun',
  '한정수': 'han-jungsu',
  '홍선애': 'hong-sunae',
  '홍성철': 'hong-sungchul',
  '홍진채': 'hong-jinchae',
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
