import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

export async function POST(request: NextRequest) {
  try {
    if (!ANTHROPIC_API_KEY) {
      return NextResponse.json(
        { error: 'ANTHROPIC_API_KEY가 설정되지 않았습니다.' }, 
        { status: 500 }
      );
    }

    const { signalId, issueTypes } = await request.json();

    if (!signalId) {
      return NextResponse.json(
        { error: 'signalId가 필요합니다.' }, 
        { status: 400 }
      );
    }

    // 1. 시그널 데이터 조회 (자막 포함)
    const { data: signalData, error: signalError } = await supabase
      .from('influencer_signals')
      .select(`
        *,
        influencer_videos (
          subtitle_text,
          title,
          published_at
        )
      `)
      .eq('id', signalId)
      .single();

    if (signalError || !signalData) {
      return NextResponse.json(
        { error: '시그널 데이터를 찾을 수 없습니다.' }, 
        { status: 404 }
      );
    }

    if (!signalData.influencer_videos?.subtitle_text) {
      return NextResponse.json(
        { error: '자막 데이터가 없습니다.' }, 
        { status: 400 }
      );
    }

    // 2. AI 개선 요청
    const subtitleText = signalData.influencer_videos.subtitle_text;
    const issueDescription = issueTypes.join(', ');

    const improvePrompt = `
품질 이슈가 발견된 시그널을 개선해 주세요.

**원본 자막:**
${subtitleText}

**기존 시그널:**
- 종목: ${signalData.stock} (${signalData.ticker || 'N/A'})
- 신호: ${signalData.signal}
- 인용문: ${signalData.key_quote || 'null'}
- 타임스탬프: ${signalData.timestamp || 'N/A'}
- 분석근거: ${signalData.analysis_reasoning || 'null'}
- 신뢰도: ${signalData.confidence || 'null'}

**발견된 품질 이슈:**
${issueDescription}

**개선 지침:**
1. 분석근거 부족: 자막을 바탕으로 최소 20자 이상의 구체적인 분석근거 작성
2. 인용문 부족: 자막에서 정확한 핵심 발언을 15자 이상 인용
3. 신뢰도 누락: 1-100 점수로 신뢰도 평가
4. 시그널 타입은 반드시 한글 5단계만 사용: 매수/긍정/중립/경계/매도

**개선안을 다음 JSON 형식으로 제공해 주세요:**
{
  "stock": "종목명",
  "ticker": "티커 또는 null",
  "signal": "매수|긍정|중립|경계|매도",
  "quote": "정확한 인용문 (15자 이상)",
  "timestamp": "MM:SS",
  "analysis_reasoning": "구체적인 분석근거 (20자 이상)",
  "confidence": 85
}

JSON만 출력하고 다른 설명은 하지 마세요.
`;

    const anthropicResponse = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 800,
        messages: [
          {
            role: 'user',
            content: improvePrompt
          }
        ]
      })
    });

    if (!anthropicResponse.ok) {
      throw new Error(`Anthropic API 오류: ${anthropicResponse.status}`);
    }

    const anthropicData = await anthropicResponse.json();
    const improvementSuggestion = anthropicData.content[0].text;

    return NextResponse.json({
      success: true,
      improvement: improvementSuggestion,
      originalSignal: {
        stock: signalData.stock,
        ticker: signalData.ticker,
        signal: signalData.signal,
        quote: signalData.key_quote,
        timestamp: signalData.timestamp,
        analysis_reasoning: signalData.analysis_reasoning,
        confidence: signalData.confidence
      }
    });

  } catch (error) {
    console.error('AI 개선 API 오류:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.' }, 
      { status: 500 }
    );
  }
}