'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { getInfluencerProfileBySpeaker } from '@/lib/supabase';
import { slugToSpeaker } from '@/lib/speakerSlugs';
import SignalDetailModal from '@/components/SignalDetailModal';
import { formatStockDisplay, formatStockShort } from '@/lib/stockNames';

export default function InfluencerProfileClient({ id }: { id: string }) {
  const router = useRouter();
  const speakerName = slugToSpeaker(id) || decodeURIComponent(id);
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSignal, setSelectedSignal] = useState<any>(null);
  const [activeStock, setActiveStock] = useState<string>('전체');

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      const data = await getInfluencerProfileBySpeaker(speakerName);
      setProfile(data);
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

  const handleCardClick = (signal: any) => {
    const channelName = signal.influencer_videos?.influencer_channels?.channel_name || '';
    setSelectedSignal({
      date: signal.influencer_videos?.published_at || signal.created_at,
      influencer: speakerName,
      signal: signal.signal,
      quote: signal.key_quote || '',
      videoUrl: signal.influencer_videos?.video_id ? `https://youtube.com/watch?v=${signal.influencer_videos.video_id}` : '#',
      analysis_reasoning: signal.reasoning,
      videoTitle: signal.influencer_videos?.title,
      channelName,
      timestamp: signal.timestamp,
      ticker: signal.ticker,
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

        {stockCounts.length > 0 && (
          <div className="mt-4">
            <p className="text-xs text-[#8b95a1] mb-1.5">관심 종목</p>
            <p className="text-sm text-[#333d4b]">
              {stockCounts.slice(0, 5).map((s, i) => (
                <span key={s.shortName}>
                  {i > 0 && <span className="text-[#d1d6db] mx-1">·</span>}
                  <span className="font-medium">{s.shortName}</span>
                  <span className="text-[#8b95a1]">({s.count})</span>
                </span>
              ))}
            </p>
          </div>
        )}
      </div>

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
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">날짜</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">종목</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">신호</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">핵심발언</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-[#8b95a1]">영상링크</th>
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
                      case '경계': return '🟠';
                      case '매도': return '🔴';
                      default: return '⚪';
                    }
                  })();

                  return (
                    <tr
                      key={signal.id || i}
                      className="hover:bg-[#f8f9fa] cursor-pointer transition-colors"
                      onClick={() => handleCardClick(signal)}
                    >
                      <td className="px-4 py-4 text-sm text-[#191f28] whitespace-nowrap">{date}</td>
                      <td className="px-4 py-4 text-sm font-medium text-[#191f28] whitespace-nowrap">{formatStockDisplay(signal.stock, signal.ticker)}</td>
                      <td className="px-4 py-4">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{signalEmoji}</span>
                          <span className="text-xs font-medium">{signal.signal}</span>
                        </div>
                      </td>
                      <td className="px-4 py-4 text-sm text-[#191f28] max-w-xs">
                        <div className="truncate" title={signal.key_quote}>{signal.key_quote || '-'}</div>
                      </td>
                      <td className="px-4 py-4">
                        {videoId ? (
                          <a
                            href={`https://youtube.com/watch?v=${videoId}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[#3182f6] hover:text-[#2171e5] text-sm font-medium"
                            onClick={(e) => e.stopPropagation()}
                          >
                            영상보기 →
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
