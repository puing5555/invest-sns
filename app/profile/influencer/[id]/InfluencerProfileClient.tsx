'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { getInfluencerProfileBySpeaker } from '@/lib/supabase';
import { slugToSpeaker } from '@/lib/speakerSlugs';
import SignalCard from '@/components/SignalCard';
import SignalDetailModal from '@/components/SignalDetailModal';

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

  // 종목별 카운트 계산 (발언 많은 순)
  const stockCounts: { name: string; count: number }[] = [];
  if (profile?.signals) {
    const countMap: Record<string, number> = {};
    for (const s of profile.signals) {
      const name = s.stock || '기타';
      countMap[name] = (countMap[name] || 0) + 1;
    }
    Object.entries(countMap)
      .sort((a, b) => b[1] - a[1])
      .forEach(([name, count]) => stockCounts.push({ name, count }));
  }

  // 필터링된 시그널
  const filteredSignals = activeStock === '전체'
    ? (profile?.signals || [])
    : (profile?.signals || []).filter((s: any) => (s.stock || '기타') === activeStock);

  const handleCardClick = (signal: any) => {
    if (signal.ticker) {
      router.push(`/stock/${signal.ticker}?tab=influencer`);
    } else {
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
    }
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
              {stockCounts.map((s, i) => (
                <span key={s.name}>
                  {i > 0 && <span className="text-[#d1d6db] mx-1">·</span>}
                  <span className="font-medium">{s.name}</span>
                  <span className="text-[#8b95a1]">({s.count})</span>
                </span>
              ))}
            </p>
          </div>
        )}
      </div>

      {/* 종목 필터 탭 */}
      {stockCounts.length > 1 && (
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
            {stockCounts.map((s) => (
              <button
                key={s.name}
                onClick={() => setActiveStock(s.name)}
                className={`flex-shrink-0 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                  activeStock === s.name
                    ? 'bg-[#191f28] text-white'
                    : 'bg-white text-[#8b95a1] border border-[#e8e8e8]'
                }`}
              >
                {s.name} {s.count}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 시그널 리스트 */}
      <div className="px-4 py-4">
        <div className="space-y-3">
          {filteredSignals.map((signal: any, i: number) => {
            const channelName = signal.influencer_videos?.influencer_channels?.channel_name || '';
            const publishedAt = signal.influencer_videos?.published_at || signal.created_at;
            const videoId = signal.influencer_videos?.video_id;
            const date = publishedAt ? new Date(publishedAt).toLocaleDateString('ko-KR', { year: 'numeric', month: 'short', day: 'numeric' }) : '';

            return (
              <SignalCard
                key={signal.id || i}
                signal={signal.signal || '중립'}
                stock={signal.stock || '알 수 없는 종목'}
                speaker={speakerName}
                channelName={channelName}
                keyQuote={signal.key_quote}
                videoTitle={signal.influencer_videos?.title}
                date={date}
                videoUrl={videoId ? `https://youtube.com/watch?v=${videoId}` : undefined}
                onClick={() => handleCardClick(signal)}
              />
            );
          })}
        </div>
      </div>

      <SignalDetailModal signal={selectedSignal} onClose={() => setSelectedSignal(null)} />
    </div>
  );
}
