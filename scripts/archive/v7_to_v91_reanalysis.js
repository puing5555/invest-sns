const {createClient} = require('@supabase/supabase-js');
const sb = createClient(
  'https://arypzhotxflimroprmdk.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8'
);

// Speaker IDs
const S = {
  배재원: '7fef30a4-a248-44d6-99b9-02bda6f47eb2',
  고연수: '3508abce-70e0-4eaa-a0d4-686b61071dd9',
  김장년: '03baa455-178d-4a82-bf47-6a12ccc2b694',
  김동훈: '5783838f-af5f-4e74-bcbf-bbc20141b199',
  박지훈: 'e59ed6f5-7a8d-4111-af1c-502ad3344e79',
  박병창: '2720d0ee-b7e2-4006-80df-90bc9de07797',
  장우진: 'aa25b0e6-aadf-4bae-a2fa-afc0a067e315',
  이건희: '731fe32d-f47a-432f-9899-305915138983',
  김장열: '8234cd75-1d0d-458c-b01c-62080c7d91e3',
  박명성: '5d03d08f-abb4-453b-bf86-40e57a0ddfdb',
};

// Full video UUIDs will be fetched from DB
const ytIds = ['R6w3T3eUVIs','hxpOT8n_ICw','-US4r1E1kOQ','XFHD_1M3Mxg','ldT75QwBB6g','x0TKvrIdIwI','8-hYd-8eojE','qYAiv0Kljas','irK0YCnox78','I4Tt3tevuTU'];

// V9.1 Signals per video (yt_id -> signals array)
const signalsByYt = {
  // 1. 배재원 - 삼성전자/코스피
  'R6w3T3eUVIs': [
    { speaker: S.배재원, stock: '삼성전자', ticker: '005930', market: 'KR', mention_type: '결론', signal: '매수', confidence: 'high', timestamp: '7:00', key_quote: '비중이 없는 분은 지금이라도 물리더라도 들어가야 된다... 바라보지만 말고 일단 포지션을 넣고 거기서 대응을 해야 된다' },
  ],

  // 2. 고연수 - 증권섹터
  'hxpOT8n_ICw': [
    { speaker: S.고연수, stock: 'NH투자증권', ticker: '005940', market: 'KR', mention_type: '결론', signal: '긍정', confidence: 'high', timestamp: '6:47', key_quote: '배당이랑 실적 성장 둘 다 가져갈 수 있다, DPS는 전년 대비 20% 성장' },
    { speaker: S.고연수, stock: '삼성증권', ticker: '016360', market: 'KR', mention_type: '결론', signal: '긍정', confidence: 'high', timestamp: '7:12', key_quote: 'DPS가 전년 대비 30% 이상 증가할 것으로 예상, 배당 수익률 4% 후반' },
    { speaker: S.고연수, stock: '한국금융지주', ticker: '071050', market: 'KR', mention_type: '결론', signal: '매수', confidence: 'high', timestamp: '7:58', key_quote: '한국 금융 지주랑 키움 증권을 추천드리고 있는데요... 지난해도 연간 2조원 순익 달성' },
    { speaker: S.고연수, stock: '키움증권', ticker: '039490', market: 'KR', mention_type: '결론', signal: '매수', confidence: 'high', timestamp: '8:14', key_quote: '키움 증권 같은 경우에도 전년 대비 순익이 20% 성장할 것으로 예상' },
  ],

  // 3. 김장년 - 메모리반도체/엔비디아
  '-US4r1E1kOQ': [
    { speaker: S.김장년, stock: '엔비디아', ticker: 'NVDA', market: 'US', mention_type: '결론', signal: '긍정', confidence: 'high', timestamp: '4:37', key_quote: '갖고 계신 분면 그냥 갖고 계시면 되고요. 안 갖고 계신 분이라면 2%면 들어가도 괜찮을 것 같아' },
    { speaker: S.김장년, stock: '삼성전자', ticker: '005930', market: 'KR', mention_type: '결론', signal: '매수', confidence: 'high', timestamp: '13:28', key_quote: '우선순은 메모리... 하이닉 삼성전자, 샌디스크, 마이크론 넷 중에 하나는 갖고 있어야지' },
    { speaker: S.김장년, stock: 'SK하이닉스', ticker: '000660', market: 'KR', mention_type: '논거', signal: '긍정', confidence: 'high', timestamp: '11:17', key_quote: '하이닉스랑 마이크론이랑 삼성전자 비중 거의 30% 정도로 된 ETF를 사세요' },
    { speaker: S.김장년, stock: '마이크론', ticker: 'MU', market: 'US', mention_type: '논거', signal: '긍정', confidence: 'high', timestamp: '9:08', key_quote: '마이크론하고 샌디스크 비슷하 11배... 미국 평균보다 반이잖아요' },
  ],

  // 4. 김동훈 - 신세계/삼성전자
  'XFHD_1M3Mxg': [
    { speaker: S.김동훈, stock: '신세계', ticker: '004170', market: 'KR', mention_type: '결론', signal: '매수', confidence: 'high', timestamp: '1:00', key_quote: '신세계가 여전히 저렴하다고 보는 상황입니다. 추가 상승 여력이 있다' },
    { speaker: S.김동훈, stock: '삼성전자', ticker: '005930', market: 'KR', mention_type: '논거', signal: '긍정', confidence: 'high', timestamp: '16:02', key_quote: '여전히 너무 저렴한 거 같습니다. 이익 전망치가 개선되고 있다' },
  ],

  // 5. 박지훈 - 효성중공업 외
  'ldT75QwBB6g': [
    { speaker: S.박지훈, stock: '효성중공업', ticker: '298040', market: 'KR', mention_type: '결론', signal: '매수', confidence: 'very_high', timestamp: '16:46', key_quote: '올해도 계속 한다... 효중이 대장으로 치고 나갈 가능성이 매우 크다' },
    { speaker: S.박지훈, stock: 'HD현대일렉트릭', ticker: '267260', market: 'KR', mention_type: '결론', signal: '긍정', confidence: 'high', timestamp: '19:06', key_quote: 'HD 현대력도 모멘텀에 뭐가 있냐면 올해 드디어 유럽의 수주를 선점' },
    { speaker: S.박지훈, stock: 'LG화학', ticker: '051910', market: 'KR', mention_type: '결론', signal: '매수', confidence: 'high', timestamp: '36:26', key_quote: 'LG화학 강력 추천드리는 바입니다... 행동주의 펀드들이 열받아 있다' },
    { speaker: S.박지훈, stock: '솔브레인', ticker: '357780', market: 'KR', mention_type: '결론', signal: '긍정', confidence: 'medium', timestamp: '28:23', key_quote: '소재단은 꼭 하나 정도는 들고 가셨으면 좋겠습니다. 솔브레인 27년부터 본격화' },
    { speaker: S.박지훈, stock: 'NC소프트', ticker: '036570', market: 'KR', mention_type: '결론', signal: '긍정', confidence: 'medium', timestamp: '33:28', key_quote: '홀딩하셔도 되겠다. YoY 2142% 성장 예상... 바닥에서 야금야금 올라가는 이유가 설명' },
    { speaker: S.박지훈, stock: '하이브', ticker: '352820', market: 'KR', mention_type: '결론', signal: '긍정', confidence: 'high', timestamp: '34:09', key_quote: '홀딩 의견 강력하게 말씀드리고 싶고... 어닝이 확인되면 충분히 다시 점핑할 가능성' },
  ],

  // 6. 박병창 - 반도체/비반도체
  'x0TKvrIdIwI': [
    { speaker: S.박병창, stock: '삼성전자', ticker: '005930', market: 'KR', mention_type: '결론', signal: '긍정', confidence: 'high', timestamp: '6:00', key_quote: '삼성전자 목표 주가 34만원 나왔다. 밸류업 관련 프로그램 발표 기대' },
    { speaker: S.박병창, stock: 'SK하이닉스', ticker: '000660', market: 'KR', mention_type: '결론', signal: '긍정', confidence: 'high', timestamp: '6:34', key_quote: 'SK하이닉스 시총 725조에 올해 영업이익 160조면 5배도 안 돼. 내년 더 올라가면 세배이 안 되는 거' },
    { speaker: S.박병창, stock: '엔비디아', ticker: 'NVDA', market: 'US', mention_type: '결론', signal: '중립', confidence: 'high', timestamp: '15:14', key_quote: '주가는 70% 이상 반영을 하고서 움직였을 가능성이 있다. 새로운게 나와야 된다. 실적이 아니라 새로운 모멘텀을 기다리는 부분' },
  ],

  // 7. 장우진 - 현대차
  '8-hYd-8eojE': [
    { speaker: S.장우진, stock: '엔비디아', ticker: 'NVDA', market: 'US', mention_type: '결론', signal: '긍정', confidence: 'high', timestamp: '16:35', key_quote: '성장률이 66.7%가 나오고 있기 때문에 엔비디아 주가가 버틴 이유... 27년까지 60% 성장률이면 올해 실적 가지고 걱정할 건 전혀 없다' },
  ],

  // 8. 이건희/김장열 - 현대차/현대건설/SK하이닉스
  'qYAiv0Kljas': [
    { speaker: S.이건희, stock: '현대차', ticker: '005380', market: 'KR', mention_type: '결론', signal: '매수', confidence: 'high', timestamp: '14:00', key_quote: '현대차 지금이라도 사야 돼요라고 물어보면 저는 예스. 의미 있는 거래량을 터트렸다는 거는 한 2, 3일이 쉬더라도 다시 고점을 뚫겠다' },
    { speaker: S.김장열, stock: '삼성전자', ticker: '005930', market: 'KR', mention_type: '결론', signal: '긍정', confidence: 'high', timestamp: '19:25', key_quote: '리레이팅 된 거 없다. 이익 전망 따라간 거. 밸류에이션 상으로 부담되지는 않는다' },
    { speaker: S.김장열, stock: 'SK하이닉스', ticker: '000660', market: 'KR', mention_type: '논거', signal: '긍정', confidence: 'high', timestamp: '16:56', key_quote: '삼성전자 하이닉스 더블 됐어. 이익 전망도 더블 오르고 주가도 더블 오르고. 리레이팅 없다' },
  ],

  // 9. 김장열 - 삼성전자
  'irK0YCnox78': [
    { speaker: S.김장열, stock: '삼성전자', ticker: '005930', market: 'KR', mention_type: '결론', signal: '긍정', confidence: 'high', timestamp: '1:55', key_quote: '삼성전자 밸류업 공시가 주총 직후 나오지 않겠냐. 최소한 배당이 전년보다 10% 이상 증가되겠구나 생각할 수 있다' },
    { speaker: S.김장열, stock: '엔비디아', ticker: 'NVDA', market: 'US', mention_type: '리포트', signal: '중립', confidence: 'high', timestamp: '5:36', key_quote: '이 정도는 잘 나올 것으로 예상한 그거에 부합했다는 겁니다. 나쁜게 아니에요. 2, 3% 오르는게 정상' },
  ],

  // 10. 박명성 - 삼성전자
  'I4Tt3tevuTU': [
    { speaker: S.박명성, stock: '삼성전자', ticker: '005930', market: 'KR', mention_type: '결론', signal: '매수', confidence: 'very_high', timestamp: '8:07', key_quote: '모건 스탠리 2027년 삼성전자 영업이익 전세계 1등. 340조원. 2027 포워드 PE 네배밖에 안 돼. 삼성전자는 계속 가도 전혀 이상하지 않은' },
  ],
};

(async () => {
  // 1. Fetch full video UUIDs
  const {data: vids, error: vErr} = await sb.from('influencer_videos').select('id,video_id,pipeline_version,signal_count').in('video_id', ytIds);
  if (vErr) { console.error('Video fetch error:', vErr); return; }
  
  const vidMap = {};
  vids.forEach(v => { vidMap[v.video_id] = v.id; });
  console.log(`Found ${vids.length} videos`);

  // 2. Count existing V7 signals
  const vidUuids = vids.map(v => v.id);
  const {data: oldSigs} = await sb.from('influencer_signals').select('id,video_id').in('video_id', vidUuids).eq('pipeline_version', 'V7');
  const oldCount = oldSigs?.length || 0;
  console.log(`Existing V7 signals to delete: ${oldCount}`);

  // 3. Delete V7 signals
  for (const uuid of vidUuids) {
    const {error} = await sb.from('influencer_signals').delete().eq('video_id', uuid).eq('pipeline_version', 'V7');
    if (error) console.error(`Delete error for ${uuid}:`, error);
  }
  console.log('V7 signals deleted');

  // 4. Insert V9.1 signals
  let totalNew = 0;
  const results = {};
  
  for (const [ytId, signals] of Object.entries(signalsByYt)) {
    const videoUuid = vidMap[ytId];
    if (!videoUuid) { console.error(`No UUID for ${ytId}`); continue; }
    
    const rows = signals.map(s => ({
      video_id: videoUuid,
      speaker_id: s.speaker,
      stock: s.stock,
      ticker: s.ticker,
      market: s.market,
      mention_type: s.mention_type,
      signal: s.signal,
      confidence: s.confidence,
      timestamp: s.timestamp,
      key_quote: s.key_quote,
      pipeline_version: 'V9.1',
      review_status: 'pending',
    }));

    const {data, error} = await sb.from('influencer_signals').insert(rows).select('id');
    if (error) { console.error(`Insert error for ${ytId}:`, error); continue; }
    
    totalNew += rows.length;
    results[ytId] = rows.length;
    console.log(`  ${ytId}: ${rows.length} signals inserted`);
  }

  // 5. Update pipeline_version and signal_count
  for (const [ytId, count] of Object.entries(results)) {
    const videoUuid = vidMap[ytId];
    const {error} = await sb.from('influencer_videos').update({
      pipeline_version: 'V9.1',
      signal_count: count,
      analyzed_at: new Date().toISOString(),
    }).eq('id', videoUuid);
    if (error) console.error(`Update error for ${ytId}:`, error);
  }

  console.log('\n=== RESULTS ===');
  console.log(`V7 signals deleted: ${oldCount}`);
  console.log(`V9.1 signals inserted: ${totalNew}`);
  console.log('\nPer video:');
  for (const [ytId, count] of Object.entries(results)) {
    console.log(`  ${ytId}: ${count} signals`);
  }
  console.log(`\nTotal: ${oldCount} V7 → ${totalNew} V9.1 (${totalNew > oldCount ? '+' : ''}${totalNew - oldCount})`);
})();
