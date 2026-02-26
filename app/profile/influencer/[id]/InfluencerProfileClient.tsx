'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface StockTag {
  name: string;
  code: string;
  mentions: number;
}

interface SignalRecord {
  date: string;
  stock: string;
  stockCode: string;
  signal: string;
  content: string;
  returnPct: string;
  source: string;
  videoUrl: string;
  timestamp: string;
  summary: string;
  videoTitle: string;
}

interface InfluencerData {
  id: string;
  name: string;
  avatar: string;
  badge: string;
  subscribers: string;
  videos: number;
  mentions: number;
  avgReturn: string;
  positiveRatio: string;
  totalSignals: number;
  coverStocks: number;
  stocks: StockTag[];
  signalHistory: SignalRecord[];
}

const mockInfluencers: Record<string, InfluencerData> = {
  'syuka': {
    id: 'syuka',
    name: '슈카월드',
    avatar: '슈',
    badge: '유튜버',
    subscribers: '253만',
    videos: 482,
    mentions: 1247,
    avgReturn: '+12.3%',
    positiveRatio: '68%',
    totalSignals: 156,
    coverStocks: 23,
    stocks: [
      { name: '삼성전자', code: '005930', mentions: 28 },
      { name: 'NAVER', code: '035420', mentions: 15 },
      { name: '카카오', code: '035720', mentions: 12 },
      { name: '현대차', code: '005380', mentions: 9 },
      { name: '테슬라', code: 'TSLA', mentions: 7 },
    ],
    signalHistory: [
      { date: '02.24', stock: '삼성전자', stockCode: '005930', signal: 'BUY', content: '"5만원대면 무조건 담아야 합니다. HBM 수주 확대되면 실적 턴어라운드 확실합니다."', returnPct: '+8.3%', source: '본인채널', videoUrl: '#', timestamp: '[5:43]', videoTitle: '"삼성전자, 지금이 기회일까? 반도체 슈퍼사이클의 시작"', summary: '슈카는 삼성전자의 HBM3E 양산 본격화와 AI 반도체 수요 급증을 근거로 현재 주가가 저평가 구간이라고 분석했습니다.' },
      { date: '02.21', stock: 'NAVER', stockCode: '035420', signal: 'POSITIVE', content: '"AI 사업 방향성은 좋아 보입니다. 관심 가져볼 만합니다."', returnPct: '+3.1%', source: '삼프로TV', videoUrl: '#', timestamp: '[12:15]', videoTitle: '"네이버 AI, 구글과 경쟁 가능할까?"', summary: '슈카는 네이버의 하이퍼클로바X와 클라우드 사업 확장을 분석하며 AI 시대 국내 플랫폼 중 가장 유리한 위치라고 평가했습니다.' },
      { date: '02.18', stock: '카카오', stockCode: '035720', signal: 'NEUTRAL', content: '"지켜보자, 아직 판단 이르다"', returnPct: '-1.2%', source: '본인채널', videoUrl: '#', timestamp: '[8:30]', videoTitle: '"카카오, 바닥은 어디인가?"', summary: '슈카는 카카오의 구조조정 효과는 아직 미미하며, AI 전략이 구체화될 때까지 관망을 권했습니다.' },
      { date: '02.10', stock: '테슬라', stockCode: 'TSLA', signal: 'CONCERN', content: '"지금 테슬라는 좀 조심해야 합니다"', returnPct: '-5.1%', source: '본인채널', videoUrl: '#', timestamp: '[15:20]', videoTitle: '"테슬라 버블 논란, 팩트체크"', summary: '슈카는 테슬라의 높은 밸류에이션과 경쟁 심화를 우려하며 경계 의견을 제시했습니다.' },
      { date: '02.05', stock: '현대차', stockCode: '005380', signal: 'BUY', content: '"현대차 지금 저평가라고 봅니다. EV 라인업 본격화되면 재평가될 것"', returnPct: '+6.2%', source: '본인채널', videoUrl: '#', timestamp: '[3:17]', videoTitle: '"현대차, 전기차 전쟁의 승자는?"', summary: '슈카는 현대차의 전기차 라인업 확대와 미국 공장 가동을 근거로 저평가 판단했습니다.' },
      { date: '01.28', stock: '삼성전자', stockCode: '005930', signal: 'POSITIVE', content: '"반도체 업사이클 시작되고 있습니다"', returnPct: '+4.5%', source: '본인채널', videoUrl: '#', timestamp: '[7:55]', videoTitle: '"반도체 업사이클, 진짜 시작인가?"', summary: '슈카는 메모리 반도체 가격 반등과 AI 서버 수요 증가를 분석하며 긍정적 전망을 제시했습니다.' },
      { date: '01.20', stock: 'NAVER', stockCode: '035420', signal: 'BUY', content: '"네이버 지금 사면 1년 뒤 웃을 겁니다"', returnPct: '+11.2%', source: '삼프로TV', videoUrl: '#', timestamp: '[18:42]', videoTitle: '"네이버 vs 카카오, 어디에 투자할까?"', summary: '슈카는 네이버의 검색광고 독점력과 AI 투자 방향성을 높이 평가하며 매수를 권했습니다.' },
    ]
  }
};

function getSignalColor(signal: string) {
  switch (signal) {
    case 'BUY': return 'bg-blue-100 text-[#3182f6] border-blue-200';
    case 'POSITIVE': return 'bg-green-100 text-[#22c55e] border-green-200';
    case 'NEUTRAL': return 'bg-yellow-100 text-[#eab308] border-yellow-200';
    case 'CONCERN': return 'bg-orange-100 text-[#f97316] border-orange-200';
    case 'SELL': return 'bg-red-100 text-[#ef4444] border-red-200';
    default: return 'bg-gray-100 text-gray-600';
  }
}

function getSignalLabel(signal: string) {
  switch (signal) {
    case 'BUY': return '매수';
    case 'POSITIVE': return '긍정';
    case 'NEUTRAL': return '중립';
    case 'CONCERN': return '경계';
    case 'SELL': return '매도';
    default: return signal;
  }
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
  const [selectedSignal, setSelectedSignal] = useState<SignalRecord | null>(null);
  const influencer = mockInfluencers[id];

  if (!influencer) {
    return (
      <div className="min-h-screen bg-[#f4f4f4] flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">🔍</div>
          <h2 className="text-xl font-bold text-[#191f28] mb-2">인플루언서를 찾을 수 없습니다</h2>
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
                        {getSignalLabel(item.signal)}
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
                  {getSignalLabel(selectedSignal.signal)}
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
