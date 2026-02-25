export interface CallRecord {
  stock: string;
  date: string;
  direction: '매수' | '매도';
  callPrice: number;
  currentPrice: number;
  returnRate: number;
  status: '진행중' | '적중' | '손절';
}

export interface Platform {
  name: '유튜브' | '텔레그램' | '블로그';
  color: string;
}

export interface MonthlyAccuracy {
  month: string;
  rate: number;
}

export interface Influencer {
  id: string;
  name: string;
  platforms: Platform[];
  followers: string;
  accuracy: number;
  totalCalls: number;
  successfulCalls: number;
  avgReturn: number;
  recentCalls: CallRecord[];
  bio?: string;
  activityPeriod?: string;
  monthlyAccuracy?: MonthlyAccuracy[];
  fullCallHistory?: CallRecord[];
  topStocks?: string[];
}

const platformConfig = {
  유튜브: { name: '유튜브' as const, color: '#ff0000' },
  텔레그램: { name: '텔레그램' as const, color: '#0088cc' },
  블로그: { name: '블로그' as const, color: '#03c75a' },
};

export const influencerData: Influencer[] = [
  {
    id: '1',
    name: '코린이아빠',
    platforms: [platformConfig.유튜브, platformConfig.텔레그램],
    followers: '12.3만',
    accuracy: 68,
    totalCalls: 50,
    successfulCalls: 34,
    avgReturn: 18.4,
    bio: "유튜브에서 소형주 분석으로 유명한 투자 크리에이터",
    activityPeriod: "2년 3개월",
    monthlyAccuracy: [
      { month: '9월', rate: 72 },
      { month: '10월', rate: 65 },
      { month: '11월', rate: 70 },
      { month: '12월', rate: 68 },
      { month: '1월', rate: 71 },
      { month: '2월', rate: 66 }
    ],
    recentCalls: [
      {
        stock: '에코프로',
        date: '02/20',
        direction: '매수',
        callPrice: 85000,
        currentPrice: 95540,
        returnRate: 12.4,
        status: '진행중'
      },
      {
        stock: '한화에어로',
        date: '02/15',
        direction: '매수',
        callPrice: 45000,
        currentPrice: 48915,
        returnRate: 8.7,
        status: '적중'
      },
      {
        stock: '카카오',
        date: '02/10',
        direction: '매수',
        callPrice: 58000,
        currentPrice: 54984,
        returnRate: -5.2,
        status: '손절'
      }
    ],
    fullCallHistory: [
      {
        stock: '에코프로',
        date: '02/20',
        direction: '매수',
        callPrice: 85000,
        currentPrice: 95540,
        returnRate: 12.4,
        status: '진행중'
      },
      {
        stock: '한화에어로',
        date: '02/15',
        direction: '매수',
        callPrice: 45000,
        currentPrice: 48915,
        returnRate: 8.7,
        status: '적중'
      },
      {
        stock: '카카오',
        date: '02/10',
        direction: '매수',
        callPrice: 58000,
        currentPrice: 54984,
        returnRate: -5.2,
        status: '손절'
      },
      {
        stock: 'LG에너지솔루션',
        date: '02/05',
        direction: '매수',
        callPrice: 420000,
        currentPrice: 546000,
        returnRate: 30.0,
        status: '적중'
      },
      {
        stock: '삼성SDI',
        date: '01/30',
        direction: '매수',
        callPrice: 780000,
        currentPrice: 960600,
        returnRate: 23.2,
        status: '적중'
      },
      {
        stock: '포스코케미칼',
        date: '01/25',
        direction: '매수',
        callPrice: 110000,
        currentPrice: 132000,
        returnRate: 20.0,
        status: '적중'
      },
      {
        stock: 'SK이노베이션',
        date: '01/20',
        direction: '매수',
        callPrice: 150000,
        currentPrice: 135000,
        returnRate: -10.0,
        status: '손절'
      },
      {
        stock: '현대차',
        date: '01/15',
        direction: '매수',
        callPrice: 190000,
        currentPrice: 218500,
        returnRate: 15.0,
        status: '적중'
      },
      {
        stock: '기아',
        date: '01/10',
        direction: '매수',
        callPrice: 88000,
        currentPrice: 101200,
        returnRate: 15.0,
        status: '적중'
      },
      {
        stock: '셀트리온',
        date: '01/05',
        direction: '매수',
        callPrice: 180000,
        currentPrice: 162000,
        returnRate: -10.0,
        status: '손절'
      }
    ],
    topStocks: ['LG에너지솔루션 (+30.0%)', '삼성SDI (+23.2%)', '포스코케미칼 (+20.0%)']
  },
  {
    id: '2',
    name: '주식하는의사',
    platforms: [platformConfig.유튜브],
    followers: '8.7만',
    accuracy: 72,
    totalCalls: 50,
    successfulCalls: 36,
    avgReturn: 22.1,
    recentCalls: [
      {
        stock: '삼성전자',
        date: '02/22',
        direction: '매수',
        callPrice: 75000,
        currentPrice: 77400,
        returnRate: 3.2,
        status: '진행중'
      },
      {
        stock: 'SK하이닉스',
        date: '02/18',
        direction: '매수',
        callPrice: 140000,
        currentPrice: 149520,
        returnRate: 6.8,
        status: '적중'
      },
      {
        stock: 'POSCO홀딩스',
        date: '02/12',
        direction: '매수',
        callPrice: 380000,
        currentPrice: 422940,
        returnRate: 11.3,
        status: '적중'
      }
    ]
  },
  {
    id: '3',
    name: '텔레그램큰손',
    platforms: [platformConfig.텔레그램],
    followers: '3.2만',
    accuracy: 58,
    totalCalls: 50,
    successfulCalls: 29,
    avgReturn: 31.5,
    recentCalls: [
      {
        stock: '아이빔테크',
        date: '02/24',
        direction: '매수',
        callPrice: 15600,
        currentPrice: 16395,
        returnRate: 5.1,
        status: '진행중'
      },
      {
        stock: '토비스',
        date: '02/19',
        direction: '매수',
        callPrice: 24000,
        currentPrice: 22008,
        returnRate: -8.3,
        status: '손절'
      },
      {
        stock: '씨케이솔루션',
        date: '02/14',
        direction: '매수',
        callPrice: 18500,
        currentPrice: 23809,
        returnRate: 28.7,
        status: '적중'
      }
    ]
  },
  {
    id: '4',
    name: '가치투자연구소',
    platforms: [platformConfig.유튜브, platformConfig.블로그],
    followers: '5.1만',
    accuracy: 75,
    totalCalls: 20,
    successfulCalls: 15,
    avgReturn: 15.2,
    recentCalls: [
      {
        stock: 'HD한국조선',
        date: '02/20',
        direction: '매수',
        callPrice: 175000,
        currentPrice: 182875,
        returnRate: 4.5,
        status: '진행중'
      },
      {
        stock: '세아제강',
        date: '02/10',
        direction: '매수',
        callPrice: 240000,
        currentPrice: 263520,
        returnRate: 9.8,
        status: '적중'
      },
      {
        stock: '롯데케미칼',
        date: '01/28',
        direction: '매수',
        callPrice: 250000,
        currentPrice: 268000,
        returnRate: 7.2,
        status: '적중'
      }
    ]
  },
  {
    id: '5',
    name: '단타의신',
    platforms: [platformConfig.텔레그램],
    followers: '15.8만',
    accuracy: 52,
    totalCalls: 150,
    successfulCalls: 78,
    avgReturn: 8.3,
    recentCalls: [
      {
        stock: '와이엠씨',
        date: '02/24',
        direction: '매수',
        callPrice: 8500,
        currentPrice: 8237,
        returnRate: -3.1,
        status: '진행중'
      },
      {
        stock: '에코프로비엠',
        date: '02/23',
        direction: '매수',
        callPrice: 180000,
        currentPrice: 185040,
        returnRate: 2.8,
        status: '진행중'
      },
      {
        stock: 'HLB',
        date: '02/22',
        direction: '매수',
        callPrice: 95000,
        currentPrice: 88825,
        returnRate: -6.5,
        status: '손절'
      }
    ]
  }
];