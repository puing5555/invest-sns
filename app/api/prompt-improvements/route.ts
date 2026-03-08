export const dynamic = 'force-static'
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
        { error: '패턴 분석 데이터가 필요합니다.' }, 
        { status: 400 }
      );
    }

    // AI로 프롬프트 개선안 생성
    const promptImprovementPrompt = `
패턴 분석 결과를 바탕으로 시그널 추출 프롬프트의 개선 버전을 제안해주세요.

**현재 프롬프트 버전:** V10

**패턴 분석 결과:**
1. **이유별 피드백 횟수 TOP:**
${patterns.reasonStats.map((item: any) => `   - ${item.reason}: ${item.count}개`).join('\n')}

2. **시그널 유형별 피드백 빈도:**
${patterns.signalTypeStats.map((item: any) => `   - ${item.signal}: ${item.count}개`).join('\n')}

3. **종목별 피드백 빈도 TOP:**
${patterns.stockStats.map((item: any) => `   - ${item.stock}: ${item.count}개`).join('\n')}

4. **발화자별 피드백 빈도 TOP:**
${patterns.speakerStats.map((item: any) => `   - ${item.speaker}: ${item.count}개`).join('\n')}

5. **총 피드백 횟수:** ${patterns.totalReports}개

**개선 방향:**
- 자주 피드백되는 이유를 해소하기 위한 명시적 지침 추가
- 특정 시그널 유형의 정확도 향상
- 종목명 인식 정확도 개선
- 활용성과 정확성 균형 개선

**개선안 제안:**
다음과 같이 개선된 지침 5-7개를 제안해주세요:

1. [개선 영역]: [개선 지침]
2. [개선 영역]: [개선 지침]
...

각 지침은 구체적이고 실행 가능한 지시사항이어야 합니다.
`;

    const anthropicResponse = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-6',
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
