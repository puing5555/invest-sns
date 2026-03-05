const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '.env.local' });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

const CONCURRENCY = 3;
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function callAnthropicAPI(prompt, retries = 2) {
  for (let attempt = 0; attempt <= retries; attempt++) {
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
          messages: [{ role: 'user', content: prompt }]
        })
      });

      if (response.status === 429) {
        const wait = Math.pow(2, attempt) * 5000;
        console.log(`    ⚠️ Rate limit, ${wait/1000}s 대기...`);
        await delay(wait);
        continue;
      }

      if (!response.ok) {
        throw new Error(`API ${response.status}`);
      }

      const data = await response.json();
      return data.content[0].text.trim();
    } catch (error) {
      if (attempt === retries) throw error;
      await delay(2000);
    }
  }
}

async function processSignal(signal, index, total) {
  try {
    let subtitleText = null;
    if (signal.video_id) {
      const { data: video } = await supabase
        .from('influencer_videos')
        .select('subtitle_text')
        .eq('id', signal.video_id)
        .single();
      if (video) subtitleText = video.subtitle_text;
    }

    const subtitle = subtitleText ? subtitleText.substring(0, 2000) : '';
    const prompt = `다음 투자 시그널의 분석 근거(reasoning)를 작성하라. 80~150자. 왜 이 시그널 타입(매수/긍정/중립/부정/매도)으로 분류했는지, 발언자의 핵심 논거를 구체적으로. 종목: ${signal.stock}, 시그널: ${signal.signal}, 핵심발언: ${signal.key_quote}${subtitle ? `, 자막(앞 2000자): ${subtitle}` : ''}`;

    const newReasoning = await callAnthropicAPI(prompt);

    const { error } = await supabase
      .from('influencer_signals')
      .update({ reasoning: newReasoning })
      .eq('id', signal.id);

    if (error) throw new Error(error.message);

    console.log(`  ✅ ${index+1}/${total}: ${signal.stock} (${signal.signal}) - ${newReasoning.length}자`);
    return true;
  } catch (err) {
    console.error(`  ❌ ${index+1}/${total}: ${signal.stock} - ${err.message}`);
    return false;
  }
}

async function main() {
  const startTime = Date.now();
  console.log(`병렬 reasoning 재생성 (동시 ${CONCURRENCY}개)\n`);

  const { data: signals, error } = await supabase
    .from('influencer_signals')
    .select('id, stock, ticker, signal, confidence, key_quote, reasoning, video_id')
    .order('id');

  if (error) { console.error(error); process.exit(1); }

  const toFix = signals.filter(s => !s.reasoning || s.reasoning.length < 80);
  console.log(`총 ${signals.length}개 중 ${toFix.length}개 처리 필요\n`);

  if (toFix.length === 0) {
    console.log('모두 완료!');
    return;
  }

  // 병렬 처리 - 동시 3개
  let success = 0, fail = 0;
  const queue = [...toFix];
  let idx = 0;

  async function worker(workerId) {
    while (idx < queue.length) {
      const myIdx = idx++;
      const signal = queue[myIdx];
      const ok = await processSignal(signal, myIdx, queue.length);
      if (ok) success++; else fail++;
      // 요청 간 짧은 딜레이
      await delay(500);
    }
  }

  const workers = [];
  for (let i = 0; i < CONCURRENCY; i++) {
    workers.push(worker(i));
  }
  await Promise.all(workers);

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(0);
  console.log(`\n=== 완료 (${elapsed}초) ===`);
  console.log(`성공: ${success}, 실패: ${fail}, 총: ${success + fail}`);
}

main();
