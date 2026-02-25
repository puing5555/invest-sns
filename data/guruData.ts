export interface Holding {
  name: string;
  ticker: string;
  percentage: number;
}

export interface NewBuy {
  name: string;
  ticker: string;
  amount: string;
}

export interface Increase {
  name: string;
  ticker: string;
  percentage: number;
}

export interface Decrease {
  name: string;
  ticker: string;
  percentage: number;
}

export interface SoldStock {
  name: string;
  ticker: string;
}

export interface Sector {
  name: string;
  pct: number;
  color: string;
}

export interface Vote {
  follow: number;
  against: number;
  comments: number;
}

export interface GuruDetail {
  newBuys: NewBuy[];
  increased: Increase[];
  decreased: Decrease[];
  soldAll: SoldStock[];
  sectors: Sector[];
  aiInsight: string;
  vote: Vote;
}

export interface Guru {
  id: string;
  name: string;
  initials: string;
  fund: string;
  aum: string;
  lastUpdate: string;
  isRealtime?: boolean;
  hasWarning?: boolean;
  warningText?: string;
  realtimeNote?: string;
  changes: {
    newBuys: number;
    increased: number;
    decreased: number;
    sold: number;
  };
  topHoldings: Holding[];
  detail?: GuruDetail;
}

export const gurus: Guru[] = [
  {
    id: 'buffett',
    name: '워렌 버핏',
    initials: 'WB',
    fund: '버크셔 해서웨이',
    aum: '$312B',
    lastUpdate: '2025 Q4',
    changes: {
      newBuys: 2,
      increased: 3,
      decreased: 2,
      sold: 1
    },
    topHoldings: [
      { name: '애플', ticker: 'AAPL', percentage: 28.9 },
      { name: '뱅크오브아메리카', ticker: 'BAC', percentage: 8.9 },
      { name: '아멕스', ticker: 'AXP', percentage: 7.3 }
    ],
    detail: {
      newBuys: [
        { name: '컨스텔레이션', ticker: 'CEG', amount: '$1.2B' },
        { name: '풀트그룹', ticker: 'PHM', amount: '$800M' }
      ],
      increased: [
        { name: '옥시덴탈', ticker: 'OXY', percentage: 12 },
        { name: '쉐브론', ticker: 'CVX', percentage: 6 }
      ],
      decreased: [
        { name: '애플', ticker: 'AAPL', percentage: 8 }
      ],
      soldAll: [
        { name: 'HP엔터프라이즈', ticker: 'HPE' }
      ],
      sectors: [
        { name: '금융', pct: 42, color: '#3b82f6' },
        { name: 'IT', pct: 29, color: '#8b5cf6' },
        { name: '에너지', pct: 15, color: '#f59e0b' },
        { name: '소비재', pct: 8, color: '#22c55e' },
        { name: '기타', pct: 6, color: '#6b7280' }
      ],
      aiInsight: '에너지 비중 유지하면서 소비재 신규 진입. 빅테크 비중은 계속 줄이는 흐름. 현금 포지션 역대 최고치.',
      vote: { follow: 72, against: 28, comments: 23 }
    }
  },
  {
    id: 'cathie-wood',
    name: '캐시 우드',
    initials: 'CW',
    fund: 'ARK Invest',
    aum: '$8.2B',
    lastUpdate: '매일(실시간)',
    isRealtime: true,
    realtimeNote: '오늘: 테슬라 +12,000주',
    changes: {
      newBuys: 5,
      increased: 0,
      decreased: 0,
      sold: 3
    },
    topHoldings: [
      { name: '테슬라', ticker: 'TSLA', percentage: 11.2 },
      { name: '코인베이스', ticker: 'COIN', percentage: 8.4 },
      { name: '로쿠', ticker: 'ROKU', percentage: 6.1 }
    ]
  },
  {
    id: 'michael-burry',
    name: '마이클 버리',
    initials: 'MB',
    fund: '사이온 자산운용',
    aum: '$290M',
    lastUpdate: '2025 Q4',
    hasWarning: true,
    warningText: '포트 80% 교체',
    changes: {
      newBuys: 4,
      increased: 0,
      decreased: 0,
      sold: 6
    },
    topHoldings: [
      { name: '알리바바', ticker: 'BABA', percentage: 18 },
      { name: '바이두', ticker: 'BIDU', percentage: 12 },
      { name: 'JD닷컴', ticker: 'JD', percentage: 9 }
    ]
  },
  {
    id: 'ray-dalio',
    name: '레이 달리오',
    initials: 'RD',
    fund: '브리지워터',
    aum: '$124B',
    lastUpdate: '2025 Q4',
    changes: {
      newBuys: 0,
      increased: 8,
      decreased: 5,
      sold: 0
    },
    topHoldings: [
      { name: 'SPY', ticker: 'SPY', percentage: 9.2 },
      { name: '구글', ticker: 'GOOGL', percentage: 4.1 },
      { name: '엔비디아', ticker: 'NVDA', percentage: 3.8 }
    ]
  },
  {
    id: 'bill-ackman',
    name: '빌 애크먼',
    initials: 'BA',
    fund: '퍼싱스퀘어',
    aum: '$12.4B',
    lastUpdate: '2025 Q4',
    changes: {
      newBuys: 1,
      increased: 2,
      decreased: 0,
      sold: 0
    },
    topHoldings: [
      { name: '유니버설뮤직', ticker: 'UMG', percentage: 22 },
      { name: '치폴레', ticker: 'CMG', percentage: 18 },
      { name: '힐튼', ticker: 'HLT', percentage: 15 }
    ]
  },
  {
    id: 'stanley-druckenmiller',
    name: '스탠리 드러큰밀러',
    initials: 'SD',
    fund: '듀케인',
    aum: '$3.8B',
    lastUpdate: '2025 Q4',
    changes: {
      newBuys: 3,
      increased: 0,
      decreased: 0,
      sold: 4
    },
    topHoldings: [
      { name: '엔비디아', ticker: 'NVDA', percentage: 15 },
      { name: '마이크로소프트', ticker: 'MSFT', percentage: 12 },
      { name: '코퍼트', ticker: 'CPRT', percentage: 8 }
    ]
  }
];

export const getGuruById = (id: string): Guru | undefined => {
  return gurus.find(guru => guru.id === id);
};

export const getGurusWithNewBuys = (): Guru[] => {
  return gurus.filter(guru => guru.changes.newBuys > 0);
};

export const getGurusWithChanges = (): Guru[] => {
  return gurus.filter(guru => 
    guru.changes.newBuys > 0 || 
    guru.changes.increased > 0 || 
    guru.changes.decreased > 0 || 
    guru.changes.sold > 0
  );
};