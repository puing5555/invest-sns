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

    const { reportId } = await request.json();

    if (!reportId) {
      return NextResponse.json(
        { error: 'reportId가 필요합니다.' }, 
        { status: 400 }
      );
    }

    // 1. 신고 데이터 조회 (시그널, 자막, 신고 사유 포함)
    const { data: reportData, error: reportError } = await supabase
      .from('signal_reports')
      .select(`
        *,
        influencer_signals (
          id,
          stock,
          ticker,
          signal,
          quote,
          timestamp,
          reasoning,
          influencer_videos (
            subtitle_text,
            title,
            published_at
          )
        )
      `)
      .eq('id', reportId)
      .single();

    if (reportError || !reportData) {
      return NextResponse.json(
        { error: '신고 데이터를 찾을 수 없습니다.' }, 
        { status: 404 }
      );
    }

    if (!reportData.influencer_signals?.influencer_videos?.subtitle_text) {
      return NextResponse.json(
        { error: '자막 데이터가 없습니다.' }, 
        { status: 400 }
      );
    }

    // 2. AI 검토 요청
    const signalData = reportData.influencer_signals;
    const subtitleText = signalData.influencer_videos.subtitle_text;

    const reviewPrompt = `
원본 자막과 시그널을 비교해서 신고 사유가 타당한지 검토해 주세요.

**원본 자막:**
${subtitleText}

**추출된 시그널:**
- 종목: ${signalData.stock} (${signalData.ticker || 'N/A'})
- 신호: ${signalData.signal}
- 인용문: ${signalData.quote}
- 타임스탬프: ${signalData.timestamp}
- 분석근거: ${signalData.reasoning || 'N/A'}

**신고 정보:**
- 신고 사유: ${reportData.reason}
- 상세 내용: ${reportData.detail || '없음'}

**검토 기준:**
1. 인용문이 실제 자막과 일치하는가?
2. 시그널 타입이 발언 내용과 일치하는가?
3. 타임스탬프가 정확한가?
4. 분석근거가 합리적인가?

**결과 형식:**
상태: [수정필요/문제없음]
근거: [구체적인 근거 설명]
`;

    const anthropicResponse = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-opus-4-6',
        max_tokens: 1000,
        messages: [
          {
            role: 'user',
            content: reviewPrompt
          }
        ]
      })
    });

    if (!anthropicResponse.ok) {
      throw new Error(`Anthropic API 오류: ${anthropicResponse.status}`);
    }

    const anthropicData = await anthropicResponse.json();
    const aiReview = anthropicData.content[0].text;

    // 3. AI 검토 결과 저장
    const { error: updateError } = await supabase
      .from('signal_reports')
      .update({ 
        ai_review: aiReview,
        updated_at: new Date().toISOString()
      })
      .eq('id', reportId);

    if (updateError) {
      throw new Error('AI 검토 결과 저장 실패');
    }

    // 4. "수정필요"인 경우 수정안 생성
    let aiSuggestion = null;
    if (aiReview.includes('수정필요') || aiReview.includes('수정 필요')) {
      const suggestionPrompt = `
이전 검토 결과에 따라 수정된 시그널을 JSON 형태로 생성해 주세요.

**원본 자막:**
${subtitleText}

**기존 시그널:**
- 종목: ${signalData.stock}
- 티커: ${signalData.ticker}
- 신호: ${signalData.signal}
- 인용문: ${signalData.quote}
- 타임스탬프: ${signalData.timestamp}
- 분석근거: ${signalData.reasoning}

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

JSON만 출력하고 다른 설명은 하지 마세요.
`;

      const suggestionResponse = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: 'claude-opus-4-6',
          max_tokens: 500,
          messages: [
            {
              role: 'user',
              content: suggestionPrompt
            }
          ]
        })
      });

      if (suggestionResponse.ok) {
        const suggestionData = await suggestionResponse.json();
        aiSuggestion = suggestionData.content[0].text;

        // 수정안 저장
        await supabase
          .from('signal_reports')
          .update({ 
            ai_suggestion: aiSuggestion,
            updated_at: new Date().toISOString()
          })
          .eq('id', reportId);
      }
    }

    return NextResponse.json({
      success: true,
      ai_review: aiReview,
      ai_suggestion: aiSuggestion
    });

  } catch (error) {
    console.error('AI 검토 API 오류:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.' }, 
      { status: 500 }
    );
  }
}