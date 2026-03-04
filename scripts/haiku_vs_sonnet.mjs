import Anthropic from '@anthropic-ai/sdk';

const SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co";
const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A";

const headers = { "apikey": SUPABASE_KEY, "Authorization": `Bearer ${SUPABASE_KEY}` };

async function supaGet(path) {
  const r = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, { headers });
  return r.json();
}

function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function makePrompt(s, title) {
  return `다음 시그널의 품질을 검증하세요.

영상 제목: ${title}
시그널 종목: ${s.stock} (${s.ticker})
시그널 타입: ${s.signal}
핵심 발언: ${s.key_quote}
근거: ${s.reasoning}
confidence: ${s.confidence}

판정 항목 (각각 O 또는 X):
1. 종목관련성: 영상 제목/주제와 시그널 종목이 관련 있는가?
2. 투자의견: key_quote가 해당 종목에 대한 실제 투자 의견(매수/매도/전망)인가? (단순 언급 X)
3. 근거충분: reasoning이 구체적 근거를 포함하는가?

최종판정: ✅정상 / ⚠️의심 / ❌불량

JSON으로만 응답:
{"relevance": "O/X", "opinion": "O/X", "evidence": "O/X", "verdict": "정상/의심/불량", "reason": "한줄 사유"}`;
}

async function callClaude(model, prompt) {
  const client = new Anthropic();
  const r = await client.messages.create({
    model,
    max_tokens: 256,
    messages: [{ role: "user", content: prompt }],
  });
  const text = r.content[0].text;
  const usage = r.usage;
  try {
    const jsonMatch = text.match(/\{[^}]+\}/);
    return { parsed: JSON.parse(jsonMatch[0]), usage };
  } catch {
    return { parsed: { relevance: "?", opinion: "?", evidence: "?", verdict: "오류", reason: text.slice(0, 80) }, usage };
  }
}

async function main() {
  console.log("Fetching signals...");
  const allSignals = await supaGet("influencer_signals?select=id,video_id,stock,ticker,signal,key_quote,reasoning,confidence&limit=1000");
  const picked = shuffle(allSignals).slice(0, 30);
  
  // Get video titles
  const videoIds = [...new Set(picked.map(s => s.video_id))];
  const videos = await supaGet(`influencer_videos?select=id,title&id=in.(${videoIds.join(",")})`);
  const videoMap = Object.fromEntries(videos.map(v => [v.id, v.title]));
  
  console.log(`Processing ${picked.length} signals with ${videoIds.length} unique videos...`);
  
  const HAIKU = "claude-3-haiku-20240307";
  const SONNET = "claude-sonnet-4-20250514";
  
  let totalHaikuIn = 0, totalHaikuOut = 0, totalSonnetIn = 0, totalSonnetOut = 0;
  const results = [];
  
  for (let i = 0; i < picked.length; i++) {
    const s = picked[i];
    const title = videoMap[s.video_id] || "(제목 없음)";
    const prompt = makePrompt(s, title);
    
    console.log(`[${i+1}/30] ${s.stock} (${s.ticker})...`);
    
    const [haiku, sonnet] = await Promise.all([
      callClaude(HAIKU, prompt),
      callClaude(SONNET, prompt),
    ]);
    
    totalHaikuIn += haiku.usage.input_tokens;
    totalHaikuOut += haiku.usage.output_tokens;
    totalSonnetIn += sonnet.usage.input_tokens;
    totalSonnetOut += sonnet.usage.output_tokens;
    
    const match = haiku.parsed.verdict === sonnet.parsed.verdict;
    results.push({ id: s.id, stock: s.stock, ticker: s.ticker, haiku: haiku.parsed, sonnet: sonnet.parsed, match });
  }
  
  // Stats
  const matchCount = results.filter(r => r.match).length;
  const matchRate = ((matchCount / 30) * 100).toFixed(1);
  const haikuCost = (totalHaikuIn * 0.8 + totalHaikuOut * 4) / 1_000_000;
  const sonnetCost = (totalSonnetIn * 3 + totalSonnetOut * 15) / 1_000_000;
  
  // Build markdown
  let md = `# Haiku vs Sonnet 시그널 검증 비교\n\n`;
  md += `**날짜:** 2026-03-04\n`;
  md += `**샘플:** 무작위 30개 시그널\n\n`;
  md += `## 요약\n`;
  md += `- **일치율:** ${matchRate}% (${matchCount}/30)\n`;
  md += `- **Haiku 비용:** $${haikuCost.toFixed(4)} (${totalHaikuIn} in / ${totalHaikuOut} out)\n`;
  md += `- **Sonnet 비용:** $${sonnetCost.toFixed(4)} (${totalSonnetIn} in / ${totalSonnetOut} out)\n`;
  md += `- **비용 비율:** Sonnet은 Haiku의 ${(sonnetCost / haikuCost).toFixed(1)}배\n\n`;
  
  md += `## 비교표\n\n`;
  md += `| # | 종목 | Haiku판정 | Sonnet판정 | 일치 |\n`;
  md += `|---|------|----------|-----------|------|\n`;
  results.forEach((r, i) => {
    const hv = r.haiku.verdict === "정상" ? "✅정상" : r.haiku.verdict === "의심" ? "⚠️의심" : "❌불량";
    const sv = r.sonnet.verdict === "정상" ? "✅정상" : r.sonnet.verdict === "의심" ? "⚠️의심" : "❌불량";
    md += `| ${i+1} | ${r.stock} (${r.ticker}) | ${hv} | ${sv} | ${r.match ? "✅" : "❌"} |\n`;
  });
  
  // Disagreements
  const disagrees = results.filter(r => !r.match);
  if (disagrees.length > 0) {
    md += `\n## 불일치 상세 (${disagrees.length}건)\n\n`;
    disagrees.forEach(r => {
      md += `### ${r.stock} (${r.ticker}) - ID: ${r.id}\n`;
      md += `- **Haiku:** ${r.haiku.verdict} - ${r.haiku.reason}\n`;
      md += `  - 관련성:${r.haiku.relevance} 의견:${r.haiku.opinion} 근거:${r.haiku.evidence}\n`;
      md += `- **Sonnet:** ${r.sonnet.verdict} - ${r.sonnet.reason}\n`;
      md += `  - 관련성:${r.sonnet.relevance} 의견:${r.sonnet.opinion} 근거:${r.sonnet.evidence}\n\n`;
    });
  }
  
  // Verdict distribution
  md += `\n## 판정 분포\n\n`;
  for (const model of ["haiku", "sonnet"]) {
    const counts = { "정상": 0, "의심": 0, "불량": 0, "오류": 0 };
    results.forEach(r => { counts[r[model].verdict] = (counts[r[model].verdict] || 0) + 1; });
    md += `**${model === "haiku" ? "Haiku" : "Sonnet"}:** 정상 ${counts["정상"]} / 의심 ${counts["의심"]} / 불량 ${counts["불량"]}${counts["오류"] ? ` / 오류 ${counts["오류"]}` : ""}\n`;
  }
  
  // Write file
  const fs = await import('fs');
  fs.writeFileSync("C:\\Users\\Mario\\work\\invest-sns\\data\\haiku_vs_sonnet_validation.md", md);
  
  // Output summary for telegram
  console.log("\n=== TELEGRAM ===");
  console.log(`🔍 [QA] Haiku vs Sonnet 검증 비교: 일치율 ${matchRate}%, Haiku $${haikuCost.toFixed(4)} vs Sonnet $${sonnetCost.toFixed(4)}`);
  console.log("=== DONE ===");
}

main().catch(e => { console.error(e); process.exit(1); });
