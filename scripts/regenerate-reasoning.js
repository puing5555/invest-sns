const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '.env.local' });

// Supabase 클라이언트 설정
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

// Anthropic API 키
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

// 딜레이 함수
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function callAnthropicAPI(prompt) {
  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 200,
        messages: [{
          role: 'user',
          content: prompt
        }]
      })
    });

    if (!response.ok) {
      throw new Error(`API 호출 실패: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data.content[0].text.trim();
  } catch (error) {
    console.error('Anthropic API 호출 오류:', error);
    throw error;
  }
}

async function generateReasoning(stock, signal, keyQuote, subtitleText) {
  const subtitle = subtitleText ? subtitleText.substring(0, 2000) : '';
  
  const prompt = `다음 투자 시그널의 분석 근거(reasoning)를 작성하라. 80~150자. 왜 이 시그널 타입(매수/긍정/중립/경계/매도)으로 분류했는지, 발언자의 핵심 논거를 구체적으로. 종목: ${stock}, 시그널: ${signal}, 핵심발언: ${keyQuote}${subtitle ? `, 자막(앞 2000자): ${subtitle}` : ''}`;

  return await callAnthropicAPI(prompt);
}

async function main() {
  console.log('reasoning 재생성 작업을 시작합니다...');

  try {
    // 1. influencer_signals에서 모든 시그널 조회 후 80자 미만 필터링
    console.log('1. reasoning이 80자 미만인 시그널을 조회합니다...');
    
    const { data: signals, error: signalsError } = await supabase
      .from('influencer_signals')
      .select('id, stock, ticker, signal, confidence, key_quote, reasoning, video_id')
      .order('id');

    if (signalsError) {
      throw new Error(`시그널 조회 오류: ${signalsError.message}`);
    }

    // reasoning 길이가 80자 미만인 것들 필터링
    const shortReasoningSignals = signals.filter(signal => 
      !signal.reasoning || signal.reasoning.length < 80
    );

    console.log(`총 ${signals.length}개 시그널 중 ${shortReasoningSignals.length}개가 80자 미만입니다.`);

    let successCount = 0;
    let failCount = 0;

    // 5개씩 배치 처리
    for (let i = 0; i < shortReasoningSignals.length; i += 5) {
      const batch = shortReasoningSignals.slice(i, i + 5);
      
      console.log(`\n배치 ${Math.floor(i/5) + 1}/${Math.ceil(shortReasoningSignals.length/5)} 처리 중... (${i + 1}-${Math.min(i + 5, shortReasoningSignals.length)})`);

      for (const signal of batch) {
        try {
          // 2. video_id로 subtitle_text 조회
          let subtitleText = null;
          if (signal.video_id) {
            const { data: video, error: videoError } = await supabase
              .from('influencer_videos')
              .select('subtitle_text')
              .eq('id', signal.video_id)
              .single();

            if (!videoError && video) {
              subtitleText = video.subtitle_text;
            }
          }

          // 3. Anthropic API 호출하여 reasoning 생성
          console.log(`  시그널 ${signal.id} (${signal.stock}) 처리 중...`);
          
          const newReasoning = await generateReasoning(
            signal.stock,
            signal.signal,
            signal.key_quote,
            subtitleText
          );

          // 4. reasoning 업데이트
          const { error: updateError } = await supabase
            .from('influencer_signals')
            .update({ reasoning: newReasoning })
            .eq('id', signal.id);

          if (updateError) {
            throw new Error(`업데이트 오류: ${updateError.message}`);
          }

          console.log(`  ✅ 완료: ${newReasoning.substring(0, 50)}...`);
          successCount++;

        } catch (error) {
          console.error(`  ❌ 시그널 ${signal.id} 처리 실패:`, error.message);
          failCount++;
        }
      }

      // 배치 간 2초 딜레이
      if (i + 5 < shortReasoningSignals.length) {
        console.log('  2초 대기 중...');
        await delay(2000);
      }
    }

    console.log('\n=== 작업 완료 ===');
    console.log(`성공: ${successCount}건`);
    console.log(`실패: ${failCount}건`);
    console.log(`총 처리: ${successCount + failCount}건`);

  } catch (error) {
    console.error('작업 중 오류 발생:', error);
    process.exit(1);
  }
}

main();