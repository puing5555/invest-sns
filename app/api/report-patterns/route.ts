import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function GET() {
  try {
    // 신고 데이터와 관련 시그널 정보 조회
    const { data: reports, error } = await supabase
      .from('signal_reports')
      .select(`
        id,
        reason,
        detail,
        created_at,
        status,
        influencer_signals (
          stock,
          signal,
          speakers (
            name
          ),
          influencer_videos (
            influencer_channels (
              channel_name
            )
          )
        )
      `)
      .order('created_at', { ascending: false });

    if (error) {
      throw new Error('신고 데이터 조회 실패: ' + error.message);
    }

    // 1. 사유별 신고 건수 집계
    const reasonStats: Record<string, number> = {};
    reports?.forEach((report) => {
      reasonStats[report.reason] = (reasonStats[report.reason] || 0) + 1;
    });

    // 2. 시그널 타입별 신고 빈도
    const signalTypeStats: Record<string, number> = {};
    reports?.forEach((report) => {
      if (report.influencer_signals?.signal) {
        const signal = report.influencer_signals.signal;
        signalTypeStats[signal] = (signalTypeStats[signal] || 0) + 1;
      }
    });

    // 3. 종목별 신고 빈도
    const stockStats: Record<string, number> = {};
    reports?.forEach((report) => {
      if (report.influencer_signals?.stock) {
        const stock = report.influencer_signals.stock;
        stockStats[stock] = (stockStats[stock] || 0) + 1;
      }
    });

    // 4. 화자별 신고 빈도
    const speakerStats: Record<string, number> = {};
    reports?.forEach((report) => {
      const speakerName = report.influencer_signals?.speakers?.name || 
                         report.influencer_signals?.influencer_videos?.influencer_channels?.channel_name;
      if (speakerName) {
        speakerStats[speakerName] = (speakerStats[speakerName] || 0) + 1;
      }
    });

    // 5. 월별 신고 트렌드 (최근 6개월)
    const monthlyStats: Record<string, number> = {};
    const now = new Date();
    reports?.forEach((report) => {
      const reportDate = new Date(report.created_at);
      const monthKey = `${reportDate.getFullYear()}-${String(reportDate.getMonth() + 1).padStart(2, '0')}`;
      monthlyStats[monthKey] = (monthlyStats[monthKey] || 0) + 1;
    });

    // 상위 항목만 추출
    const topReasons = Object.entries(reasonStats)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10);

    const topSignalTypes = Object.entries(signalTypeStats)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10);

    const topStocks = Object.entries(stockStats)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10);

    const topSpeakers = Object.entries(speakerStats)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10);

    return NextResponse.json({
      success: true,
      patterns: {
        totalReports: reports?.length || 0,
        reasonStats: topReasons.map(([reason, count]) => ({ reason, count })),
        signalTypeStats: topSignalTypes.map(([signal, count]) => ({ signal, count })),
        stockStats: topStocks.map(([stock, count]) => ({ stock, count })),
        speakerStats: topSpeakers.map(([speaker, count]) => ({ speaker, count })),
        monthlyStats: Object.entries(monthlyStats)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([month, count]) => ({ month, count }))
      }
    });

  } catch (error) {
    console.error('신고 패턴 분석 오류:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.' }, 
      { status: 500 }
    );
  }
}