export interface Report {
  id: string;
  stockName: string;
  title: string;
  firm: string;
  analystName: string;
  date: string;
  targetPriceOld?: number;
  targetPriceNew: number;
  changeType: 'up' | 'down' | 'maintain' | 'new';
  recommendation: string;
  aiSummary: string;
  aiSummaryFull: string;
  analystAccuracy: number;
  starRating: number;
}

export interface Analyst {
  id: string;
  name: string;
  firm: string;
  sector: string;
  accuracy: number;
  successful: number;
  total: number;
  avgReturn: number;
  starRating: number;
  trustBadge: 'verified' | 'accumulating';
  recentReports: string[];
  avatar?: string;
}

export interface TargetPriceHistory {
  date: string;
  price: number;
  analyst: string;
  firm: string;
}

export const reports: Report[] = [
  {
    id: '1',
    stockName: 'SK하이닉스',
    title: 'HBM 수혜 본격화, 목표가 상향',
    firm: '한국투자',
    analystName: '김OO',
    date: '2025.02.25',
    targetPriceOld: 180000,
    targetPriceNew: 210000,
    changeType: 'up',
    recommendation: '매수유지',
    aiSummary: 'HBM3E 양산 본격화로 ASP 상승 기대. 2025 영업익 전년대비 +45% 전망. 목표가 PER 12배 적용.',
    aiSummaryFull: 'HBM3E 양산 본격화로 ASP 상승 기대. 2025 영업익 전년대비 +45% 전망. 목표가 PER 12배 적용. SK하이닉스는 AI 메모리 시장의 핵심 기업으로 HBM 점유율 확대가 지속될 것으로 예상. 삼성전자 대비 기술 우위 유지하며 가격 프리미엄 지속 전망.',
    analystAccuracy: 62,
    starRating: 4
  },
  {
    id: '2',
    stockName: '삼성전자',
    title: '파운드리 회복 + 메모리 업사이클',
    firm: '미래에셋',
    analystName: '박OO',
    date: '2025.02.24',
    targetPriceOld: 78000,
    targetPriceNew: 85000,
    changeType: 'up',
    recommendation: '매수',
    aiSummary: '2나노 수율 개선으로 파운드리 흑자전환 기대. DRAM 가격 반등 수혜.',
    aiSummaryFull: '2나노 수율 개선으로 파운드리 흑자전환 기대. DRAM 가격 반등 수혜. 파운드리 부문의 수율 개선으로 2025년 흑자전환 가능할 것으로 예상. 메모리 부문도 재고 정상화 완료로 가격 상승 사이클 진입. AI 반도체 수요 증가도 긍정적 요인.',
    analystAccuracy: 58,
    starRating: 3
  },
  {
    id: '3',
    stockName: 'HD한국조선해양',
    title: '수주 모멘텀 지속, 조선 슈퍼사이클',
    firm: 'NH투자',
    analystName: '이OO',
    date: '2025.02.23',
    targetPriceOld: 170000,
    targetPriceNew: 195000,
    changeType: 'up',
    recommendation: '매수',
    aiSummary: '카타르 LNG선 추가 수주 기대. 2025 수주잔고 역대 최고치 전망.',
    aiSummaryFull: '카타르 LNG선 추가 수주 기대. 2025 수주잔고 역대 최고치 전망. 글로벌 LNG 수요 증가로 LNG선 신규 수주가 지속될 것으로 예상. 조선업계 슈퍼사이클이 본격화되면서 선가 상승도 동반. ESG 규제 강화로 친환경선박 수요도 증가 전망.',
    analystAccuracy: 71,
    starRating: 5
  },
  {
    id: '4',
    stockName: '에코프로',
    title: '2차전지 바닥 확인, 반등 시작',
    firm: '키움',
    analystName: '최OO',
    date: '2025.02.22',
    targetPriceOld: 280000,
    targetPriceNew: 310000,
    changeType: 'up',
    recommendation: '매수',
    aiSummary: '북미 양극재 공장 가동률 상승. 재고 정상화 완료. 하반기 턴어라운드.',
    aiSummaryFull: '북미 양극재 공장 가동률 상승. 재고 정상화 완료. 하반기 턴어라운드. 2차전지 업계의 재고 조정이 완료되면서 수요 회복 신호가 나타나고 있음. 북미 IRA 수혜로 현지 공장 가동률 상승. 중국 업체 대비 기술 경쟁력 우위 유지.',
    analystAccuracy: 55,
    starRating: 3
  },
  {
    id: '5',
    stockName: '카카오',
    title: '실적 부진 지속, 목표가 하향',
    firm: '삼성증권',
    analystName: '정OO',
    date: '2025.02.21',
    targetPriceOld: 65000,
    targetPriceNew: 52000,
    changeType: 'down',
    recommendation: '중립',
    aiSummary: '광고 매출 회복 지연. AI 투자비용 증가로 수익성 악화.',
    aiSummaryFull: '광고 매출 회복 지연. AI 투자비용 증가로 수익성 악화. 디지털 광고 시장 경쟁 심화로 매출 성장 둔화. AI 기술 투자 확대로 단기 수익성 압박. 하지만 장기적으로는 AI 기반 신사업 포트폴리오 확장 기대. 카카오페이 분할 상장도 긍정적 요인.',
    analystAccuracy: 64,
    starRating: 4
  },
  {
    id: '6',
    stockName: '한화에어로스페이스',
    title: '방산 수출 확대, 중장기 성장',
    firm: '대신',
    analystName: '윤OO',
    date: '2025.02.20',
    targetPriceNew: 310000,
    changeType: 'new',
    recommendation: '매수',
    aiSummary: '폴란드 추가 수주 가시화. K-방산 글로벌 점유율 확대.',
    aiSummaryFull: '폴란드 추가 수주 가시화. K-방산 글로벌 점유율 확대. 우크라이나 전쟁으로 글로벌 방산 수요 급증. 한국 방산 기업의 가성비 우위로 수출 확대 지속. 차세대 전투기 사업 참여로 장기 성장동력 확보. ESG 이슈는 있으나 국가 안보 차원에서 투자 필요성 인정.',
    analystAccuracy: 48,
    starRating: 2
  }
];

export const analysts: Analyst[] = [
  {
    id: '1',
    name: '이OO',
    firm: 'NH투자',
    sector: '조선/해운',
    accuracy: 71,
    successful: 25,
    total: 35,
    avgReturn: 16.8,
    starRating: 5,
    trustBadge: 'verified',
    recentReports: ['3', '1']
  },
  {
    id: '2',
    name: '김OO',
    firm: '한국투자',
    sector: '반도체',
    accuracy: 62,
    successful: 37,
    total: 60,
    avgReturn: 14.2,
    starRating: 4,
    trustBadge: 'verified',
    recentReports: ['1', '2']
  },
  {
    id: '3',
    name: '정OO',
    firm: '삼성증권',
    sector: '인터넷/플랫폼',
    accuracy: 64,
    successful: 28,
    total: 44,
    avgReturn: 11.5,
    starRating: 4,
    trustBadge: 'verified',
    recentReports: ['5']
  },
  {
    id: '4',
    name: '최OO',
    firm: '키움',
    sector: '2차전지',
    accuracy: 55,
    successful: 22,
    total: 40,
    avgReturn: 8.3,
    starRating: 3,
    trustBadge: 'verified',
    recentReports: ['4']
  },
  {
    id: '5',
    name: '윤OO',
    firm: '대신',
    sector: '방산/항공',
    accuracy: 48,
    successful: 8,
    total: 17,
    avgReturn: 6.1,
    starRating: 2,
    trustBadge: 'accumulating',
    recentReports: ['6']
  }
];

export const targetPriceHistory: TargetPriceHistory[] = [
  { date: '2025.02.25', price: 210000, analyst: '김OO', firm: '한국투자' },
  { date: '2025.01.15', price: 180000, analyst: '김OO', firm: '한국투자' },
  { date: '2024.12.10', price: 165000, analyst: '박XX', firm: '미래에셋' },
  { date: '2024.11.20', price: 155000, analyst: '이YY', firm: 'KB증권' },
  { date: '2024.10.25', price: 150000, analyst: '김OO', firm: '한국투자' }
];