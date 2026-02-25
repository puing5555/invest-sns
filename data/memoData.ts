export interface MemoAttachment {
  type: '공시' | '애널리포트' | '인플루언서콜';
  label: string;
}

export interface MemoData {
  id: number;
  stock: string | null;
  title: string;
  content: string;
  tag: '매수근거' | '매도근거' | '관찰' | 'AI일지';
  tagIcon: string; // 📗📕📒🤖
  date: string;
  attachments: MemoAttachment[];
  isAI?: boolean;
}

export const memoData: MemoData[] = [
  {
    id: 1,
    stock: "에코프로",
    title: "25만 밑 분할매수 계획",
    content: "1차 매수: 25만 밑 30%, 2차 매수: 22만 밑 40%, 나머지 대기. 목표가 32만. 손절 20만 밑. 근거: 외국인 순매수 전환, 인플루언서 3명 동시 콜, 2차전지 바닥 시그널.",
    tag: "매수근거",
    tagIcon: "📗",
    date: "2025.02.18",
    attachments: [{ type: "공시", label: "에코프로 공급계약 체결 공시" }]
  },
  {
    id: 2,
    stock: "삼성전자",
    title: "주총 전 매수 전략",
    content: "주총 D-23. 밸류업 안건 나올 가능성. 7만 밑 추가매수 고려. 배당 +16% 확정. 임원 연속매수도 긍정적 시그널.",
    tag: "매수근거",
    tagIcon: "📗",
    date: "2025.02.20",
    attachments: [{ type: "애널리포트", label: "삼성전자 목표가 상향 리포트" }]
  },
  {
    id: 3,
    stock: "카카오",
    title: "손절 복기",
    content: "52,000에 매수 → 48,500 손절. 실적 쇼크 예상 못함. 다음엔 실적 발표 전 포지션 줄이기. 교훈: 실적 시즌에는 보수적으로.",
    tag: "매도근거",
    tagIcon: "📕",
    date: "2025.02.15",
    attachments: []
  },
  {
    id: 4,
    stock: "아이빔테크놀로지",
    title: "공급계약 공시 분석",
    content: "161억 공급계약. 매출대비 33%. 과거 유사 패턴 +8.2%. 시총 546억 소형주라 변동성 주의. 진입가 30,000 부근.",
    tag: "매수근거",
    tagIcon: "📗",
    date: "2025.02.25",
    attachments: [
      { type: "공시", label: "아이빔테크놀로지 공급계약 체결" },
      { type: "인플루언서콜", label: "한투맨 매수 콜" }
    ]
  },
  {
    id: 5,
    stock: null,
    title: "📅 2025.02.24 AI 투자일지",
    content: "오늘 포트폴리오 +1.2%. 에코프로 +3.2% 기여. 삼성전자 보합. 특이사항: 에코프로 외국인 순매수 전환, 아이빔테크 공시 발생. HD한국조선 해명공시 미확정 — 재공시 예정일 체크 필요.",
    tag: "AI일지",
    tagIcon: "🤖",
    date: "2025.02.24",
    attachments: [],
    isAI: true
  }
];