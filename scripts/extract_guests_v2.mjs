
const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8';
const CHANNEL_ID = 'd153b75b-1843-4a99-b49f-c31081a8f566';
const headers = { 'apikey': SUPABASE_KEY, 'Authorization': `Bearer ${SUPABASE_KEY}` };

async function query(path) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, { headers });
  return res.json();
}

// Get all videos
let allVideos = [];
for (let offset = 0; ; offset += 1000) {
  const batch = await query(`influencer_videos?select=id,title,published_at&channel_id=eq.${CHANNEL_ID}&order=published_at.desc&offset=${offset}&limit=1000`);
  allVideos.push(...batch);
  if (batch.length < 1000) break;
}
console.log('Total videos:', allVideos.length);

// Get signal counts
let allSignals = [];
for (let offset = 0; ; offset += 1000) {
  const batch = await query(`influencer_signals?select=video_id&video_id=not.is.null&offset=${offset}&limit=1000`);
  allSignals.push(...batch);
  if (batch.length < 1000) break;
}
const signalCounts = {};
for (const s of allSignals) signalCounts[s.video_id] = (signalCounts[s.video_id] || 0) + 1;

// Korean surname check (common Korean surnames)
const SURNAMES = new Set('김이박최정강조윤장임한오서신권황안송류전홍고문양손배백허유남심노하곽성차주우구신임나전민유진지엄채원천방공강현변함오추도소석선설마길주연방위표명기반왕금옥육인맹제모장남탁국여진어은편구용'.split(''));

function isLikelyKoreanName(str) {
  if (!/^[가-힣]{2,4}$/.test(str)) return false;
  // Check if first char is a common surname
  if (!SURNAMES.has(str[0])) return false;
  // Exclude common non-name words
  const nonNames = new Set(['이것','이번','이런','이제','이후','이전','이유','이상','이하','이미','이렇','이재용','최근','최초','최대','최고','최소','최강','최후','최신','정말','정리','정도','정확','정부','정책','정상','강한','강력','강세','강의','강하','조금','조만','한국','한번','한가','한편','전기','전자','전쟁','전략','전망','전문','전세','전체','전환','임의','장기','장밋','장현','배경','배당','배팅','배터','서프','서비','신기','신제','신저','유동','유리','유일','유전','남은','남아','남겨','심상','심각','노력','노동','노리','하락','하반','하이','하승','곽성','성장','성과','성공','성수','변동','현대','현금','현재','현실','원전','원리','원달','원화','원인','공매','공학','공급','공방','공부','진짜','진출','진행','진땀','도끼','도전','소름','소프','소장','선택','선임','선언','선물','설계','설명','마지','마이','마우','마음','마감','마인','마켓','길래','유사','유튜','유가','유럽','허용','고용','고민','고공','고평','주식','전문가','오리지날','한국은행','원리버','제네럴','스탠포드','엔비디아','비트코인','테슬라','구글','삼성','삼촌','경제센터']);
  if (nonNames.has(str)) return false;
  return true;
}

const TITLE_WORDS = /(?:대표|박사|CIO|CEO|CFO|COO|CTO|이사|본부장|팀장|차장|교수|연구원|연구위원|애널리스트|위원|소장|원장|부장|실장|센터장|전문가|전무|상무|부사장|사장|회장|총괄|디렉터|매니저|파트너|수석|선임|책임|작가|기자|PM|엔지니어|변호사|대표님)/;

function extractGuest(title) {
  if (!title) return null;
  
  // Strategy 1: After separator ㅣ|⎮｜, find "Name Affiliation Title"
  // e.g. "...ㅣ정주용 그래비티벤처스 CIO [1부]"
  // e.g. "...ㅣ강정수 박사 블루닷AI [3부]"
  // e.g. "...⎮IT의 신 이형수 대표"
  
  const sepMatch = title.match(/[ㅣ|⎮｜]/);
  if (sepMatch) {
    const after = title.substring(title.lastIndexOf(sepMatch[0]) + 1).trim();
    // Clean brackets at end
    const cleaned = after.replace(/\[.*?\]$/g, '').trim();
    
    // Find all potential Korean names in this segment
    const words = cleaned.split(/[\s,]+/);
    for (let i = 0; i < words.length; i++) {
      const w = words[i];
      if (isLikelyKoreanName(w) && w !== '이효석') {
        // Check if followed by title word somewhere
        const rest = words.slice(i).join(' ');
        if (TITLE_WORDS.test(rest)) {
          return extractInfo(w, cleaned);
        }
      }
    }
  }
  
  // Strategy 2: "Name Affiliation Title" patterns anywhere with clear markers
  // e.g. "(강사 : 김단테 대표)", "ft. 이름", "w. 이름", "feat. 이름"
  const ftPatterns = [
    /(?:ft\.|feat\.|with\.|w\.)\s*([가-힣]{2,4})\b/i,
    /강사\s*[:：]\s*([가-힣]{2,4})\s/,
  ];
  for (const pat of ftPatterns) {
    const m = title.match(pat);
    if (m && isLikelyKoreanName(m[1]) && m[1] !== '이효석') {
      return extractInfo(m[1], title);
    }
  }
  
  // Strategy 3: Bracketed patterns like "[이정윤 세무사 4부]"
  const bracketMatch = title.match(/[(\[【]([^)\]】]+)[)\]】]/g);
  if (bracketMatch) {
    for (const bm of bracketMatch) {
      const inner = bm.slice(1, -1);
      const bwords = inner.split(/[\s,]+/);
      for (let i = 0; i < bwords.length; i++) {
        if (isLikelyKoreanName(bwords[i]) && bwords[i] !== '이효석') {
          const rest = bwords.slice(i).join(' ');
          if (TITLE_WORDS.test(rest)) {
            return extractInfo(bwords[i], inner);
          }
        }
      }
    }
  }
  
  // Strategy 4: "소속 이름 직함" at end of title (no separator)
  // e.g. "...⎮삼성액티브자산운용 양희창 매니저, 바바리안 리서치 정희석 이사"
  {
    const words = title.split(/[\s,]+/);
    for (let i = 0; i < words.length; i++) {
      if (isLikelyKoreanName(words[i]) && words[i] !== '이효석') {
        // Check next word is a title
        if (i + 1 < words.length && TITLE_WORDS.test(words[i + 1])) {
          return extractInfo(words[i], title);
        }
      }
    }
  }
  
  return null;
}

function extractInfo(name, context) {
  const idx = context.indexOf(name);
  const after = context.substring(idx + name.length).trim()
    .replace(/\[.*?\]/g, '').replace(/\(.*?\)/g, '').trim();
  
  // Extract title word
  const titleMatch = after.match(TITLE_WORDS);
  let title = titleMatch ? titleMatch[0] : '';
  
  // Affiliation is between name and title
  let affiliation = '';
  if (titleMatch) {
    affiliation = after.substring(0, after.indexOf(titleMatch[0])).trim();
  }
  
  // Also check before name for affiliation
  const before = context.substring(0, idx).trim();
  if (!affiliation) {
    // Check if word before name could be affiliation
    const beforeWords = before.split(/[\s,]+/).filter(Boolean);
    if (beforeWords.length > 0) {
      const lastBefore = beforeWords[beforeWords.length - 1];
      // If it looks like an org name (not a common word)
      if (lastBefore.length >= 2 && /[가-힣a-zA-Z]/.test(lastBefore)) {
        // Could be affiliation like "그래비티벤처스", "KT", "SK증권"
        // But be cautious
      }
    }
  }
  
  return { name, affiliation, title };
}

// Process
const guestMap = {};
let guestVideoCount = 0;
let totalAffectedSignals = 0;
const unmatchedWithGuest = []; // titles that seem to have guests but weren't matched

for (const video of allVideos) {
  const result = extractGuest(video.title);
  if (!result) continue;
  
  const { name, affiliation, title } = result;
  
  // Final validation
  if (!isLikelyKoreanName(name)) continue;
  
  guestVideoCount++;
  const sc = signalCounts[video.id] || 0;
  totalAffectedSignals += sc;
  
  if (!guestMap[name]) {
    guestMap[name] = { name, affiliation, title, videos: [], total_signals: 0 };
  }
  if (!guestMap[name].affiliation && affiliation) guestMap[name].affiliation = affiliation;
  if (!guestMap[name].title && title) guestMap[name].title = title;
  
  guestMap[name].videos.push({ video_id: video.id, title: video.title, signal_count: sc });
  guestMap[name].total_signals += sc;
}

const guests = Object.values(guestMap).sort((a, b) => b.videos.length - a.videos.length);

const output = {
  summary: { total_videos: allVideos.length, guest_videos: guestVideoCount, unique_guests: guests.length, total_affected_signals: totalAffectedSignals },
  guests
};

import { writeFileSync, mkdirSync } from 'fs';
mkdirSync('data', { recursive: true });
writeFileSync('data/hs_guest_signals_v2.json', JSON.stringify(output, null, 2), 'utf-8');

console.log('\n=== Summary ===');
console.log(JSON.stringify(output.summary, null, 2));
console.log('\n=== Guests ===');
for (const g of guests) {
  console.log(`${g.name} | ${g.affiliation} ${g.title} | ${g.videos.length}편 | ${g.total_signals} signals`);
  for (const v of g.videos) console.log(`  - ${v.title} (signals: ${v.signal_count})`);
}
