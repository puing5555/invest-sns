// Trade-related interfaces and data

export interface TradeHelperData {
  stockName: string;
  stopLoss: number;
  takeProfit?: number;
  tp1?: number;
  tp2?: number;
  patternCount: number;
  weekRebound?: number;
  monthRebound?: number;
  moreUpProb?: number;
  avgMoreUp?: number;
  isNearTarget?: boolean;
}

export interface PatternData {
  category: string;
  count: number;
  weekRebound: number;
  biWeekRebound: number;
  monthRebound: number;
}

export interface AnalysisPanelData {
  stockName: string;
  mode: 'loss' | 'profit';
  currentPrice: number;
  buyPrice: number;
  lossAmount?: number;
  patterns: PatternData[];
  specialConditions?: string[];
  vote: {
    options: Array<{
      label: string;
      emoji: string;
      percent: number;
      color: string;
    }>;
    totalVotes: number;
  };
  moreUpProb?: number;
  avgMoreUp?: number;
  dropProb?: number;
  avgDrop?: number;
  scenarios?: string[];
}

export interface TradeReviewData {
  id: string;
  stockName: string;
  buyPrice: number;
  buyDate: string;
  sellPrice: number;
  sellDate: string;
  returnPercent: number;
  verdict: '좋은매매' | '아쉬운매매' | '나쁜매매';
  priceHistory: {
    oneWeek: number;
    twoWeek: number;
    oneMonth: number;
  };
}

// Trade helper data for each stock
export const tradeHelperData: { [key: string]: TradeHelperData } = {
  'HD한국조선해양': {
    stockName: 'HD한국조선해양',
    stopLoss: 184000,
    takeProfit: 210000,
    patternCount: 15,
    weekRebound: 47,
    monthRebound: 58
  },
  '아이빔테크놀로지': {
    stockName: '아이빔테크놀로지',
    stopLoss: 28500,
    tp1: 33000,
    tp2: 36000,
    patternCount: 23,
    moreUpProb: 38,
    avgMoreUp: 6.2,
    isNearTarget: true
  },
  '에코프로': {
    stockName: '에코프로',
    stopLoss: 230000,
    tp1: 275000,
    tp2: 300000,
    patternCount: 15
  },
  '삼성전자': {
    stockName: '삼성전자',
    stopLoss: 65000,
    tp1: 78000,
    tp2: 85000,
    patternCount: 18
  },
  'SK하이닉스': {
    stockName: 'SK하이닉스',
    stopLoss: 168000,
    tp1: 200000,
    tp2: 220000,
    patternCount: 21
  }
};

// Analysis panel data
export const analysisPanelData: { [key: string]: AnalysisPanelData } = {
  '에코프로': {
    stockName: '에코프로',
    mode: 'loss',
    currentPrice: 248000,
    buyPrice: 265000,
    lossAmount: -17000,
    patterns: [
      {
        category: '종목 동일 패턴',
        count: 15,
        weekRebound: 34,
        biWeekRebound: 56,
        monthRebound: 68
      },
      {
        category: '섹터 유사',
        count: 89,
        weekRebound: 42,
        biWeekRebound: 61,
        monthRebound: 73
      },
      {
        category: '전체 시장',
        count: 340,
        weekRebound: 38,
        biWeekRebound: 58,
        monthRebound: 71
      }
    ],
    specialConditions: ['🔴 지지선 이탈', '🟢 거래량 정상', '🟡 기관 관망'],
    vote: {
      options: [
        { label: '홀드', emoji: '💎', percent: 62, color: '#22c55e' },
        { label: '손절', emoji: '💸', percent: 28, color: '#ef4444' },
        { label: '물타기', emoji: '🔄', percent: 10, color: '#3b82f6' }
      ],
      totalVotes: 1247
    }
  },
  '아이빔테크놀로지': {
    stockName: '아이빔테크놀로지',
    mode: 'profit',
    currentPrice: 32400,
    buyPrice: 30000,
    moreUpProb: 38,
    avgMoreUp: 6.2,
    dropProb: 62,
    avgDrop: -8.4,
    scenarios: [
      'A: 공급계약 추가 발표 (+15%)',
      'B: 현재 추세 유지 (+5%)',
      'C: 실적 부진 우려 (-10%)'
    ],
    patterns: [],
    vote: {
      options: [
        { label: '전량익절', emoji: '💰', percent: 41, color: '#22c55e' },
        { label: '절반익절', emoji: '⚖️', percent: 35, color: '#f59e0b' },
        { label: '홀드', emoji: '💎', percent: 24, color: '#3b82f6' }
      ],
      totalVotes: 892
    }
  }
};

// Trade review data
export const tradeReviewData: TradeReviewData[] = [
  {
    id: '1',
    stockName: '에코프로',
    buyPrice: 248000,
    buyDate: '02/20',
    sellPrice: 278000,
    sellDate: '02/28',
    returnPercent: 12.1,
    verdict: '좋은매매',
    priceHistory: {
      oneWeek: 265000,
      twoWeek: 252000,
      oneMonth: 289000
    }
  },
  {
    id: '2',
    stockName: '카카오',
    buyPrice: 52000,
    buyDate: '02/05',
    sellPrice: 48500,
    sellDate: '02/15',
    returnPercent: -6.7,
    verdict: '아쉬운매매',
    priceHistory: {
      oneWeek: 46000,
      twoWeek: 49000,
      oneMonth: 51500
    }
  }
];