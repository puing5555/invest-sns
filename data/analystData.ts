export interface AnalystReport {
  id: string;
  title: string;
  targetPrice: number;
  currentPrice: number;
  investmentOpinion: 'BUY' | 'SELL' | 'HOLD' | 'STRONG_BUY' | 'STRONG_SELL';
  previousTargetPrice?: number;
  upsidePotential: number;
  publishedAt: string;
  summary: string;
  keyPoints: string[];
}

export interface AnalystPerformance {
  stock: string;
  entryPrice: number;
  exitPrice?: number;
  returnRate: number;
  hitTarget: boolean;
  daysToTarget?: number;
  entryDate: string;
  exitDate?: string;
  status: '진행중' | '목표달성' | '손절' | '만료';
}

export interface Analyst {
  id: string;
  name: string;
  company: string; // 증권사명
  sector: string; // 전문 섹터
  accuracyRate: number; // 적중률 %
  totalReports: number;
  successfulPredictions: number;
  avgReturn: number; // 평균 수익률 %
  experienceYears: number;
  profileImage?: string;
  recentReports: AnalystReport[];
  recentPerformance: AnalystPerformance[];
}

// 샘플 애널리스트 데이터
export const analysts: Analyst[] = [
  {
    id: 'kim-sunwoo',
    name: '김선우',
    company: '한국투자증권',
    sector: '반도체',
    accuracyRate: 72.5,
    totalReports: 45,
    successfulPredictions: 33,
    avgReturn: 8.3,
    experienceYears: 7,
    profileImage: '/avatars/analyst-kim.jpg',
    recentReports: [
      {
        id: 'r1',
        title: 'SK하이닉스: HBM3E 매출 확대로 목표가 상향',
        targetPrice: 210000,
        currentPrice: 180000,
        investmentOpinion: 'BUY',
        previousTargetPrice: 190000,
        upsidePotential: 16.7,
        publishedAt: '2026-02-27T14:30:00Z',
        summary: 'HBM3E 매출 비중 30% 돌파로 수익성 크게 개선. 영업이익률 35%로 업계 최고 수준.',
        keyPoints: ['HBM3E 매출 비중 30% 돌파', '영업이익률 35% 달성', 'AI 수요 지속 증가']
      },
      {
        id: 'r2', 
        title: '삼성전자: 메모리 업사이클 진입, 매수 유지',
        targetPrice: 95000,
        currentPrice: 86000,
        investmentOpinion: 'BUY',
        upsidePotential: 10.5,
        publishedAt: '2026-02-26T09:15:00Z',
        summary: '메모리 가격 상승 사이클 진입. D램 가격 10% 상승으로 수익성 개선 전망.',
        keyPoints: ['메모리 가격 상승', 'D램 10% 가격 인상', '1Q 실적 턴어라운드']
      }
    ],
    recentPerformance: [
      {
        stock: 'SK하이닉스',
        entryPrice: 165000,
        exitPrice: 185000,
        returnRate: 12.1,
        hitTarget: true,
        daysToTarget: 23,
        entryDate: '2026-01-15',
        exitDate: '2026-02-07',
        status: '목표달성'
      },
      {
        stock: '삼성전자',
        entryPrice: 82000,
        returnRate: 4.9,
        hitTarget: false,
        entryDate: '2026-02-10',
        status: '진행중'
      }
    ]
  },
  {
    id: 'lee-mirae',
    name: '이미래',
    company: '삼성증권',
    sector: '바이오/헬스케어',
    accuracyRate: 68.2,
    totalReports: 38,
    successfulPredictions: 26,
    avgReturn: 6.7,
    experienceYears: 5,
    profileImage: '/avatars/analyst-lee.jpg',
    recentReports: [
      {
        id: 'r3',
        title: '셀트리온: 코로나 치료제 매출 안정화',
        targetPrice: 220000,
        currentPrice: 195000,
        investmentOpinion: 'BUY',
        upsidePotential: 12.8,
        publishedAt: '2026-02-26T16:45:00Z',
        summary: '코로나 치료제 레클리쿠맙 매출이 안정적 흐름. 바이오시밀러 사업도 견조.',
        keyPoints: ['레클리쿠맙 안정 매출', '바이오시밀러 성장', '신약 파이프라인 진전']
      }
    ],
    recentPerformance: [
      {
        stock: '셀트리온',
        entryPrice: 180000,
        exitPrice: 210000,
        returnRate: 16.7,
        hitTarget: true,
        daysToTarget: 42,
        entryDate: '2025-12-20',
        exitDate: '2026-01-31',
        status: '목표달성'
      }
    ]
  },
  {
    id: 'park-tech',
    name: '박테크',
    company: 'NH투자증권',
    sector: '테크/IT서비스',
    accuracyRate: 74.1,
    totalReports: 52,
    successfulPredictions: 39,
    avgReturn: 9.1,
    experienceYears: 9,
    profileImage: '/avatars/analyst-park.jpg',
    recentReports: [
      {
        id: 'r4',
        title: '네이버: AI 플랫폼 확장으로 성장 가속화',
        targetPrice: 280000,
        currentPrice: 245000,
        investmentOpinion: 'BUY',
        upsidePotential: 14.3,
        publishedAt: '2026-02-25T11:20:00Z',
        summary: 'HyperCLOVA X 상용화로 AI 매출 급증. 클라우드 사업 확장도 긍정적.',
        keyPoints: ['HyperCLOVA X 상용화', 'AI 매출 3배 증가', '클라우드 사업 확장']
      }
    ],
    recentPerformance: []
  },
  {
    id: 'choi-finance',
    name: '최금융',
    company: '대신증권',
    sector: '금융',
    accuracyRate: 69.8,
    totalReports: 41,
    successfulPredictions: 29,
    avgReturn: 7.2,
    experienceYears: 6,
    profileImage: '/avatars/analyst-choi.jpg',
    recentReports: [
      {
        id: 'r5',
        title: '신한금융지주: 금리 안정화로 NIM 개선',
        targetPrice: 58000,
        currentPrice: 52000,
        investmentOpinion: 'BUY',
        upsidePotential: 11.5,
        publishedAt: '2026-02-24T13:30:00Z',
        summary: '기준금리 안정화로 순이자마진(NIM) 개선. 대출 성장도 양호한 흐름.',
        keyPoints: ['NIM 개선 전망', '대출 성장 지속', '충당금 부담 완화']
      }
    ],
    recentPerformance: []
  },
  {
    id: 'jung-energy',
    name: '정에너지',
    company: 'KB증권',
    sector: '에너지/화학',
    accuracyRate: 71.3,
    totalReports: 33,
    successfulPredictions: 24,
    avgReturn: 8.8,
    experienceYears: 8,
    profileImage: '/avatars/analyst-jung.jpg',
    recentReports: [
      {
        id: 'r6',
        title: 'SK이노베이션: 배터리 분할 후 밸류업',
        targetPrice: 180000,
        currentPrice: 155000,
        investmentOpinion: 'BUY',
        upsidePotential: 16.1,
        publishedAt: '2026-02-23T10:45:00Z',
        summary: '배터리 사업 분할 후 각 사업부 가치 재평가. 석유화학 업황 개선도 긍정적.',
        keyPoints: ['배터리 분할 밸류업', '석유화학 마진 회복', 'ESG 투자 유치']
      }
    ],
    recentPerformance: []
  }
];

// 최신 리포트 (전체)
export const latestReports = analysts.flatMap(analyst => 
  analyst.recentReports.map(report => ({
    ...report,
    analystId: analyst.id,
    analystName: analyst.name,
    company: analyst.company,
    accuracyRate: analyst.accuracyRate
  }))
).sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime());

// 투자의견별 색상
export const opinionColors = {
  'STRONG_BUY': 'bg-red-600 text-white',
  'BUY': 'bg-blue-600 text-white',
  'HOLD': 'bg-gray-500 text-white',
  'SELL': 'bg-orange-600 text-white',
  'STRONG_SELL': 'bg-red-800 text-white'
};

// 투자의견 한글 변환
export const opinionLabels = {
  'STRONG_BUY': '적극매수',
  'BUY': '매수',
  'HOLD': '보유',
  'SELL': '매도',
  'STRONG_SELL': '적극매도'
};