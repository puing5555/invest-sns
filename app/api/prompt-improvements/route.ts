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

    const { patterns } = await request.json();

    if (!patterns) {
      return NextResponse.json(
        { error: '신고 패턴 데이터가 필요합니다.' }, 
        { status: 400 }
      );
    }

    // AI에게 프롬프트 개선안 요청
    const promptImprovementPrompt = `
신고 패턴 분석 결과를 바탕으로 파이프라인 프롬프트의 개선 규칙을 제안해 주세요.

**현재 프롬프트 버전:** V10

**신고 패턴 분석:**
1. **사유별 신고 건수 TOP:**
${patterns.reasonStats.map((item: any) => `   - ${item.reason}: ${item.count}건`).join('\n')}

2. **시그널 타입별 신고 빈도:**
${patterns.signalTypeStats.map((item: any) => `   - ${item.signal}: ${item.count}건`).join('\n')}

3. **종목별 신고 빈도 TOP:**
${patterns.stockStats.map((item: any) => `   - ${item.stock}: ${item.count}건`).join('\n')}

4. **화자별 신고 빈도 TOP:**
${patterns.speakerStats.map((item: any) => `   - ${item.speaker}: ${item.count}건`).join('\n')}

5. **총 신고 건수:** ${patterns.totalReports}건

**분석 기준:**
- 자주 신고되는 사유를 줄이기 위한 추출 규칙 강화
- 특정 시그널 타입의 오탐지 방지
- 종목명/티커 정확도 향상
- 인용문 및 분석근거의 품질 향상

**개선안 형식:**
다음과 같이 구체적인 규칙 5-7개를 제안해 주세요:

1. [문제점] → [개선 규칙]
2. [문제점] → [개선 규칙]
...

각 규칙은 구체적이고 실행 가능한 지침이어야 합니다.
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
        max_tokens: 1500,
        messages: [
          {
            role: 'user',
            content: promptImprovementPrompt
          }
        ]
      })
    });

    if (!anthropicResponse.ok) {
      throw new Error(`Anthropic API 오류: ${anthropicResponse.status}`);
    }

    const anthropicData = await anthropicResponse.json();
    const promptImprovements = anthropicData.content[0].text;

    return NextResponse.json({
      success: true,
      improvements: promptImprovements,
      currentVersion: 'V10',
      analysisDate: new Date().toISOString(),
      patternsAnalyzed: patterns
    });

  } catch (error) {
    console.error('프롬프트 개선안 생성 오류:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.' }, 
      { status: 500 }
    );
  }
}