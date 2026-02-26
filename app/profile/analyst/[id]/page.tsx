import { notFound } from 'next/navigation'

interface AnalystData {
  id: string
  name: string
  avatar: string
  company: string
  sector: string
  reports: number
  coverStocks: number
  activePeriod: string
  stats: {
    accuracy6M: string
    accuracy12M: string
    avgDeviation: string
    rating: number
  }
  summaryCards: Array<{
    title: string
    value: string
    subtitle: string
  }>
  coverStocks: Array<{
    name: string
    code: string
    reports: number
  }>
  reportHistory: Array<{
    date: string
    stock: string
    opinion: 'BUY' | 'HOLD' | 'SELL'
    targetPrice: string
    currentPrice: string
    deviation: string
    aiSummary: string
  }>
}

// Mock data
const mockAnalysts: Record<string, AnalystData> = {
  'kim-sunwoo': {
    id: 'kim-sunwoo',
    name: '김선우',
    avatar: '📊',
    company: '한국투자증권',
    sector: 'IT/반도체',
    reports: 147,
    coverStocks: 28,
    activePeriod: '3년 2개월',
    stats: {
      accuracy6M: '72.4%',
      accuracy12M: '68.1%',
      avgDeviation: '8.3%',
      rating: 4.2
    },
    summaryCards: [
      {
        title: '최근 30일 리포트',
        value: '12건',
        subtitle: '전월 대비 +3건'
      },
      {
        title: '매수 의견 비율',
        value: '64%',
        subtitle: '업계 평균 58%'
      },
      {
        title: '목표가 달성 평균 기간',
        value: '4.2개월',
        subtitle: '업계 평균 5.1개월'
      }
    ],
    coverStocks: [
      { name: '삼성전자', code: '005930', reports: 12 },
      { name: 'SK하이닉스', code: '000660', reports: 8 },
      { name: 'LG에너지솔루션', code: '373220', reports: 6 },
      { name: 'NAVER', code: '035420', reports: 5 }
    ],
    reportHistory: [
      {
        date: '2026-02-25',
        stock: '삼성전자',
        opinion: 'BUY',
        targetPrice: '85,000',
        currentPrice: '74,200',
        deviation: '+14.6%',
        aiSummary: 'AI 반도체 수혜와 HBM 수요 증가로 실적 개선 전망'
      },
      {
        date: '2026-02-20',
        stock: 'SK하이닉스',
        opinion: 'BUY',
        targetPrice: '145,000',
        currentPrice: '138,500',
        deviation: '+4.7%',
        aiSummary: '메모리 반도체 사이클 회복과 AI 수요로 긍정적 전망'
      }
    ]
  }
}

function OpinionBadge({ opinion }: { opinion: string }) {
  const colors = {
    BUY: 'bg-blue-100 text-blue-700 border-blue-200',
    HOLD: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    SELL: 'bg-red-100 text-red-700 border-red-200'
  }
  
  const labels = {
    BUY: '매수',
    HOLD: '보유',
    SELL: '매도'
  }
  
  return (
    <span className={`px-2 py-1 rounded-full text-xs border ${colors[opinion as keyof typeof colors]}`}>
      {labels[opinion as keyof typeof labels]}
    </span>
  )
}

function TargetPriceChart() {
  return (
    <div className="bg-white border border-[#e8e8e8] rounded-lg p-4">
      <h3 className="font-semibold mb-4 text-[#191f28]">종목별 목표가 차트</h3>
      <div className="relative h-64">
        <svg viewBox="0 0 400 200" className="w-full h-full">
          {/* Grid lines */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#f0f0f0" strokeWidth="1"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
          
          {/* Current price line */}
          <line x1="0" y1="120" x2="400" y2="120" stroke="#6b7280" strokeWidth="2" strokeDasharray="5,5"/>
          
          {/* Target price bars */}
          <rect x="50" y="80" width="30" height="40" fill="#3b82f6" opacity="0.7"/>
          <rect x="120" y="70" width="30" height="50" fill="#3b82f6" opacity="0.7"/>
          <rect x="190" y="90" width="30" height="30" fill="#3b82f6" opacity="0.7"/>
          <rect x="260" y="60" width="30" height="60" fill="#3b82f6" opacity="0.7"/>
          
          {/* Labels */}
          <text x="65" y="140" textAnchor="middle" className="text-xs fill-current">삼성전자</text>
          <text x="135" y="140" textAnchor="middle" className="text-xs fill-current">SK하이닉스</text>
          <text x="205" y="140" textAnchor="middle" className="text-xs fill-current">LG에너지</text>
          <text x="275" y="140" textAnchor="middle" className="text-xs fill-current">NAVER</text>
        </svg>
        
        <div className="absolute bottom-2 left-4 flex gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-blue-500 opacity-70"></div>
            <span>목표가</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-1 bg-gray-500"></div>
            <span>현재가</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function StarRating({ rating }: { rating: number }) {
  const stars = []
  const fullStars = Math.floor(rating)
  const hasHalfStar = rating % 1 !== 0
  
  for (let i = 0; i < fullStars; i++) {
    stars.push(<span key={i} className="text-yellow-400">★</span>)
  }
  
  if (hasHalfStar) {
    stars.push(<span key="half" className="text-yellow-400">☆</span>)
  }
  
  const emptyStars = 5 - Math.ceil(rating)
  for (let i = 0; i < emptyStars; i++) {
    stars.push(<span key={`empty-${i}`} className="text-gray-300">☆</span>)
  }
  
  return <div className="flex items-center gap-1">{stars}</div>
}

export default function AnalystProfile({ params }: { params: { id: string } }) {
  const analyst = mockAnalysts[params.id]
  
  if (!analyst) {
    notFound()
  }
  
  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white border border-[#e8e8e8] rounded-lg p-6">
        <div className="flex gap-5 items-start">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-2xl font-bold flex-shrink-0">
            {analyst.avatar}
          </div>
          
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-xl font-bold text-[#191f28]">{analyst.name}</h1>
              <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full border border-green-200">
                {analyst.company}
              </span>
              <span className="px-2 py-1 bg-gray-100 text-[#191f28] text-xs rounded-full border border-gray-200">
                {analyst.sector}
              </span>
            </div>
            
            <div className="flex gap-6 mb-4 text-sm text-[#8b95a1]">
              <div>
                <div className="font-semibold text-[#191f28]">{analyst.reports}</div>
                <div>리포트 수</div>
              </div>
              <div>
                <div className="font-semibold text-[#191f28]">{analyst.coverStocks}</div>
                <div>커버 종목</div>
              </div>
              <div>
                <div className="font-semibold text-[#191f28]">{analyst.activePeriod}</div>
                <div>활동 기간</div>
              </div>
            </div>
          </div>
          
          <button className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors">
            팔로우
          </button>
        </div>
      </div>
      
      {/* Statistics */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white border border-[#e8e8e8] rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-600 mb-1">{analyst.stats.accuracy6M}</div>
          <div className="text-sm text-[#8b95a1]">6개월 적중률</div>
        </div>
        <div className="bg-white border border-[#e8e8e8] rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-600 mb-1">{analyst.stats.accuracy12M}</div>
          <div className="text-sm text-[#8b95a1]">12개월 적중률</div>
        </div>
        <div className="bg-white border border-[#e8e8e8] rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-[#191f28] mb-1">{analyst.stats.avgDeviation}</div>
          <div className="text-sm text-[#8b95a1]">평균 괴리율</div>
        </div>
        <div className="bg-white border border-[#e8e8e8] rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-[#191f28] mb-1 flex items-center justify-center">
            {analyst.stats.rating}
            <StarRating rating={analyst.stats.rating} />
          </div>
          <div className="text-sm text-[#8b95a1]">평점</div>
        </div>
      </div>
      
      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4">
        {analyst.summaryCards.map((card, index) => (
          <div key={index} className="bg-white border border-[#e8e8e8] rounded-lg p-4">
            <div className="text-sm text-[#8b95a1] mb-1">{card.title}</div>
            <div className="text-2xl font-bold text-[#191f28] mb-1">{card.value}</div>
            <div className="text-xs text-green-600">{card.subtitle}</div>
          </div>
        ))}
      </div>
      
      {/* Cover Stocks */}
      <div className="bg-white border border-[#e8e8e8] rounded-lg p-6">
        <h2 className="font-semibold mb-4 text-[#191f28]">커버 종목</h2>
        <div className="flex flex-wrap gap-2">
          {analyst.coverStocks.map(stock => (
            <button
              key={stock.code}
              className="px-3 py-2 bg-gray-100 text-[#191f28] rounded-full text-sm border border-gray-200 hover:bg-gray-200 transition-colors"
            >
              {stock.name}({stock.reports})
            </button>
          ))}
        </div>
      </div>
      
      {/* Chart */}
      <TargetPriceChart />
      
      {/* Report History Table */}
      <div className="bg-white border border-[#e8e8e8] rounded-lg p-6">
        <h2 className="font-semibold mb-4 text-[#191f28]">리포트 이력</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#e8e8e8]">
                <th className="text-left py-3 text-[#8b95a1] font-medium">날짜</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">종목</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">의견</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">목표가</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">현재가</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">괴리율</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">AI 요약</th>
              </tr>
            </thead>
            <tbody>
              {analyst.reportHistory.map((report, index) => (
                <tr key={index} className="border-b border-[#f0f0f0]">
                  <td className="py-3 text-[#191f28]">{report.date}</td>
                  <td className="py-3 text-[#191f28]">{report.stock}</td>
                  <td className="py-3">
                    <OpinionBadge opinion={report.opinion} />
                  </td>
                  <td className="py-3 text-[#191f28] font-medium">{report.targetPrice}원</td>
                  <td className="py-3 text-[#191f28]">{report.currentPrice}원</td>
                  <td className="py-3 text-green-600 font-medium">{report.deviation}</td>
                  <td className="py-3 text-[#191f28] max-w-xs truncate">{report.aiSummary}</td>
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
    { id: 'kim-sunwoo' }
  ]
}