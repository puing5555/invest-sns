// 코린이 아빠 시그널 11개 INSERT (v3 스키마)
const SUPABASE_URL = 'https://arypzhotxflimroprmdk.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A';

const headers = {
  'apikey': SUPABASE_KEY,
  'Authorization': `Bearer ${SUPABASE_KEY}`,
  'Content-Type': 'application/json',
  'Prefer': 'return=representation'
};

async function query(table, params = '') {
  const r = await fetch(`${SUPABASE_URL}/rest/v1/${table}?${params}`, { headers });
  if (!r.ok) throw new Error(`GET ${table}: ${r.status} ${await r.text()}`);
  return r.json();
}

async function insert(table, data) {
  const r = await fetch(`${SUPABASE_URL}/rest/v1/${table}`, {
    method: 'POST', headers: { ...headers, 'Prefer': 'return=representation,resolution=merge-duplicates' }, body: JSON.stringify(data)
  });
  if (!r.ok) throw new Error(`INSERT ${table}: ${r.status} ${await r.text()}`);
  return r.json();
}

async function main() {
  // 1. Get speaker_id for 코린이 아빠
  const speakers = await query('speakers', 'name=eq.코린이 아빠');
  if (!speakers.length) throw new Error('코린이 아빠 speaker not found');
  const speakerId = speakers[0].id;
  console.log('speaker_id:', speakerId);

  // 2. Get channel_id for 코린이 아빠
  const channels = await query('influencer_channels', 'channel_handle=eq.@corinpapa1106');
  if (!channels.length) throw new Error('코린이 아빠 channel not found');
  const channelId = channels[0].id;
  console.log('channel_id:', channelId);

  // 3. Insert 11 videos
  const videoData = [
    { video_id: '82TEaq8GIfc', title: '캔톤, 업비트 상장 초읽기' },
    { video_id: 'PGQW7nyoRRI', title: '캔톤이 기관 전용 코인?' },
    { video_id: 'XxlsTMRDR_o', title: '비트코인 에너지 흡수하는 캔톤' },
    { video_id: 'pRTYEzspqyU', title: '이더 에너지 흡수하는 캔톤' },
    { video_id: 'IiPJSJ42H4o', title: '리플 에너지 흡수하는 캔톤' },
    { video_id: 'awXkJ9hK-a0', title: '캔톤이 다크코인?' },
    { video_id: 'TjKVuAGhC1M', title: '명료법 무기한 연기의 여파' },
    { video_id: 'Vy2jrX-uCbY', title: 'AI 버블 붕괴에도 캔톤이 살아남는 이유' },
    { video_id: '3eeUC7UBaG4', title: '트럼프 가문과 캔톤 네트워크' },
    { video_id: 'A7qHwvcGh9A', title: '실적이 중요한 거야 바보야' },
    { video_id: '7AaksU-R3dg', title: 'XRP 헤어질 결심' },
  ].map(v => ({
    channel_id: channelId,
    video_id: v.video_id,
    title: v.title,
    has_subtitle: true,
    analyzed_at: new Date().toISOString(),
    pipeline_version: 'V5',
    signal_count: 0
  }));

  const videos = await insert('influencer_videos', videoData);
  console.log(`Inserted ${videos.length} videos`);

  // Build video_id -> uuid map
  const vidMap = {};
  for (const v of videos) vidMap[v.video_id] = v.id;

  // 4. Insert 11 signals (v3 schema: no 'speaker' text column, uses speaker_id)
  const signals = [
    { vid: '82TEaq8GIfc', stock: 'CC', ticker: 'CC', market: 'CRYPTO', mention_type: '결론', signal: '매수', confidence: 'high', timestamp: '05:30', key_quote: '업비트 상장 시간 문제. 삼성이 선택한 건 캔톤', reasoning: '삼성 파트너십+업비트 상장 분석' },
    { vid: 'PGQW7nyoRRI', stock: 'CC', ticker: 'CC', market: 'CRYPTO', mention_type: '결론', signal: '매수', confidence: 'high', timestamp: '04:15', key_quote: '캔톤이 기관 전용? 개인도 쉽게 접근 가능', reasoning: '접근성 개선' },
    { vid: 'XxlsTMRDR_o', stock: 'CC', ticker: 'CC', market: 'CRYPTO', mention_type: '결론', signal: '매수', confidence: 'high', timestamp: '08:20', key_quote: '비트코인 희소성 흡수한 캔톤', reasoning: 'BTC 특성 흡수 기술적 진화' },
    { vid: 'pRTYEzspqyU', stock: 'CC', ticker: 'CC', market: 'CRYPTO', mention_type: '결론', signal: '매수', confidence: 'high', timestamp: '12:45', key_quote: '이더리움 스마트계약 뛰어넘는 캔톤 RWA', reasoning: 'ETH 대비 우위 RWA 선점' },
    { vid: 'IiPJSJ42H4o', stock: 'CC', ticker: 'CC', market: 'CRYPTO', mention_type: '결론', signal: '매수', confidence: 'high', timestamp: '07:10', key_quote: '리플 결제시스템 학습한 캔톤 기관 솔루션', reasoning: 'XRP 벤치마킹 기관 확대' },
    { vid: 'awXkJ9hK-a0', stock: 'CC', ticker: 'CC', market: 'CRYPTO', mention_type: '논거', signal: '긍정', confidence: 'medium', timestamp: '06:35', key_quote: '허가형 블록체인이 미국 정부가 원하는 방향', reasoning: '규제 친화적 구조' },
    { vid: 'TjKVuAGhC1M', stock: 'CC', ticker: 'CC', market: 'CRYPTO', mention_type: '뉴스', signal: '긍정', confidence: 'medium', timestamp: '09:15', key_quote: '코인베이스가 반대하는 이유가 캔톤 위협', reasoning: '경쟁사 견제로 시장 지위 확인' },
    { vid: 'Vy2jrX-uCbY', stock: 'CC', ticker: 'CC', market: 'CRYPTO', mention_type: '결론', signal: '매수', confidence: 'high', timestamp: '10:30', key_quote: 'AI 버블 터져도 캔톤은 실체 있는 솔루션', reasoning: '펀더멘털 기반 안정성' },
    { vid: '3eeUC7UBaG4', stock: 'CC', ticker: 'CC', market: 'CRYPTO', mention_type: '논거', signal: '매수', confidence: 'high', timestamp: '08:45', key_quote: '트럼프 RWA 전략에 캔톤 핵심', reasoning: '정치적 배경+정책 연계' },
    { vid: 'A7qHwvcGh9A', stock: 'BTC', ticker: 'BTC', market: 'CRYPTO', mention_type: '논거', signal: '경계', confidence: 'medium', timestamp: '05:20', key_quote: '실적 없는 코인 정리 시점, 캔톤은 다르다', reasoning: '시장 선별 차별화' },
    { vid: '7AaksU-R3dg', stock: 'XRP', ticker: 'XRP', market: 'CRYPTO', mention_type: '결론', signal: '매도', confidence: 'high', timestamp: '03:45', key_quote: 'XRP 헤어질 시간. 캔톤으로 갈아타야', reasoning: 'XRP→CC 전환 필요' },
  ].map(s => ({
    video_id: vidMap[s.vid],
    speaker_id: speakerId,
    stock: s.stock,
    ticker: s.ticker,
    market: s.market,
    mention_type: s.mention_type,
    signal: s.signal,
    confidence: s.confidence,
    timestamp: s.timestamp,
    key_quote: s.key_quote,
    reasoning: s.reasoning,
    pipeline_version: 'V5',
    review_status: 'approved'
  }));

  const inserted = await insert('influencer_signals', signals);
  console.log(`Inserted ${inserted.length} signals`);

  // 5. Verify
  const total = await query('influencer_signals', 'select=id&speaker_id=eq.' + speakerId);
  console.log(`Total 코린이 아빠 signals in DB: ${total.length}`);
}

main().catch(e => { console.error(e); process.exit(1); });
