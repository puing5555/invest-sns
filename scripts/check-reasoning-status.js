const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '.env.local' });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

async function checkReasoningStatus() {
  console.log('reasoning 상태를 확인합니다...');

  try {
    // 전체 시그널 조회
    const { data: allSignals, error: allError } = await supabase
      .from('influencer_signals')
      .select('id, stock, ticker, signal, confidence, key_quote, reasoning, video_id')
      .order('id');

    if (allError) {
      throw new Error(`전체 시그널 조회 오류: ${allError.message}`);
    }

    console.log(`총 시그널 개수: ${allSignals.length}`);

    // reasoning 상태별 분석
    const nullReasoning = allSignals.filter(s => s.reasoning === null);
    const emptyReasoning = allSignals.filter(s => s.reasoning === '');
    const shortReasoning = allSignals.filter(s => s.reasoning && s.reasoning.length > 0 && s.reasoning.length < 80);
    const validReasoning = allSignals.filter(s => s.reasoning && s.reasoning.length >= 80);

    console.log(`\n=== reasoning 상태 분석 ===`);
    console.log(`null: ${nullReasoning.length}건`);
    console.log(`빈 문자열: ${emptyReasoning.length}건`);
    console.log(`1-79자: ${shortReasoning.length}건`);
    console.log(`80자 이상: ${validReasoning.length}건`);
    
    const needUpdate = nullReasoning.length + emptyReasoning.length + shortReasoning.length;
    console.log(`업데이트 필요: ${needUpdate}건`);

    // 샘플 데이터 출력
    console.log(`\n=== 샘플 데이터 ===`);
    
    if (nullReasoning.length > 0) {
      console.log('\nreasoning이 null인 시그널 (처음 3개):');
      nullReasoning.slice(0, 3).forEach(s => {
        console.log(`  ID: ${s.id}, Stock: ${s.stock}, Signal: ${s.signal}, Reasoning: ${s.reasoning}`);
      });
    }

    if (shortReasoning.length > 0) {
      console.log('\nreasoning이 80자 미만인 시그널 (처음 3개):');
      shortReasoning.slice(0, 3).forEach(s => {
        console.log(`  ID: ${s.id}, Stock: ${s.stock}, Signal: ${s.signal}, Reasoning length: ${s.reasoning.length}, Content: "${s.reasoning}"`);
      });
    }

    if (validReasoning.length > 0) {
      console.log('\nreasoning이 정상인 시그널 (처음 2개):');
      validReasoning.slice(0, 2).forEach(s => {
        console.log(`  ID: ${s.id}, Stock: ${s.stock}, Signal: ${s.signal}, Reasoning length: ${s.reasoning.length}`);
      });
    }

  } catch (error) {
    console.error('확인 중 오류 발생:', error);
  }
}

checkReasoningStatus();