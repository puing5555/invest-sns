'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { getInfluencerProfileBySpeaker } from '@/lib/supabase';
import SignalCard from '@/components/SignalCard';
import SignalDetailModal from '@/components/SignalDetailModal';

const V9_SIGNAL_COLORS: Record<string, string> = {
  '매수': 'text-green-600 bg-green-50',
  '긍정': 'text-blue-600 bg-blue-50',
  '중립': 'text-yellow-600 bg-yellow-50',
  '경계': 'text-orange-600 bg-orange-50',
  '매도': 'text-red-600 bg-red-50',
};

export default function InfluencerProfileClient({ id }: { id: string }) {
  const router = useRouter();
  const speakerName = decodeURIComponent(id);
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSignal, setSelectedSignal] = useState<any>(null);

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

  // 시그널 통계
  const signalCounts: Record<string, number> = {};
  profile.signals.forEach((s: any) => {
    signalCounts[s.signal] = (signalCounts[s.signal] || 0) + 1;
  });

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

        <div className="flex items-start gap-5">
          <div className="w-16 h-16 rounded-full bg-[#e8f4fd] flex items-center justify-center text-2xl font-bold text-[#3182f6] flex-shrink-0">
            {speakerName.charAt(0)}
          </div>
          <div className="flex-1">
            <h1 className="text-xl font-bold text-[#191f28] mb-1">{speakerName}</h1>
            {profile.channels.length > 0 && (
              <p className="text-sm text-[#8b95a1] mb-3">
                {profile.channels.join(' · ')}
              </p>
            )}
            <div className="flex gap-5 flex-wrap">
              <div>
                <span className="text-lg font-bold text-[#191f28]">{profile.totalSignals}건</span>
                <span className="text-xs text-[#8b95a1] ml-1">총 시그널</span>
              </div>
              <div>
                <span className="text-lg font-bold text-[#191f28]">{profile.stocks.length}개</span>
                <span className="text-xs text-[#8b95a1] ml-1">커버 종목</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 시그널 분포 */}
      <div className="px-4 py-4">
        <div className="bg-white rounded-xl border border-gray-100 p-4 mb-4">
          <div className="text-xs font-medium text-[#8b95a1] mb-3">📊 시그널 분포</div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(signalCounts).map(([sig, count]) => (
              <span key={sig} className={`px-3 py-1.5 rounded-full text-xs font-medium ${V9_SIGNAL_COLORS[sig] || 'text-gray-600 bg-gray-50'}`}>
                {sig} {count}건
              </span>
            ))}
          </div>
        </div>

        {/* 시그널 목록 */}
        <div className="text-xs font-medium text-[#8b95a1] mb-3">📋 전체 시그널 ({profile.totalSignals}건)</div>
        <div className="space-y-3">
          {profile.signals.map((signal: any, i: number) => {
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
