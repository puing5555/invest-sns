import { notFound } from 'next/navigation'

interface InfluencerData {
  id: string
  name: string
  avatar: string
  badge: string
  subscribers: string
  videos: number
  mentions: number
  avgReturn: string
  positiveRatio: string
  totalSignals: number
  coverStocks: number
  stocks: Array<{
    name: string
    code: string
    mentions: number
  }>
  recentSignals: Array<{
    signal: 'BUY' | 'POSITIVE' | 'NEUTRAL' | 'CAUTION' | 'SELL'
    stock: string
    return: string
    content: string
    source: string
    date: string
  }>
  signalHistory: Array<{
    date: string
    stock: string
    signal: 'BUY' | 'POSITIVE' | 'NEUTRAL' | 'CAUTION' | 'SELL'
    content: string
    return: string
    source: string
    videoUrl?: string
  }>
}

// Mock data
const mockInfluencers: Record<string, InfluencerData> = {
  'syuka': {
    id: 'syuka',
    name: '슈카월드',
    avatar: '🎯',
    badge: '유튜버',
    subscribers: '82.4만',
    videos: 847,
    mentions: 156,
    avgReturn: '+24.6%',
    positiveRatio: '68.4%',
    totalSignals: 234,
    coverStocks: 42,
    stocks: [
      { name: '삼성전자', code: '005930', mentions: 28 },
      { name: 'NAVER', code: '035420', mentions: 15 },
      { name: 'SK하이닉스', code: '000660', mentions: 12 },
      { name: 'LG에너지솔루션', code: '373220', mentions: 8 }
    ],
    recentSignals: [
      {
        signal: 'BUY',
        stock: '삼성전자',
        return: '+12.3%',
        content: 'AI 반도체 수혜로 실적 개선 기대',
        source: '유튜브',
        date: '2026-02-25'
      },
      {
        signal: 'POSITIVE',
        stock: 'NAVER',
        return: '+8.7%',
        content: '클라우드 사업 성장으로 기대감 상승',
        source: '유튜브',
        date: '2026-02-24'
      }
    ],
    signalHistory: [
      {
        date: '2026-02-25',
        stock: '삼성전자',
        signal: 'BUY',
        content: 'AI 반도체 수혜로 실적 개선 기대',
        return: '+12.3%',
        source: '유튜브',
        videoUrl: 'https://youtube.com/watch?v=abc123'
      }
    ]
  }
}

function SignalBadge({ signal }: { signal: string }) {
  const colors = {
    BUY: 'bg-blue-100 text-blue-700 border-blue-200',
    POSITIVE: 'bg-green-100 text-green-700 border-green-200',
    NEUTRAL: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    CAUTION: 'bg-orange-100 text-orange-700 border-orange-200',
    SELL: 'bg-red-100 text-red-700 border-red-200'
  }
  
  const labels = {
    BUY: '매수',
    POSITIVE: '긍정',
    NEUTRAL: '중립',
    CAUTION: '경계',
    SELL: '매도'
  }
  
  return (
    <span className={`px-2 py-1 rounded-full text-xs border ${colors[signal as keyof typeof colors]}`}>
      {labels[signal as keyof typeof labels]}
    </span>
  )
}

function StockChart() {
  return (
    <div className="bg-white border border-[#e8e8e8] rounded-lg p-4">
      <h3 className="font-semibold mb-4 text-[#191f28]">종목별 신호 차트</h3>
      <div className="relative h-64">
        <svg viewBox="0 0 400 200" className="w-full h-full">
          {/* Grid lines */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#f0f0f0" strokeWidth="1"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
          
          {/* Price line */}
          <polyline
            fill="none"
            stroke="#6b7280"
            strokeWidth="2"
            points="0,150 50,120 100,100 150,80 200,90 250,70 300,60 350,50 400,40"
          />
          
          {/* Signal points */}
          <circle cx="50" cy="120" r="4" fill="#3b82f6" />
          <circle cx="150" cy="80" r="4" fill="#10b981" />
          <circle cx="250" cy="70" r="4" fill="#f59e0b" />
          <circle cx="350" cy="50" r="4" fill="#3b82f6" />
        </svg>
        
        <div className="absolute bottom-2 left-4 flex gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span>매수</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span>긍정</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <span>중립</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function InfluencerProfile({ params }: { params: { id: string } }) {
  const influencer = mockInfluencers[params.id]
  
  if (!influencer) {
    notFound()
  }
  
  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white border border-[#e8e8e8] rounded-lg p-6">
        <div className="flex gap-5 items-start">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-2xl font-bold flex-shrink-0">
            {influencer.avatar}
          </div>
          
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-xl font-bold text-[#191f28]">{influencer.name}</h1>
              <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full border border-red-200">
                {influencer.badge}
              </span>
            </div>
            
            <div className="flex gap-6 mb-4 text-sm text-[#8b95a1]">
              <div>
                <div className="font-semibold text-[#191f28]">{influencer.subscribers}</div>
                <div>구독자</div>
              </div>
              <div>
                <div className="font-semibold text-[#191f28]">{influencer.videos}</div>
                <div>영상 수</div>
              </div>
              <div>
                <div className="font-semibold text-[#191f28]">{influencer.mentions}</div>
                <div>종목 언급</div>
              </div>
            </div>
          </div>
          
          <button className="px-4 py-2 bg-[#3182f6] text-white rounded-lg text-sm font-medium hover:bg-[#2171e5] transition-colors">
            팔로우
          </button>
        </div>
      </div>
      
      {/* Statistics */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white border border-[#e8e8e8] rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-600 mb-1">{influencer.avgReturn}</div>
          <div className="text-sm text-[#8b95a1]">평균 수익률</div>
        </div>
        <div className="bg-white border border-[#e8e8e8] rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-600 mb-1">{influencer.positiveRatio}</div>
          <div className="text-sm text-[#8b95a1]">긍정 신호 비율</div>
        </div>
        <div className="bg-white border border-[#e8e8e8] rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-[#191f28] mb-1">{influencer.totalSignals}</div>
          <div className="text-sm text-[#8b95a1]">총 신호 수</div>
        </div>
        <div className="bg-white border border-[#e8e8e8] rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-[#191f28] mb-1">{influencer.coverStocks}</div>
          <div className="text-sm text-[#8b95a1]">커버 종목 수</div>
        </div>
      </div>
      
      {/* Stock Tags */}
      <div className="bg-white border border-[#e8e8e8] rounded-lg p-6">
        <h2 className="font-semibold mb-4 text-[#191f28]">관심 종목</h2>
        <div className="flex flex-wrap gap-2">
          {influencer.stocks.map(stock => (
            <button
              key={stock.code}
              className="px-3 py-2 bg-[#f2f4f6] text-[#191f28] rounded-full text-sm border border-[#e8e8e8] hover:bg-[#e9ecef] transition-colors"
            >
              {stock.name}({stock.mentions})
            </button>
          ))}
        </div>
      </div>
      
      {/* Recent Signals */}
      <div className="bg-white border border-[#e8e8e8] rounded-lg p-6">
        <h2 className="font-semibold mb-4 text-[#191f28]">최근 주요 발언</h2>
        <div className="space-y-4">
          {influencer.recentSignals.map((signal, index) => (
            <div key={index} className="border border-[#e8e8e8] rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <SignalBadge signal={signal.signal} />
                  <span className="font-medium text-[#191f28]">{signal.stock}</span>
                  <span className="text-green-600 text-sm font-medium">{signal.return}</span>
                </div>
                <span className="text-xs text-[#8b95a1]">{signal.date}</span>
              </div>
              <p className="text-[#191f28] mb-2">{signal.content}</p>
              <div className="text-xs text-[#8b95a1]">출처: {signal.source}</div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Chart */}
      <StockChart />
      
      {/* Signal History Table */}
      <div className="bg-white border border-[#e8e8e8] rounded-lg p-6">
        <h2 className="font-semibold mb-4 text-[#191f28]">전체 발언 이력</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#e8e8e8]">
                <th className="text-left py-3 text-[#8b95a1] font-medium">날짜</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">종목</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">신호</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">핵심 발언</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">수익률</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">출처</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">링크</th>
              </tr>
            </thead>
            <tbody>
              {influencer.signalHistory.map((item, index) => (
                <tr key={index} className="border-b border-[#f0f0f0]">
                  <td className="py-3 text-[#191f28]">{item.date}</td>
                  <td className="py-3 text-[#191f28]">{item.stock}</td>
                  <td className="py-3">
                    <SignalBadge signal={item.signal} />
                  </td>
                  <td className="py-3 text-[#191f28] max-w-xs truncate">{item.content}</td>
                  <td className="py-3 text-green-600 font-medium">{item.return}</td>
                  <td className="py-3 text-[#8b95a1]">{item.source}</td>
                  <td className="py-3">
                    {item.videoUrl && (
                      <a 
                        href={item.videoUrl} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-500 hover:underline"
                      >
                        영상 보기
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export async function generateStaticParams() {
  return [
    { id: 'syuka' }
  ]
}