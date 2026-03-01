import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function GET() {
  try {
    // 품질 이슈가 있는 시그널 조회
    const { data: signals, error } = await supabase
      .from('influencer_signals')
      .select(`
        id,
        stock,
        ticker,
        signal,
        key_quote,
        analysis_reasoning,
        confidence,
        created_at,
        influencer_videos (
          title,
          published_at,
          video_id,
          influencer_channels (
            channel_name,
            channel_handle
          )
        ),
        speakers (
          name
        )
      `)
      .order('created_at', { ascending: false })
      .limit(100); // 최근 100개만 검사

    if (error) {
      throw new Error('시그널 데이터 조회 실패: ' + error.message);
    }

    // 품질 이슈 탐지
    const issues: any[] = [];

    signals?.forEach((signal) => {
      const issueTypes: string[] = [];
      const currentValues: Record<string, string> = {};

      // 1. reasoning이 null이거나 20자 미만
      if (!signal.analysis_reasoning || signal.analysis_reasoning.length < 20) {
        issueTypes.push('분석근거 부족');
        currentValues['분석근거 부족'] = signal.analysis_reasoning || 'null';
      }

      // 2. key_quote가 15자 미만
      if (!signal.key_quote || signal.key_quote.length < 15) {
        issueTypes.push('인용문 부족');
        currentValues['인용문 부족'] = signal.key_quote || 'null';
      }

      // 3. confidence가 없는 경우
      if (!signal.confidence) {
        issueTypes.push('신뢰도 누락');
        currentValues['신뢰도 누락'] = 'null';
      }

      // 이슈가 있는 경우에만 추가
      if (issueTypes.length > 0) {
        issues.push({
          id: signal.id,
          stock: signal.stock,
          ticker: signal.ticker,
          signal: signal.signal,
          quote: signal.key_quote,
          analysis_reasoning: signal.analysis_reasoning,
          confidence: signal.confidence,
          created_at: signal.created_at,
          influencer_videos: signal.influencer_videos,
          speakers: signal.speakers,
          issueTypes,
          currentValues
        });
      }
    });

    return NextResponse.json({
      success: true,
      issues,
      totalChecked: signals?.length || 0,
      totalIssues: issues.length
    });

  } catch (error) {
    console.error('품질 이슈 조회 오류:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.' }, 
      { status: 500 }
    );
  }
}