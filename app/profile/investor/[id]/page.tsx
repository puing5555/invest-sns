import { notFound } from 'next/navigation'

interface InvestorData {
  id: string
  name: string
  avatar: string
  type: '재벌총수' | '등기임원' | '슈퍼개미' | '행동주의펀드' | '기관'
  position: string
  companies: string[]
  stats: {
    totalTrades: number
    netPurchase: string
    avgReturnAfterBuy: string
  }
  holdings: Array<{
    name: string
    code: string
    trades: number
    ownership?: string
  }>
  tradingHistory: Array<{
    date: string
    stock: string
    action: 'BUY' | 'SELL'
    amount: string
    price: string
    ownership?: string
    purpose?: string
  }>
  majorHoldings: Array<{
    name: string
    code: string
    ownership: string
    value: string
  }>
}

// Mock data
const mockInvestors: Record<string, InvestorData> = {
  'lee-jaeyong': {
    id: 'lee-jaeyong',
    name: '이재용',
    avatar: '👑',
    type: '재벌총수',
    position: '삼성전자 회장',
    companies: ['삼성전자', '삼성물산', '삼성생명'],
    stats: {
      totalTrades: 47,
      netPurchase: '+2,847억원',
      avgReturnAfterBuy: '+18.4%'
    },
    holdings: [
      { name: '삼성전자', code: '005930', trades: 18 },
      { name: '삼성물산', code: '028260', trades: 3 },
      { name: '삼성생명', code: '032830', trades: 2 }
    ],
    tradingHistory: [
      {
        date: '2026-02-20',
        stock: '삼성전자',
        action: 'BUY',
        amount: '156억원',
        price: '73,500',
        ownership: '4.18%',
        purpose: '경영권 안정화'
      },
      {
        date: '2026-01-15',
        stock: '삼성물산',
        action: 'BUY',
        amount: '89억원',
        price: '105,000',
        ownership: '18.3%'
      }
    ],
    majorHoldings: [
      {
        name: '삼성전자',
        code: '005930',
        ownership: '4.18%',
        value: '1조 2,847억원'
      },
      {
        name: '삼성물산',
        code: '028260',
        ownership: '18.3%',
        value: '3,142억원'
      }
    ]
  }
}

function ActionBadge({ action }: { action: 'BUY' | 'SELL' }) {
  const colors = {
    BUY: 'bg-blue-100 text-blue-700 border-blue-200',
    SELL: 'bg-red-100 text-red-700 border-red-200'
  }
  
  const labels = {
    BUY: '매수',
    SELL: '매도'
  }
  
  const icons = {
    BUY: '▲',
    SELL: '▼'
  }
  
  return (
    <span className={`px-2 py-1 rounded-full text-xs border flex items-center gap-1 ${colors[action]}`}>
      <span>{icons[action]}</span>
      {labels[action]}
    </span>
  )
}

function TradingChart() {
  return (
    <div className="bg-white border border-[#e8e8e8] rounded-lg p-4">
      <h3 className="font-semibold mb-4 text-[#191f28]">매매 차트</h3>
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
            points="0,150 50,130 100,110 150,90 200,100 250,80 300,70 350,60 400,50"
          />
          
          {/* Buy markers */}
          <polygon points="50,130 45,120 55,120" fill="#3b82f6" />
          <polygon points="150,90 145,80 155,80" fill="#3b82f6" />
          <polygon points="300,70 295,60 305,60" fill="#3b82f6" />
          
          {/* Sell markers */}
          <polygon points="200,100 195,110 205,110" fill="#ef4444" />
        </svg>
        
        <div className="absolute bottom-2 left-4 flex gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-0 h-0 border-l-2 border-r-2 border-b-3 border-transparent border-b-blue-500"></div>
            <span>매수</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-0 h-0 border-l-2 border-r-2 border-t-3 border-transparent border-t-red-500"></div>
            <span>매도</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function HoldingsChart({ holdings }: { holdings: InvestorData['majorHoldings'] }) {
  return (
    <div className="bg-white border border-[#e8e8e8] rounded-lg p-4">
      <h3 className="font-semibold mb-4 text-[#191f28]">보유 지분 (5% 이상)</h3>
      <div className="space-y-4">
        {holdings.map((holding, index) => {
          const percentage = parseFloat(holding.ownership)
          const width = Math.min((percentage / 20) * 100, 100) // 최대 20%를 100%로 표시
          
          return (
            <div key={index}>
              <div className="flex justify-between items-center mb-2">
                <span className="font-medium text-[#191f28]">{holding.name}</span>
                <div className="text-right">
                  <div className="text-sm font-medium text-[#191f28]">{holding.ownership}</div>
                  <div className="text-xs text-[#8b95a1]">{holding.value}</div>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${width}%` }}
                ></div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function getTypeColor(type: string) {
  const colors = {
    '재벌총수': 'bg-purple-100 text-purple-700 border-purple-200',
    '등기임원': 'bg-blue-100 text-blue-700 border-blue-200',
    '슈퍼개미': 'bg-green-100 text-green-700 border-green-200',
    '행동주의펀드': 'bg-orange-100 text-orange-700 border-orange-200',
    '기관': 'bg-gray-100 text-gray-700 border-gray-200'
  }
  return colors[type as keyof typeof colors] || colors['기관']
}

export default function InvestorProfile({ params }: { params: { id: string } }) {
  const investor = mockInvestors[params.id]
  
  if (!investor) {
    notFound()
  }
  
  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white border border-[#e8e8e8] rounded-lg p-6">
        <div className="flex gap-5 items-start">
          <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center text-2xl font-bold flex-shrink-0">
            {investor.avatar}
          </div>
          
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-xl font-bold text-[#191f28]">{investor.name}</h1>
              <span className={`px-2 py-1 text-xs rounded-full border ${getTypeColor(investor.type)}`}>
                {investor.type}
              </span>
              <span className="px-2 py-1 bg-gray-100 text-[#191f28] text-xs rounded-full border border-gray-200">
                {investor.position}
              </span>
            </div>
            
            <div className="flex flex-wrap gap-2 mb-4">
              {investor.companies.map(company => (
                <span
                  key={company}
                  className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full border border-blue-200"
                >
                  {company}
                </span>
              ))}
            </div>
          </div>
          
          <button className="px-4 py-2 bg-[#3182f6] text-white rounded-lg text-sm font-medium hover:bg-[#2171e5] transition-colors">
            알림 받기
          </button>
        </div>
      </div>
      
      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white border border-[#e8e8e8] rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-[#191f28] mb-1">{investor.stats.totalTrades}</div>
          <div className="text-sm text-[#8b95a1]">총 매매 건수</div>
        </div>
        <div className="bg-white border border-[#e8e8e8] rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-600 mb-1">{investor.stats.netPurchase}</div>
          <div className="text-sm text-[#8b95a1]">순매수 금액</div>
        </div>
        <div className="bg-white border border-[#e8e8e8] rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-600 mb-1">{investor.stats.avgReturnAfterBuy}</div>
          <div className="text-sm text-[#8b95a1]">매수 후 평균 수익률</div>
        </div>
      </div>
      
      {/* Holdings Tags */}
      <div className="bg-white border border-[#e8e8e8] rounded-lg p-6">
        <h2 className="font-semibold mb-4 text-[#191f28]">보유 종목</h2>
        <div className="flex flex-wrap gap-2">
          {investor.holdings.map(holding => (
            <button
              key={holding.code}
              className="px-3 py-2 bg-[#f2f4f6] text-[#191f28] rounded-full text-sm border border-[#e8e8e8] hover:bg-[#e9ecef] transition-colors"
            >
              {holding.name} {holding.trades}건
            </button>
          ))}
        </div>
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TradingChart />
        <HoldingsChart holdings={investor.majorHoldings} />
      </div>
      
      {/* Trading History Table */}
      <div className="bg-white border border-[#e8e8e8] rounded-lg p-6">
        <h2 className="font-semibold mb-4 text-[#191f28]">매매/지분변동 이력</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#e8e8e8]">
                <th className="text-left py-3 text-[#8b95a1] font-medium">날짜</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">종목</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">구분</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">금액</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">단가</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">지분율</th>
                <th className="text-left py-3 text-[#8b95a1] font-medium">목적</th>
              </tr>
            </thead>
            <tbody>
              {investor.tradingHistory.map((trade, index) => (
                <tr key={index} className="border-b border-[#f0f0f0]">
                  <td className="py-3 text-[#191f28]">{trade.date}</td>
                  <td className="py-3 text-[#191f28]">{trade.stock}</td>
                  <td className="py-3">
                    <ActionBadge action={trade.action} />
                  </td>
                  <td className="py-3 text-[#191f28] font-medium">{trade.amount}</td>
                  <td className="py-3 text-[#191f28]">{trade.price}원</td>
                  <td className="py-3 text-[#191f28]">{trade.ownership || '-'}</td>
                  <td className="py-3 text-[#8b95a1]">{trade.purpose || '-'}</td>
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
    { id: 'lee-jaeyong' }
  ]
}