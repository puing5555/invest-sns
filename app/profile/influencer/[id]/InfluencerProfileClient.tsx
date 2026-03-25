'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { getInfluencerProfileBySpeaker, getSignalVoteCounts } from '@/lib/supabase';
import { slugToSpeaker } from '@/lib/speakerSlugs';
import SignalDetailModal from '@/components/SignalDetailModal';
import { formatStockDisplay, formatStockShort } from '@/lib/stockNames';
import { formatStockPrice } from '@/lib/currency';
import scorecardData from '@/data/influencer_scorecard.json';
import reportsData from '@/data/influencer_reports.json';

export default function InfluencerProfileClient({ id }: { id: string }) {
  const router = useRouter();
  const speakerName = slugToSpeaker(id) || decodeURIComponent(id);
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSignal, setSelectedSignal] = useState<any>(null);
  const [activeStock, setActiveStock] = useState<string>('전체');
  const [likeCounts, setLikeCounts] = useState<Record<string, number>>({});
  const [reportOpen, setReportOpen] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      const data = await getInfluencerProfileBySpeaker(speakerName);
      setProfile(data);

      // 좋아요 카운트 가져오기
      if (data?.signals?.length > 0) {
        const signalIds = data.signals.map((s: any) => s.id).filter(Boolean);
        if (signalIds.length > 0) {
          try {
            const counts = await getSignalVoteCounts(signalIds);
            setLikeCounts(counts);
          } catch (e) {
            console.error('Failed to load like counts:', e);
          }
        }
      }

      setLoading(false);
    };
    load();
  }, [speakerName]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#f4f4f4] flex items-center justify-center">
        <div className="text-4xl mb-4">⏳</div>
      </div>
    );
  }

  if (!profile || profile.totalSignals === 0) {
    return (
      <div className="min-h-screen bg-[#f4f4f4] flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">🔍</div>
          <h2 className="text-xl font-bold text-[#191f28] mb-2">'{speakerName}' 시그널을 찾을 수 없습니다</h2>
          <Link href="/explore/influencer" className="text-[#3182f6]">← 인플루언서 목록으로</Link>
        </div>
      </div>
    );
  }

  // 종목별 카운트 계산 (발언 많은 순, 같은 종목 합산)
  const stockCounts: { name: string; count: number; shortName: string }[] = [];
  if (profile?.signals) {
    const countMap: Record<string, number> = {};
    const displayMap: Record<string, string> = {};
    for (const s of profile.signals) {
      // shortName 기준으로 그룹핑 (중복 제거)
      const shortName = formatStockShort(s.stock, s.ticker) || '기타';
      const displayName = formatStockDisplay(s.stock, s.ticker) || '기타';
      countMap[shortName] = (countMap[shortName] || 0) + 1;
      if (!displayMap[shortName]) displayMap[shortName] = displayName;
    }
    Object.entries(countMap)
      .sort((a, b) => b[1] - a[1])
      .forEach(([shortName, count]) => stockCounts.push({ name: displayMap[shortName], count, shortName }));
  }

  // 필터링된 시그널 (published_at 우선 최신순 정렬)
  const sortByDate = (a: any, b: any) => {
    const dateA = a.influencer_videos?.published_at || a.created_at || '';
    const dateB = b.influencer_videos?.published_at || b.created_at || '';
    return dateB.localeCompare(dateA);
  };
  const filteredSignals = (activeStock === '전체'
    ? (profile?.signals || [])
    : (profile?.signals || []).filter((s: any) => (formatStockShort(s.stock, s.ticker) || '기타') === activeStock)
  ).sort(sortByDate);

  // scored_list에서 signal id → 1Y/현재 수익률 lookup
  const scoredMap: Record<string, { return_1y: number | null; return_current: number | null; hit: boolean | null }> = {};
  const sc = (scorecardData as any).speakers || {};
  const cardData = sc[id] || null;
  if (cardData?.scored_list) {
    for (const s of cardData.scored_list) {
      if (s.id) scoredMap[s.id] = { return_1y: s.return_1y, return_current: s.return_current, hit: s.hit };
    }
  }

  const handleCardClick = (signal: any) => {
    const channelName = signal.influencer_videos?.influencer_channels?.channel_name || '';
    setSelectedSignal({
      id: signal.id,
      date: signal.influencer_videos?.published_at || signal.created_at,
      influencer: speakerName,
      signal: signal.signal,
      quote: signal.key_quote || '',
      videoUrl: (() => {
        const vid = signal.influencer_videos?.video_id;
        if (!vid) return '#';
        let url = `https://www.youtube.com/watch?v=${vid}`;
        const ts = signal.timestamp;
        if (ts && ts !== 'N/A' && ts !== 'null') {
          const parts = ts.split(':').map(Number);
          const secs = parts.length === 3 ? parts[0]*3600+parts[1]*60+parts[2] : parts.length === 2 ? parts[0]*60+parts[1] : parts[0];
          if (secs > 0) url += `&t=${secs}`;
        }
        return url;
      })(),
      analysis_reasoning: signal.reasoning,
      videoTitle: signal.influencer_videos?.title,
      channelName,
      timestamp: signal.timestamp,
      ticker: signal.ticker,
      likeCount: likeCounts[signal.id] || 0,
    });
  };

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* Header */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-6">
        <div className="mb-4">
          <button onClick={() => router.push('/explore/influencer')} className="flex items-center gap-2 text-[#8b95a1] hover:text-[#191f28] transition-colors">
            <span className="text-lg">←</span>
            <span className="text-sm">인플루언서 목록</span>
          </button>
        </div>

        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-full bg-[#e8f4fd] flex items-center justify-center text-2xl font-bold text-[#3182f6] flex-shrink-0">
            {speakerName.charAt(0)}
          </div>
          <div>
            <h1 className="text-xl font-bold text-[#191f28]">{speakerName}</h1>
            <p className="text-sm text-[#8b95a1] mt-1">총 {profile.totalSignals}건의 시그널</p>
          </div>
        </div>

      </div>

      {/* 성과 요약 */}
      {(() => {
        const sc = (scorecardData as any).speakers || {};
        const card = sc[id] || null;
        if (!card || card.scored_signals === 0) return null;

        const hitColor = card.hit_rate != null
          ? (card.hit_rate >= 60 ? 'text-green-600' : card.hit_rate >= 50 ? 'text-yellow-600' : 'text-red-500')
          : 'text-gray-400';
        const medColor = card.median_return_1y != null
          ? (card.median_return_1y >= 0 ? 'text-green-600' : 'text-red-500')
          : 'text-gray-400';

        return (
          <div className="px-4 pt-4">
            <div className="bg-white rounded-lg border border-[#e8e8e8] p-4">
              <h3 className="text-xs font-medium text-[#8b95a1] mb-3">성과 요약 <span className="text-[10px] text-[#b0b8c1]">매수/긍정/매도 기준, 월별 dedup</span></h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {/* 1열: 적중률 */}
                <div className="text-center">
                  <div className={`text-2xl font-bold ${hitColor}`}>{card.hit_rate != null ? `${card.hit_rate}%` : '수집 중'}</div>
                  <div className="text-xs text-[#8b95a1] mt-1">적중률</div>
                  <div className="text-[10px] text-[#8b95a1]">{card.hit_eligible || 0}건 기준</div>
                </div>
                {/* 2열: 승/패 */}
                <div className="text-center">
                  <div className="text-2xl font-bold text-[#191f28]">
                    <span className="text-green-600">{card.wins}</span>
                    <span className="text-[#8b95a1] text-lg mx-1">/</span>
                    <span className="text-red-500">{card.losses}</span>
                  </div>
                  <div className="text-xs text-[#8b95a1] mt-1">승 / 패</div>
                  {card.pending > 0 && <div className="text-[10px] text-[#8b95a1]">평가 중 {card.pending}건</div>}
                </div>
                {/* 3열: 중앙수익률 (1Y | 현재) */}
                <div className="text-center">
                  <div className="text-sm font-bold">
                    <span className={medColor}>
                      {card.median_return_1y != null ? `${card.median_return_1y >= 0 ? '+' : ''}${card.median_return_1y?.toFixed(0)}%` : '-'}
                    </span>
                    <span className="text-[#d1d6db] mx-1">|</span>
                    <span className={card.median_return_current != null ? (card.median_return_current >= 0 ? 'text-green-600' : 'text-red-500') : 'text-gray-400'}>
                      {card.median_return_current != null ? `${card.median_return_current >= 0 ? '+' : ''}${card.median_return_current?.toFixed(0)}%` : '-'}
                    </span>
                  </div>
                  <div className="text-xs text-[#8b95a1] mt-1">중앙수익률</div>
                  <div className="text-[10px] text-[#8b95a1]">1Y | 현재</div>
                </div>
                {/* 4열: 최고 콜 */}
                {card.best_call && (
                  <div className="text-center">
                    <div className="text-lg font-bold text-green-600">
                      {card.best_call.return_1y != null ? `+${card.best_call.return_1y?.toFixed(0)}%` : `+${card.best_call.return_current?.toFixed(0)}%`}
                    </div>
                    <div className="text-xs text-[#191f28] font-medium truncate">{card.best_call.stock}</div>
                    <div className="text-[10px] text-[#8b95a1]">최고 콜 {card.best_call.return_1y != null ? '(1Y)' : '(현재)'}</div>
                  </div>
                )}
              </div>

              {/* 승/패 바 + 시장별 */}
              <div className="mt-3 flex items-center gap-4 flex-wrap">
                {card.wins + card.losses > 0 && (
                  <div className="flex items-center gap-2 flex-1 min-w-[120px]">
                    <div className="flex h-2 rounded-full overflow-hidden bg-gray-100 flex-1">
                      <div className="bg-green-500" style={{ width: `${(card.wins / (card.wins + card.losses)) * 100}%` }} />
                      <div className="bg-red-400" style={{ width: `${(card.losses / (card.wins + card.losses)) * 100}%` }} />
                    </div>
                    <span className="text-[10px] text-[#8b95a1] whitespace-nowrap">{card.wins}W/{card.losses}L</span>
                  </div>
                )}
                {card.market && Object.keys(card.market).length > 0 && (
                  <div className="flex gap-3">
                    {Object.entries(card.market).map(([mkt, data]: [string, any]) => (
                      <span key={mkt} className="text-[10px] text-[#8b95a1]">
                        <span className="font-medium text-[#333d4b]">{mkt}</span> {data.count}건
                        {data.hit_rate != null && <span className={data.hit_rate >= 50 ? 'text-green-600' : 'text-red-500'}> {data.hit_rate}%</span>}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })()}

      {/* AI 분석 리포트 */}
      {(() => {
        const sc = (scorecardData as any).speakers || {};
        const card = sc[id] || null;
        const report = (reportsData as any).reports?.[id];
        if (!card || !report || card.hit_eligible < 3) return null;

        const sim = report.sections?.follow_simulation;
        const styleColors: Record<string, string> = {
          '⭐올라운더': 'bg-blue-50 text-blue-700',
          '🎯스나이퍼': 'bg-green-50 text-green-700',
          '💣홈런히터': 'bg-orange-50 text-orange-700',
          '📊시그널 수집 중': 'bg-gray-50 text-gray-500',
          '📊일반': 'bg-gray-50 text-gray-600',
        };
        const styleCls = styleColors[card.style_tag] || 'bg-gray-50 text-gray-600';

        return (
          <div className="px-4 pt-4">
            <div className="bg-white rounded-lg border border-[#e8e8e8] p-4">
              {/* 헤더: 제목 + 스타일 태그 */}
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-medium text-[#8b95a1]">AI 분석 리포트</h3>
                <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${styleCls}`}>
                  {card.style_tag}
                </span>
              </div>

              {/* 한줄 평가 */}
              <p className="text-sm text-[#191f28] mb-4">{report.sections?.one_liner}</p>

              {/* TOP3 / WORST3 */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div>
                  <p className="text-xs font-medium text-green-600 mb-1.5">TOP 3 콜</p>
                  {(card.top3_calls || []).map((c: any, i: number) => (
                    <div key={i} className="text-xs text-[#333d4b] mb-1">
                      <div className="font-medium truncate">{c.stock}</div>
                      <div className="text-[10px]">
                        <span className="text-green-600 font-medium">{c.return_1y != null ? `1Y +${c.return_1y?.toFixed(0)}%` : '1Y 평가중'}</span>
                        <span className="text-[#d1d6db] mx-1">|</span>
                        <span className="text-[#8b95a1]">{c.return_current != null ? `현재 ${c.return_current >= 0 ? '+' : ''}${c.return_current?.toFixed(0)}%` : ''}</span>
                      </div>
                    </div>
                  ))}
                </div>
                <div>
                  <p className="text-xs font-medium text-red-500 mb-1.5">WORST 3 콜</p>
                  {(card.worst3_calls || []).map((c: any, i: number) => (
                    <div key={i} className="text-xs text-[#333d4b] mb-1">
                      <div className="font-medium truncate">{c.stock}</div>
                      <div className="text-[10px]">
                        <span className="text-red-500 font-medium">{c.return_1y != null ? `1Y ${c.return_1y >= 0 ? '+' : ''}${c.return_1y?.toFixed(0)}%` : '1Y 평가중'}</span>
                        <span className="text-[#d1d6db] mx-1">|</span>
                        <span className="text-[#8b95a1]">{c.return_current != null ? `현재 ${c.return_current >= 0 ? '+' : ''}${c.return_current?.toFixed(0)}%` : ''}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 홈런 비율 바 */}
              <div className="mb-4">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-[#8b95a1]">홈런 비율 (+100% 이상)</span>
                  <span className="font-medium text-[#191f28]">{card.homerun_rate}%</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-[#3182f6] rounded-full transition-all" style={{ width: `${Math.min(card.homerun_rate || 0, 100)}%` }} />
                </div>
              </div>

              {/* 기대수익률 + 팔로우 시뮬레이션 */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-[#f8f9fa] rounded-lg p-3 text-center">
                  <div className={`text-lg font-bold ${(card.expected_return || 0) >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                    {card.expected_return != null ? `${card.expected_return >= 0 ? '+' : ''}${card.expected_return?.toFixed(1)}%` : '-'}
                  </div>
                  <div className="text-[10px] text-[#8b95a1] mt-0.5">기대수익률</div>
                </div>
                {sim && (sim.total_invested_1y > 0 || sim.total_invested_cur > 0) && (
                  <div className="bg-[#f8f9fa] rounded-lg p-3 text-center">
                    <div className="text-sm font-bold">
                      <span className={`${(sim.return_1y || 0) >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                        {sim.return_1y != null ? `${sim.return_1y >= 0 ? '+' : ''}${sim.return_1y}%` : '-'}
                      </span>
                      <span className="text-[#d1d6db] mx-1">|</span>
                      <span className={`${(sim.return_cur || 0) >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                        {sim.return_cur != null ? `${sim.return_cur >= 0 ? '+' : ''}${sim.return_cur}%` : '-'}
                      </span>
                    </div>
                    <div className="text-[10px] text-[#8b95a1] mt-0.5">팔로우 수익률</div>
                    <div className="text-[10px] text-[#8b95a1]">1Y | 현재</div>
                  </div>
                )}
              </div>

              {/* 접이식 상세 리포트 */}
              <button
                onClick={() => setReportOpen(!reportOpen)}
                className="text-xs text-[#3182f6] font-medium hover:underline"
              >
                {reportOpen ? '접기 ▲' : '상세 리포트 보기 ▼'}
              </button>
              {reportOpen && (
                <div className="mt-3 text-xs text-[#333d4b] space-y-3 bg-[#f8f9fa] rounded-lg p-4">
                  {[
                    { key: 'strengths_weaknesses', title: '강점/약점' },
                    { key: 'investment_pattern', title: '투자 패턴' },
                    { key: 'trend_analysis', title: '트렌드 분석' },
                    { key: 'ai_opinion', title: 'AI 종합 의견' },
                  ].map(({ key, title }) => {
                    const text = key === 'follow_simulation'
                      ? report.sections?.[key]?.text
                      : report.sections?.[key];
                    if (!text) return null;
                    return (
                      <div key={key}>
                        <p className="font-medium text-[#191f28] mb-1">{title}</p>
                        <p className="whitespace-pre-wrap leading-relaxed">{text}</p>
                      </div>
                    );
                  })}
                  {sim?.text && (
                    <div>
                      <p className="font-medium text-[#191f28] mb-1">팔로우 시뮬레이션</p>
                      <p className="whitespace-pre-wrap leading-relaxed">{sim.text}</p>
                    </div>
                  )}
                </div>
              )}

              {/* 분석 기준 */}
              <p className="text-[10px] text-[#b0b8c1] mt-3">분석 기준: 2026년 3월</p>
            </div>
          </div>
        );
      })()}

      {/* 종목 필터 탭 (시그널 5개 이상만) */}
      {(() => {
        const filteredTabs = stockCounts.filter(s => s.count >= 5);
        return filteredTabs.length > 0 ? (
          <div className="px-4 pt-4 pb-0">
            <div className="flex gap-2 overflow-x-auto no-scrollbar">
              <button
                onClick={() => setActiveStock('전체')}
                className={`flex-shrink-0 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                  activeStock === '전체'
                    ? 'bg-[#191f28] text-white'
                    : 'bg-white text-[#8b95a1] border border-[#e8e8e8]'
                }`}
              >
                전체 {profile.totalSignals}
              </button>
              {filteredTabs.map((s) => (
                <button
                  key={s.shortName}
                  onClick={() => setActiveStock(s.shortName)}
                  className={`flex-shrink-0 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    activeStock === s.shortName
                      ? 'bg-[#191f28] text-white'
                      : 'bg-white text-[#8b95a1] border border-[#e8e8e8]'
                  }`}
                >
                  {s.shortName} {s.count}
                </button>
              ))}
            </div>
          </div>
        ) : null;
      })()}

      {/* 시그널 테이블 */}
      <div className="px-4 py-4">
        <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[#f8f9fa]">
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-medium text-[#8b95a1] whitespace-nowrap w-[12%]">날짜</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-[#8b95a1] w-[11%]">종목</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-[#8b95a1] whitespace-nowrap min-w-[60px] w-[7%]">신호</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-[#8b95a1]">핵심발언</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-[#8b95a1] whitespace-nowrap w-[12%]">수익률</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-[#8b95a1] whitespace-nowrap w-[5%]">링크</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#f0f0f0]">
                {filteredSignals.map((signal: any, i: number) => {
                  const publishedAt = signal.influencer_videos?.published_at || signal.created_at;
                  const videoId = signal.influencer_videos?.video_id;
                  const date = publishedAt ? new Date(publishedAt).toLocaleDateString('ko-KR', { year: 'numeric', month: 'short', day: 'numeric' }) : '';
                  const signalEmoji = (() => {
                    switch (signal.signal) {
                      case '매수': return '🟢';
                      case '긍정': return '🔵';
                      case '중립': return '🟡';
                      case '부정': return '🟠';
                      case '매도': return '🔴';
                      default: return '⚪';
                    }
                  })();

                  const isRef = signal.signal === '부정' || signal.signal === '중립';
                  const rowCls = isRef ? 'opacity-50' : '';

                  return (
                    <tr
                      key={signal.id || i}
                      className={`hover:bg-[#f8f9fa] cursor-pointer transition-colors ${rowCls}`}
                      onClick={() => handleCardClick(signal)}
                    >
                      <td className="px-3 py-3 text-xs text-[#191f28] whitespace-nowrap">{date}</td>
                      <td className="px-3 py-3 text-xs font-medium text-[#191f28] w-[11%]">
                        {signal.ticker ? (
                          <Link
                            href={`/stock/${signal.ticker}?tab=influencer`}
                            className="text-[#3182f6] hover:underline break-words"
                            title={formatStockDisplay(signal.stock, signal.ticker)}
                            onClick={(e) => e.stopPropagation()}
                          >{formatStockShort(signal.stock, signal.ticker) || formatStockDisplay(signal.stock, signal.ticker)}</Link>
                        ) : (
                          <div className="break-words" title={formatStockDisplay(signal.stock, signal.ticker)}>{formatStockShort(signal.stock, signal.ticker) || formatStockDisplay(signal.stock, signal.ticker)}</div>
                        )}
                      </td>
                      <td className="px-3 py-3 whitespace-nowrap">
                        <div className="flex items-center gap-1 flex-nowrap">
                          <span className="text-base flex-shrink-0">{signalEmoji}</span>
                          <span className="text-xs font-medium">{signal.signal}</span>
                        </div>
                      </td>
                      <td className="px-3 py-3 text-xs text-[#191f28]">
                        <div className="line-clamp-2" title={signal.key_quote}>{signal.key_quote || '-'}</div>
                      </td>
                      <td className="px-3 py-3 text-xs whitespace-nowrap">
                        {(() => {
                          if (isRef) return <span className="text-[#8b95a1]">참고</span>;
                          const scored = signal.id ? scoredMap[signal.id] : null;
                          if (!scored) return <span className="text-[#8b95a1]">-</span>;
                          const r1y = scored.return_1y;
                          const rCur = scored.return_current;
                          const isBuy = signal.signal === '매수' || signal.signal === '긍정';
                          const retForColor = r1y ?? rCur;
                          const isGood = retForColor != null ? (isBuy ? retForColor > 0 : retForColor < 0) : false;
                          const color = retForColor != null ? (isGood ? 'text-[#22c55e]' : 'text-[#ef4444]') : 'text-[#8b95a1]';
                          return (
                            <div>
                              {r1y != null ? (
                                <div className={`font-medium ${color}`}>
                                  {r1y >= 0 ? '▲' : '▼'} {r1y >= 0 ? '+' : ''}{r1y}%
                                  <span className="text-[10px] text-[#8b95a1] ml-0.5">1Y</span>
                                </div>
                              ) : (
                                <div className="text-[#8b95a1]">평가 중</div>
                              )}
                              {rCur != null && (
                                <div className="text-[10px] text-[#8b95a1]">
                                  현재 {rCur >= 0 ? '+' : ''}{rCur}%
                                </div>
                              )}
                            </div>
                          );
                        })()}
                      </td>
                      <td className="px-3 py-3">
                        {videoId ? (
                          <a
                            href={(() => {
                              let url = `https://www.youtube.com/watch?v=${videoId}`;
                              const ts = signal.timestamp;
                              if (ts && ts !== 'N/A' && ts !== 'null') {
                                const parts = ts.split(':').map(Number);
                                const secs = parts.length === 3 ? parts[0]*3600+parts[1]*60+parts[2] : parts.length === 2 ? parts[0]*60+parts[1] : parts[0];
                                if (secs > 0) url += `&t=${secs}`;
                              }
                              return url;
                            })()}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[#3182f6] hover:text-[#2171e5] text-xs font-medium"
                            onClick={(e) => e.stopPropagation()}
                          >
                            보기→
                          </a>
                        ) : '-'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <SignalDetailModal signal={selectedSignal} onClose={() => setSelectedSignal(null)} />
    </div>
  );
}
