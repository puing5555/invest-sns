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
        { error: 'ANTHROPIC_API_KEY媛 ?ㅼ젙?섏? ?딆븯?듬땲??' }, 
        { status: 500 }
      );
    }

    const { patterns } = await request.json();

    if (!patterns) {
      return NextResponse.json(
        { error: '?좉퀬 ?⑦꽩 ?곗씠?곌? ?꾩슂?⑸땲??' }, 
        { status: 400 }
      );
    }

    // AI?먭쾶 ?꾨＼?꾪듃 媛쒖꽑???붿껌
    const promptImprovementPrompt = `
?좉퀬 ?⑦꽩 遺꾩꽍 寃곌낵瑜?諛뷀깢?쇰줈 ?뚯씠?꾨씪???꾨＼?꾪듃??媛쒖꽑 洹쒖튃???쒖븞??二쇱꽭??

**?꾩옱 ?꾨＼?꾪듃 踰꾩쟾:** V10

**?좉퀬 ?⑦꽩 遺꾩꽍:**
1. **?ъ쑀蹂??좉퀬 嫄댁닔 TOP:**
${patterns.reasonStats.map((item: any) => `   - ${item.reason}: ${item.count}嫄?).join('\n')}

2. **?쒓렇????낅퀎 ?좉퀬 鍮덈룄:**
${patterns.signalTypeStats.map((item: any) => `   - ${item.signal}: ${item.count}嫄?).join('\n')}

3. **醫낅ぉ蹂??좉퀬 鍮덈룄 TOP:**
${patterns.stockStats.map((item: any) => `   - ${item.stock}: ${item.count}嫄?).join('\n')}

4. **?붿옄蹂??좉퀬 鍮덈룄 TOP:**
${patterns.speakerStats.map((item: any) => `   - ${item.speaker}: ${item.count}嫄?).join('\n')}

5. **珥??좉퀬 嫄댁닔:** ${patterns.totalReports}嫄?

**遺꾩꽍 湲곗?:**
- ?먯＜ ?좉퀬?섎뒗 ?ъ쑀瑜?以꾩씠湲??꾪븳 異붿텧 洹쒖튃 媛뺥솕
- ?뱀젙 ?쒓렇????낆쓽 ?ㅽ깘吏 諛⑹?
- 醫낅ぉ紐??곗빱 ?뺥솗???μ긽
- ?몄슜臾?諛?遺꾩꽍洹쇨굅???덉쭏 ?μ긽

**媛쒖꽑???뺤떇:**
?ㅼ쓬怨?媛숈씠 援ъ껜?곸씤 洹쒖튃 5-7媛쒕? ?쒖븞??二쇱꽭??

1. [臾몄젣?? ??[媛쒖꽑 洹쒖튃]
2. [臾몄젣?? ??[媛쒖꽑 洹쒖튃]
...

媛?洹쒖튃? 援ъ껜?곸씠怨??ㅽ뻾 媛?ν븳 吏移⑥씠?댁빞 ?⑸땲??
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
      throw new Error(`Anthropic API ?ㅻ쪟: ${anthropicResponse.status}`);
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
    console.error('?꾨＼?꾪듃 媛쒖꽑???앹꽦 ?ㅻ쪟:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : '?????녿뒗 ?ㅻ쪟媛 諛쒖깮?덉뒿?덈떎.' }, 
      { status: 500 }
    );
  }
}
