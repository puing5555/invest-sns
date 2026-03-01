import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const { reportId, action } = await req.json();
    
    if (!reportId) {
      return new Response(JSON.stringify({ error: "reportId is required" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const anthropicKey = Deno.env.get("ANTHROPIC_API_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    // 1. 신고 데이터 조회
    const { data: report, error: reportError } = await supabase
      .from("signal_reports")
      .select(`
        *,
        influencer_signals (
          id, stock, ticker, signal, key_quote, timestamp, reasoning,
          influencer_videos (
            subtitle_text, title, published_at
          )
        )
      `)
      .eq("id", reportId)
      .single();

    if (reportError || !report) {
      return new Response(JSON.stringify({ error: "신고 데이터를 찾을 수 없습니다." }), {
        status: 404,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const signal = report.influencer_signals;
    const subtitleText = signal?.influencer_videos?.subtitle_text;

    if (!subtitleText) {
      return new Response(JSON.stringify({ error: "자막 데이터가 없습니다." }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // 2. AI 검토 요청
    const reviewPrompt = `원본 자막과 시그널을 비교해서 신고 사유가 타당한지 검토해 주세요.

**원본 자막:**
${subtitleText}

**추출된 시그널:**
- 종목: ${signal.stock} (${signal.ticker || "N/A"})
- 신호: ${signal.signal}
- 인용문: ${signal.key_quote}
- 타임스탬프: ${signal.timestamp}
- 분석근거: ${signal.reasoning || "N/A"}

**신고 정보:**
- 신고 사유: ${report.reason}
- 상세 내용: ${report.detail || "없음"}

**검토 기준:**
1. 인용문이 실제 자막과 일치하는가?
2. 시그널 타입이 발언 내용과 일치하는가?
3. 타임스탬프가 정확한가?
4. 분석근거가 합리적인가?

**결과 형식:**
상태: [수정필요/문제없음]
근거: [구체적인 근거 설명]`;

    const aiReview = await callAnthropic(anthropicKey, reviewPrompt, 1000);

    // 3. 검토 결과 저장
    await supabase.from("signal_reports").update({
      ai_review: aiReview,
      updated_at: new Date().toISOString(),
    }).eq("id", reportId);

    // 4. "수정필요"인 경우 수정안 생성
    let aiSuggestion = null;
    if (aiReview.includes("수정필요") || aiReview.includes("수정 필요")) {
      const suggestionPrompt = `이전 검토 결과에 따라 수정된 시그널을 JSON 형태로 생성해 주세요.

**원본 자막:**
${subtitleText}

**기존 시그널:**
- 종목: ${signal.stock}
- 티커: ${signal.ticker}
- 신호: ${signal.signal}
- 인용문: ${signal.key_quote}
- 타임스탬프: ${signal.timestamp}
- 분석근거: ${signal.reasoning}

**검토 결과:**
${aiReview}

**수정안을 다음 JSON 형식으로 제공해 주세요:**
{
  "stock": "종목명",
  "ticker": "티커 또는 null",
  "signal": "매수|긍정|중립|경계|매도",
  "quote": "정확한 인용문",
  "timestamp": "MM:SS",
  "analysis_reasoning": "수정된 분석근거"
}

JSON만 출력하고 다른 설명은 하지 마세요.`;

      try {
        aiSuggestion = await callAnthropic(anthropicKey, suggestionPrompt, 500);
        await supabase.from("signal_reports").update({
          ai_suggestion: aiSuggestion,
          updated_at: new Date().toISOString(),
        }).eq("id", reportId);
      } catch (e) {
        console.error("수정안 생성 실패:", e);
      }
    }

    return new Response(
      JSON.stringify({ success: true, ai_review: aiReview, ai_suggestion: aiSuggestion }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("AI review error:", error);
    return new Response(
      JSON.stringify({ error: error.message || "알 수 없는 오류가 발생했습니다." }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});

async function callAnthropic(apiKey: string, prompt: string, maxTokens: number): Promise<string> {
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: maxTokens,
      messages: [{ role: "user", content: prompt }],
    }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Anthropic API error (${response.status}): ${err}`);
  }

  const data = await response.json();
  return data.content[0].text;
}
