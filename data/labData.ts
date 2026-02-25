// TypeScript interfaces for Strategy Lab data

export interface DailyIdea {
  id: string;
  stockName: string;
  idea: string;
  entry: number;
  target: number;
  stop: number;
  targetPercent: number;
  stopPercent: number;
  winRate: number;
  totalTrades: number;
  successCount: number;
  tags: string[];
}

export interface BacktestResult {
  id: string;
  name: string;
  conditions: string[];
  totalTrades: number;
  winRate: number;
  avgReturn: number;
  maxReturn: number;
  maxLoss: number;
  cumulativeReturn: number;
  sharpe: number;
  equityPoints: { x: number; y: number }[];
}

export interface QuantBot {
  id: string;
  name: string;
  description: string;
  conditions: string[];
  status: 'active' | 'inactive';
  todaySignals: string[];
  sixMonthReturn: number;
}

export interface InfluencerSimulation {
  id: string;
  name: string;
  duration: string;
  initialAmount: number;
  currentAmount: number;
  returnPercent: number;
  winRate: number;
  totalTrades: number;
  sparklinePoints: number[];
}

export interface SwingIdea {
  id: string;
  type: 'ai' | 'community';
  stockName: string;
  description: string;
  entry?: number;
  target?: number;
  stop?: number;
  timeframe?: string;
  author?: string;
  likes?: number;
  comments?: number;
}

export interface LongTermIdea {
  id: string;
  type: 'ai-report' | 'community';
  title: string;
  description: string;
  readTime?: number;
  views?: number;
  relatedStocks?: string[];
  author?: string;
  isEditorPick?: boolean;
  likes?: number;
  comments?: number;
}

// Dummy data
export const dailyIdeas: DailyIdea[] = [
  {
    id: '1',
    stockName: '에코프로비엠',
    idea: '2차전지 업계 실적 개선과 함께 중국 소재 수급 안정화로 마진 개선 기대. 기술적으로도 20일선 돌파 후 상승 모멘텀 확인.',
    entry: 92000,
    target: 98500,
    stop: 88000,
    targetPercent: 7.1,
    stopPercent: -4.3,
    winRate: 68,
    totalTrades: 25,
    successCount: 17,
    tags: ['수급전환', '기술적반등', '거래량급증']
  },
  {
    id: '2',
    stockName: '포스코DX',
    idea: '4Q 실적 서프라이즈 기대감과 함께 데이터센터 확장 투자로 성장성 부각. 애널리스트 목표가 상향도 긍정적 모멘텀.',
    entry: 38200,
    target: 42000,
    stop: 36000,
    targetPercent: 9.9,
    stopPercent: -5.8,
    winRate: 72,
    totalTrades: 18,
    successCount: 13,
    tags: ['실적서프라이즈', '애널상향', '기관매수']
  },
  {
    id: '3',
    stockName: '한화에어로스페이스',
    idea: '방산 수출 확대와 국가간 장비 현대화 수요 증가로 수주 잔고 확대 전망. 외국인 순매수도 지속되고 있어 상승 동력 충분.',
    entry: 285000,
    target: 310000,
    stop: 272000,
    targetPercent: 8.8,
    stopPercent: -4.6,
    winRate: 65,
    totalTrades: 31,
    successCount: 20,
    tags: ['테마강세', '수주잔고', '외국인순매수']
  }
];

export const backtestResults: BacktestResult[] = [
  {
    id: '1',
    name: '공시 전략',
    conditions: ['A등급 공시', '시총 1000억 이하', '거래량 전일대비 200%+'],
    totalTrades: 147,
    winRate: 64.6,
    avgReturn: 6.8,
    maxReturn: 32.4,
    maxLoss: -18.2,
    cumulativeReturn: 189.3,
    sharpe: 1.42,
    equityPoints: [
      { x: 0, y: 100 }, { x: 1, y: 105 }, { x: 2, y: 103 }, { x: 3, y: 108 },
      { x: 4, y: 112 }, { x: 5, y: 115 }, { x: 6, y: 118 }, { x: 7, y: 125 },
      { x: 8, y: 130 }, { x: 9, y: 128 }, { x: 10, y: 135 }, { x: 11, y: 140 },
      { x: 12, y: 145 }, { x: 13, y: 150 }, { x: 14, y: 155 }, { x: 15, y: 160 },
      { x: 16, y: 165 }, { x: 17, y: 170 }, { x: 18, y: 175 }, { x: 19, y: 180 },
      { x: 20, y: 185 }, { x: 21, y: 189 }
    ]
  }
];

export const presetStrategies = [
  { name: '고PER 반등 전략', winRate: 58.3 },
  { name: '외국인 순매수 추종', winRate: 71.2 },
  { name: '실적 서프라이즈 전략', winRate: 69.8 }
];

export const quantBots: QuantBot[] = [
  {
    id: '1',
    name: '공시 사냥꾼',
    description: 'A등급 공시 발표 후 거래량 급증 종목을 실시간 감지하여 자동 매매',
    conditions: ['A등급 공시 발표', '거래량 300% 이상', '시총 500억~3000억', '상한가 제외'],
    status: 'active',
    todaySignals: ['아이빔테크놀로지'],
    sixMonthReturn: 45.2
  },
  {
    id: '2',
    name: '수급 추적기',
    description: '기관과 외국인의 대량 매수 패턴을 분석하여 수급 전환 시점을 포착',
    conditions: ['외국인 3일 연속 순매수', '기관 매수량 평균 200% 이상', '개인 매도 우세'],
    status: 'active',
    todaySignals: ['에코프로', 'SK하이닉스'],
    sixMonthReturn: 28.7
  }
];

export const influencerSimulations: InfluencerSimulation[] = [
  {
    id: '1',
    name: '코린이아빠',
    duration: '6개월',
    initialAmount: 100000000,
    currentAmount: 123400000,
    returnPercent: 23.4,
    winRate: 68,
    totalTrades: 34,
    sparklinePoints: [100, 105, 103, 108, 112, 115, 118, 125, 130, 128, 135, 140, 145, 150, 155, 160, 165, 170, 175, 180, 185, 190, 188, 192, 195, 200, 205, 210, 208, 215, 220, 223, 225, 230, 234]
  },
  {
    id: '2',
    name: '주식하는의사',
    duration: '6개월',
    initialAmount: 100000000,
    currentAmount: 131800000,
    returnPercent: 31.8,
    winRate: 72,
    totalTrades: 28,
    sparklinePoints: [100, 108, 106, 112, 118, 120, 125, 132, 138, 135, 142, 148, 152, 158, 162, 168, 172, 178, 182, 185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 318]
  }
];

export const swingIdeas: SwingIdea[] = [
  {
    id: '1',
    type: 'ai',
    stockName: 'POSCO홀딩스',
    description: 'RSI 과매도 구간에서 외국인 매수 전환, 철강 가격 상승 기대감으로 2-4주 스윙 추천',
    entry: 342000,
    target: 380000,
    stop: 325000,
    timeframe: '2-4주'
  },
  {
    id: '2',
    type: 'community',
    stockName: '세아제강',
    description: '조선 수주 호조와 밸류업 기대, 저PER 구간에서 매수 기회',
    author: '가치투자연구소',
    likes: 89,
    comments: 23
  }
];

export const longTermIdeas: LongTermIdea[] = [
  {
    id: '1',
    type: 'ai-report',
    title: '2025년 방산 섹터 전망',
    description: 'AI 분석: 글로벌 방산비 증가 트렌드와 한국 방산업체 수혜주 분석 리포트',
    readTime: 15,
    views: 2340,
    relatedStocks: ['한화에어로', '현대로템', 'LIG넥스원']
  },
  {
    id: '2',
    type: 'community',
    title: '삼성전자 저평가론',
    description: '반도체 슈퍼사이클 진입 전 마지막 저점 매수 기회 분석',
    author: '반도체마니아',
    isEditorPick: true,
    likes: 156,
    comments: 67
  },
  {
    id: '3',
    type: 'community',
    title: '2차전지 밸류체인 완전 분석',
    description: 'EV 시장 성장과 함께하는 소재-부품-완성품 투자 로드맵',
    author: '배터리연구소',
    likes: 98,
    comments: 34
  }
];

export interface LabCard {
  id: string;
  icon: string;
  iconBgColor: string;
  title: string;
  description: string;
  badge: string;
  badgeColor: string;
}

export const labCards: LabCard[] = [
  {
    id: 'daily',
    icon: '🎯',
    iconBgColor: 'bg-red-500',
    title: '내일의 단타 아이디어',
    description: 'AI가 매일 분석하는 단타 후보 종목과 진입/목표가 정보를 확인하세요.',
    badge: '매일 업데이트',
    badgeColor: 'bg-red-100 text-red-600'
  },
  {
    id: 'backtest',
    icon: '📊',
    iconBgColor: 'bg-green-500',
    title: '공시 전략 백테스트',
    description: '나만의 투자 전략을 백테스트로 검증하고 수익률을 미리 확인해보세요.',
    badge: 'PRO 기능',
    badgeColor: 'bg-blue-100 text-blue-600'
  },
  {
    id: 'quant',
    icon: '🤖',
    iconBgColor: 'bg-purple-500',
    title: 'AI 퀀트봇 생성',
    description: '조건을 설정하면 AI가 자동으로 매매하는 퀀트 전략을 만들어보세요.',
    badge: 'PRO+ 기능',
    badgeColor: 'bg-purple-100 text-purple-600'
  },
  {
    id: 'influencer',
    icon: '👤',
    iconBgColor: 'bg-orange-500',
    title: '인플루언서 전략 시뮬레이션',
    description: '인기 투자 인플루언서들의 포트폴리오를 따라하면 얼마나 벌 수 있을까요?',
    badge: '인기 기능',
    badgeColor: 'bg-orange-100 text-orange-600'
  },
  {
    id: 'swing',
    icon: '📈',
    iconBgColor: 'bg-teal-500',
    title: '스윙 연구소',
    description: 'AI 추천 스윙 종목과 커뮤니티 인기 중장기 아이디어를 모아봤습니다.',
    badge: '커뮤니티',
    badgeColor: 'bg-teal-100 text-teal-600'
  },
  {
    id: 'longterm',
    icon: '📚',
    iconBgColor: 'bg-navy-500',
    title: '장기투자 아이디어',
    description: 'AI 리포트와 에디터가 엄선한 장기 투자 아이디어를 확인하세요.',
    badge: '에디터 큐레이션',
    badgeColor: 'bg-indigo-100 text-indigo-600'
  }
];