export interface NewsData {
  id: number;
  urgent?: boolean;
  title: string;
  source: string;
  time: string;
  aiAnalysis: string;
  relatedStocks: string[];
  sentiment: 'positive' | 'neutral' | 'negative';
  comments: number;
  saves: number;
}

export const newsData: NewsData[] = [
  {
    id: 1,
    urgent: true,
    title: "삼성전자, 파운드리 2나노 수율 40% 돌파 — 업계 최초",
    source: "한국경제",
    time: "32분 전",
    aiAnalysis: "삼성전자 +, 관련 장비주(한미반도체, 주성엔지니어링) +",
    relatedStocks: ["삼성전자", "한미반도체"],
    sentiment: 'positive',
    comments: 147,
    saves: 89
  },
  {
    id: 2,
    title: "미 연준 3월 금리 동결 시사 — 파월 의장 의회 증언",
    source: "연합뉴스",
    time: "1시간 전",
    aiAnalysis: "성장주 +, 채권 -, 원/달러 약보합 예상",
    relatedStocks: ["코스피", "코스닥", "원/달러"],
    sentiment: 'neutral',
    comments: 203,
    saves: 156
  },
  {
    id: 3,
    title: "에코프로, 북미 양극재 공장 증설 발표 — 2조원 규모",
    source: "매일경제",
    time: "2시간 전",
    aiAnalysis: "배터리 소재 대장주 모멘텀 강화, 2차전지 생태계 확장 기대",
    relatedStocks: ["에코프로", "에코프로비엠"],
    sentiment: 'positive',
    comments: 92,
    saves: 68
  },
  {
    id: 4,
    title: "카카오 4분기 실적 쇼크 — 영업이익 컨센 대비 -23%",
    source: "조선비즈",
    time: "3시간 전",
    aiAnalysis: "플랫폼 매출 둔화, 광고 수익 감소로 수익성 악화 우려",
    relatedStocks: ["카카오", "카카오뱅크"],
    sentiment: 'negative',
    comments: 284,
    saves: 45
  },
  {
    id: 5,
    title: "HD현대중공업, 카타르 LNG선 8척 수주 — 3.2조원",
    source: "서울경제",
    time: "4시간 전",
    aiAnalysis: "조선업 수주 호조 지속, 친환경 선박 시장 선점 효과",
    relatedStocks: ["HD한국조선해양", "HD현대중공업"],
    sentiment: 'positive',
    comments: 76,
    saves: 134
  },
  {
    id: 6,
    title: "외국인, 코스피 3일 연속 순매수 — 반도체·자동차 집중",
    source: "한국경제TV",
    time: "5시간 전",
    aiAnalysis: "외국인 자금 유입 지속, 기술주 중심 매수세 확산",
    relatedStocks: ["삼성전자", "SK하이닉스"],
    sentiment: 'positive',
    comments: 165,
    saves: 98
  },
  {
    id: 7,
    title: "중국 경기부양 기대감 — 희토류·철강 관련주 주목",
    source: "이데일리",
    time: "6시간 전",
    aiAnalysis: "중국 인프라 투자 확대 시 원자재 수혜 기대",
    relatedStocks: ["POSCO홀딩스", "세아제강"],
    sentiment: 'positive',
    comments: 54,
    saves: 72
  },
  {
    id: 8,
    title: "바이든 행정부, 반도체 보조금 추가 배정 — 삼성 미국법인 포함",
    source: "Bloomberg (번역)",
    time: "8시간 전",
    aiAnalysis: "미국 반도체 투자 인센티브 확대로 삼성 수혜 전망",
    relatedStocks: ["삼성전자"],
    sentiment: 'positive',
    comments: 189,
    saves: 112
  }
];