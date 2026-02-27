'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { getInfluencerProfile, getSignalColor } from '@/lib/supabase';

// 신호별 색상 매핑
function getSignalLabel(signal: string) {
  // DB는 한글로 저장되어 있으므로 그대로 사용
  return signal;
}

function getSignalDotColor(signal: string) {
  switch (signal) {
    case 'BUY': return '#3182f6';
    case 'POSITIVE': return '#22c55e';
    case 'NEUTRAL': return '#eab308';
    case 'CONCERN': return '#f97316';
    case 'SELL': return '#ef4444';
    default: return '#9ca3af';
  }
}

export default function InfluencerProfileClient({ id }: { id: string }) {
  const router = useRouter();
  const [isFollowing, setIsFollowing] = useState(false);
  const [selectedSignal, setSelectedSignal] = useState<any | null>(null);
  const [influencer, setInfluencer] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 데이터 로드
  useEffect(() => {
    const loadInfluencerData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getInfluencerProfile(id);
        
        if (!data) {
          setError('인플루언서를 찾을 수 없습니다');
          return;
        }

        // 데이터를 UI용 형태로 변환
        const transformedData = {
          id: data.id,
          name: data.channel_name,
          avatar: data.channel_name.charAt(0),
          badge: '유튜버',
          subscribers: data.subscriber_count ? `${Math.floor(data.subscriber_count / 10000)}만` : 'N/A',
          videos: 0, // TODO: 영상 수 계산
          mentions: data.signals?.length || 0,
          avgReturn: 'N/A', // TODO: 평균 수익률 계산
          positiveRatio: 'N/A', // TODO: 긍정 비율 계산
          totalSignals: data.signals?.length || 0,
          coverStocks: new Set(data.signals?.map((s: any) => s.stock)).size || 0,
          stocks: [], // TODO: 주요 종목 계산
          signalHistory: (data.signals || []).map((signal: any) => {
            const publishedDate = signal.influencer_videos?.published_at 
              ? new Date(signal.influencer_videos.published_at)
              : new Date();
            
            const videoUrl = signal.influencer_videos?.video_id 
              ? `https://youtube.com/watch?v=${signal.influencer_videos.video_id}`
              : '#';

            return {
              date: publishedDate.toLocaleDateString('ko-KR', { month: '2-digit', day: '2-digit' }),
              stock: signal.stock,
              stockCode: signal.ticker,
              signal: signal.signal,
              content: signal.key_quote || '키 인용문이 없습니다.',
              returnPct: 'N/A', // TODO: 수익률 계산
              source: data.channel_name,
              videoUrl,
              timestamp: signal.timestamp ? `[${Math.floor(signal.timestamp / 60)}:${String(signal.timestamp % 60).padStart(2, '0')}]` : '[0:00]',
              videoTitle: signal.influencer_videos?.title || 'Unknown Video',
              summary: signal.reasoning || '분석 내용이 없습니다.'
            };
          })
        };

        setInfluencer(transformedData);
      } catch (err) {
        console.error('Error loading influencer data:', err);
        setError('데이터를 불러오는 중 오류가 발생했습니다');
      } finally {
        setLoading(false);
      }
    };

    loadInfluencerData();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#f4f4f4] flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">⏳</div>
          <h2 className="text-xl font-bold text-[#191f28] mb-2">데이터를 불러오는 중...</h2>
        </div>
      </div>
    );
  }

  if (error || !influencer) {
    return (
      <div className="min-h-screen bg-[#f4f4f4] flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">🔍</div>
          <h2 className="text-xl font-bold text-[#191f28] mb-2">{error || '인플루언서를 찾을 수 없습니다'}</h2>
          <Link href="/explore/influencer" className="text-[#3182f6]">← 인플루언서 목록으로</Link>
        </div>
      </div>
    );
  }

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
            {influencer.avatar}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-1 flex-wrap">
              <h1 className="text-xl font-bold text-[#191f28]">{influencer.name}</h1>
              <span className="px-2 py-0.5 bg-blue-100 text-[#3182f6] text-xs rounded-full border border-blue-200">{influencer.badge}</span>
              <span className="px-2 py-0.5 bg-[#f2f4f6] text-[#8b95a1] text-xs rounded-full">한국주식 · 미국주식</span>
            </div>
            <div className="text-sm text-[#8b95a1] mb-3">
              구독자 {influencer.subscribers} · 분석 영상 {influencer.videos}개 · 종목 언급 {influencer.mentions}건
            </div>
            <div className="flex gap-5 flex-wrap">
              <div><span className="text-lg font-bold text-[#3182f6]">{influencer.positiveRatio}</span><span className="text-xs text-[#8b95a1] ml-1">긍정 신호 비율</span></div>
              <div><span className="text-lg font-bold text-[#191f28]">{influencer.totalSignals}건</span><span className="text-xs text-[#8b95a1] ml-1">총 신호</span></div>
              <div><span className="text-lg font-bold text-[#191f28]">{influencer.coverStocks}개</span><span className="text-xs text-[#8b95a1] ml-1">커버 종목</span></div>
            </div>
          </div>
          <button
            onClick={() => setIsFollowing(!isFollowing)}
            className={`px-5 py-2.5 rounded-lg text-sm font-medium transition-colors flex-shrink-0 ${
              isFollowing ? 'bg-[#f2f4f6] text-[#8b95a1] border border-[#e8e8e8]' : 'bg-[#3182f6] text-white hover:bg-[#2171e5]'
            }`}
          >
            {isFollowing ? '팔로잉' : '팔로우'}
          </button>
        </div>
      </div>

      <div className="px-4 py-4 space-y-4">
        {/* 관심종목 태그 */}
        <div className="bg-white rounded-lg border border-[#e8e8e8] p-5">
          <div className="text-xs font-medium text-[#8b95a1] mb-3">📌 관심 종목 (클릭 시 해당 종목 차트 + 신호 확인)</div>
          <div className="flex flex-wrap gap-2">
            {influencer.stocks.map(stock => (
              <Link
                key={stock.code}
                href={`/stock/${stock.code}?tab=influencer`}
                className="px-3 py-2 bg-[#e8f4fd] text-[#3182f6] rounded-full text-sm border border-blue-200 hover:bg-blue-200 transition-colors"
              >
                {stock.name} ({stock.mentions})
              </Link>
            ))}
          </div>
        </div>

        {/* 종목별 신호 차트 */}
        <div className="bg-white rounded-lg border border-[#e8e8e8] p-5">
          <div className="text-xs font-medium text-[#8b95a1] mb-3">📊 종목별 신호 차트</div>
          <div className="flex gap-2 mb-4 flex-wrap">
            <span className="px-3 py-1.5 bg-[#3182f6] text-white rounded-full text-xs">전체 ({influencer.totalSignals})</span>
            {influencer.stocks.map(s => (
              <span key={s.code} className="px-3 py-1.5 bg-[#f2f4f6] text-[#8b95a1] rounded-full text-xs border border-[#e8e8e8] hover:bg-[#e9ecef] cursor-pointer">{s.name} ({s.mentions})</span>
            ))}
          </div>
          <div className="relative h-48 bg-[#f8f9fa] rounded-lg border border-[#e8e8e8] overflow-hidden">
            <svg viewBox="0 0 500 180" className="w-full h-full">
              <polyline fill="none" stroke="#d1d5db" strokeWidth="1.5" points="20,140 80,120 140,100 200,110 260,80 320,70 380,60 440,50 480,45" />
              {influencer.signalHistory.slice(0, 6).map((sig, i) => {
                const x = 60 + i * 75;
                const y = 130 - i * 15 + (i % 2 === 0 ? -10 : 10);
                return <circle key={i} cx={x} cy={y} r="6" fill={getSignalDotColor(sig.signal)} stroke="white" strokeWidth="2" />;
              })}
            </svg>
            <div className="absolute bottom-2 left-4 flex gap-3 text-[10px] text-[#8b95a1]">
              <span><span className="inline-block w-2 h-2 rounded-full bg-[#3182f6] mr-1"></span>매수</span>
              <span><span className="inline-block w-2 h-2 rounded-full bg-[#22c55e] mr-1"></span>긍정</span>
              <span><span className="inline-block w-2 h-2 rounded-full bg-[#eab308] mr-1"></span>중립</span>
              <span><span className="inline-block w-2 h-2 rounded-full bg-[#f97316] mr-1"></span>경계</span>
              <span><span className="inline-block w-2 h-2 rounded-full bg-[#ef4444] mr-1"></span>매도</span>
            </div>
          </div>
        </div>

        {/* 전체 발언 이력 */}
        <div className="bg-white rounded-lg border border-[#e8e8e8] p-5">
          <div className="text-xs font-medium text-[#8b95a1] mb-3">📋 전체 발언 이력</div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#e8e8e8]">
                  <th className="text-left py-3 px-2 text-[#8b95a1] font-medium text-xs">날짜</th>
                  <th className="text-left py-3 px-2 text-[#8b95a1] font-medium text-xs">종목</th>
                  <th className="text-left py-3 px-2 text-[#8b95a1] font-medium text-xs">신호</th>
                  <th className="text-left py-3 px-2 text-[#8b95a1] font-medium text-xs">핵심 발언</th>
                  <th className="text-left py-3 px-2 text-[#8b95a1] font-medium text-xs">수익률</th>
                  <th className="text-left py-3 px-2 text-[#8b95a1] font-medium text-xs">출처</th>
                  <th className="text-left py-3 px-2 text-[#8b95a1] font-medium text-xs">영상</th>
                </tr>
              </thead>
              <tbody>
                {influencer.signalHistory.map((item, i) => (
                  <tr key={i} className="border-b border-[#f0f0f0] hover:bg-[#f8f9fa] cursor-pointer" onClick={() => setSelectedSignal(item)}>
                    <td className="py-3 px-2 text-[#191f28] whitespace-nowrap">{item.date}</td>
                    <td className="py-3 px-2">
                      <Link href={`/stock/${item.stockCode}?tab=influencer`} className="text-[#191f28] font-medium hover:text-[#3182f6]">
                        {item.stock}
                      </Link>
                    </td>
                    <td className="py-3 px-2">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium border ${getSignalColor(item.signal)}`}>
                        {item.signal}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-[#191f28] max-w-[200px] truncate">{item.content}</td>
                    <td className={`py-3 px-2 font-medium ${item.returnPct.startsWith('+') ? 'text-[#22c55e]' : 'text-[#ef4444]'}`}>{item.returnPct}</td>
                    <td className="py-3 px-2 text-[#8b95a1]">{item.source}</td>
                    <td className="py-3 px-2">
                      <button onClick={() => setSelectedSignal(item)} className="text-[#3182f6] hover:underline text-xs">▶ 영상</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* 영상 분석 팝업 */}
      {selectedSignal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setSelectedSignal(null)}>
          <div className="bg-white rounded-2xl max-w-lg w-full max-h-[85vh] overflow-y-auto shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between px-6 py-4 border-b border-[#e8e8e8]">
              <h3 className="font-bold text-[#191f28] text-lg">▶ 영상 분석</h3>
              <div className="flex items-center gap-2">
                <button className="w-9 h-9 rounded-full bg-[#f8f9fa] flex items-center justify-center text-[#8b95a1] hover:bg-[#e9ecef]" title="메모 저장">♡</button>
                <button className="w-9 h-9 rounded-full bg-[#f8f9fa] flex items-center justify-center text-[#8b95a1] hover:bg-[#e9ecef]" title="신고">⚠️</button>
                <button onClick={() => setSelectedSignal(null)} className="w-9 h-9 rounded-full bg-[#f8f9fa] flex items-center justify-center text-[#8b95a1] hover:bg-[#e9ecef]">✕</button>
              </div>
            </div>
            <div className="px-6 py-5">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-xl font-bold text-[#191f28]">{selectedSignal.stock}</span>
                <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getSignalColor(selectedSignal.signal)}`}>
                  {selectedSignal.signal}
                </span>
              </div>
              <p className="text-sm text-[#8b95a1] mb-5">{selectedSignal.videoTitle} · {selectedSignal.date}</p>
              <div className="mb-5">
                <div className="text-xs font-medium text-[#8b95a1] mb-2">💬 발언 내용</div>
                <div className="bg-[#f8f9fa] rounded-xl p-4 border border-[#e8e8e8]">
                  <p className="text-[#191f28] leading-relaxed text-[15px]">{selectedSignal.content}</p>
                  <p className="text-xs text-[#3182f6] mt-2">타임스탬프: {selectedSignal.timestamp}</p>
                </div>
              </div>
              <div className="mb-6">
                <div className="text-xs font-medium text-[#8b95a1] mb-2">📎 영상 요약</div>
                <p className="text-[#4e5968] text-sm leading-relaxed">{selectedSignal.summary}</p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => { setSelectedSignal(null); router.push(`/stock/${selectedSignal.stockCode}?tab=influencer`); }}
                  className="flex-1 py-3.5 bg-[#e8f4fd] text-[#3182f6] rounded-xl text-center font-medium hover:bg-[#d0e8fc] transition-colors border border-blue-200"
                >
                  📊 차트보기
                </button>
                <a href={selectedSignal.videoUrl} target="_blank" rel="noopener noreferrer" className="flex-1 py-3.5 bg-[#3182f6] text-white rounded-xl text-center font-medium hover:bg-[#2171e5] transition-colors">
                  ▶ 영상보기
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
