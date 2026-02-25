export interface SignalBadge {
  icon: string;
  label: string;
}

export interface WatchlistStock {
  id: string;
  name: string;
  code: string;
  currentPrice: number;
  changePercent: number;
  buyPrice: number | null;
  profitRate: number | null;
  badges: SignalBadge[];
  alert: {
    message: string;
    timeAgo: string;
  };
  memo: string | null;
}

export const watchlistStocks: WatchlistStock[] = [
  {
    id: '1',
    name: '삼성전자',
    code: '005930',
    currentPrice: 71200,
    changePercent: 0.8,
    buyPrice: 68000,
    profitRate: 4.7,
    badges: [
      { icon: '👔', label: '임원매수' },
      { icon: '🎯', label: '애널상향' }
    ],
    alert: {
      message: '부사장 3일 연속 매수 감지',
      timeAgo: '2시간전'
    },
    memo: '7만 밑에서 추가매수 고려'
  },
  {
    id: '2',
    name: '에코프로',
    code: '086520',
    currentPrice: 248000,
    changePercent: 3.2,
    buyPrice: null,
    profitRate: null,
    badges: [
      { icon: '👤', label: '인플3명콜 🔥' },
      { icon: '🏦', label: '기관순매수' },
      { icon: '📈', label: '거래량급증' }
    ],
    alert: {
      message: '코린이아빠 매수콜',
      timeAgo: '4시간전'
    },
    memo: '25만 밑 분할매수, 목표 32만'
  },
  {
    id: '3',
    name: 'SK하이닉스',
    code: '000660',
    currentPrice: 182000,
    changePercent: 1.8,
    buyPrice: 175000,
    profitRate: 4.0,
    badges: [
      { icon: '🎯', label: '애널상향' },
      { icon: '🏦', label: '외국인순매수' }
    ],
    alert: {
      message: '한투 김OO 목표가 210,000 상향',
      timeAgo: '오늘'
    },
    memo: null
  },
  {
    id: '4',
    name: '아이빔테크놀로지',
    code: '399720',
    currentPrice: 32400,
    changePercent: 5.1,
    buyPrice: 30000,
    profitRate: 8.0,
    badges: [
      { icon: '📋', label: 'A등급공시' },
      { icon: '👤', label: '인플콜' }
    ],
    alert: {
      message: '공급계약 161억 공시',
      timeAgo: '오늘'
    },
    memo: '공급계약 공시 나오면 추가매수'
  },
  {
    id: '5',
    name: 'HD한국조선해양',
    code: '009540',
    currentPrice: 187500,
    changePercent: 2.1,
    buyPrice: 192000,
    profitRate: -2.3,
    badges: [
      { icon: '🎯', label: '애널상향' }
    ],
    alert: {
      message: 'NH투자 목표가 195,000',
      timeAgo: '어제'
    },
    memo: '조선 수주 사이클 장기 보유'
  }
];

export const searchResults = [
  '삼성전자',
  '에코프로',
  'SK하이닉스',
  'POSCO홀딩스',
  '현대차',
  '카카오',
  'NAVER',
  'LG에너지솔루션'
];