export interface Notification {
  id: string;
  type: '공시' | '인플루언서' | '임원매매' | '애널리스트' | '가격' | '수급' | 'AI시그널';
  icon: string;
  title: string;
  body: string;
  detail: string;
  time: string;
  read: boolean;
  link: string;
}

export interface NotificationSettings {
  a급공시: boolean;
  b급공시: boolean;
  인플루언서콜: boolean;
  애널리스트목표가: boolean;
  임원매매: boolean;
  가격알림: boolean;
  ai시그널: boolean;
  수급감지: boolean;
}

export const initialNotifications: Notification[] = [
  {
    id: '1',
    type: '공시',
    icon: '📋',
    title: 'A등급 공시',
    body: '아이빔테크놀로지 — 공급계약 체결 161억원',
    detail: '매출대비 33%, 과거 유사 패턴 +8.2%',
    time: '5분 전',
    read: false,
    link: '/disclosure'
  },
  {
    id: '2',
    type: '인플루언서',
    icon: '👤',
    title: '인플루언서 콜',
    body: '코린이아빠 → 에코프로 매수콜',
    detail: '25만 밑 분할매수 추천',
    time: '32분 전',
    read: false,
    link: '/influencer'
  },
  {
    id: '3',
    type: '임원매매',
    icon: '👔',
    title: '임원 매매',
    body: '삼성전자 부사장 김OO — 50,000주 매수 (35억)',
    detail: '3일 연속 매수 🔥',
    time: '1시간 전',
    read: false,
    link: '/watchlist'
  },
  {
    id: '4',
    type: '애널리스트',
    icon: '🎯',
    title: '목표가 변동',
    body: 'SK하이닉스 — 한투 김OO 목표가 180,000→210,000 상향',
    detail: '적중률 62% ★★★★',
    time: '2시간 전',
    read: true,
    link: '/stock/sk-hynix'
  },
  {
    id: '5',
    type: '인플루언서',
    icon: '👤',
    title: '인플루언서 콜',
    body: '주식하는의사 → SK하이닉스 매수콜',
    detail: 'HBM 수혜 본격화',
    time: '3시간 전',
    read: true,
    link: '/influencer'
  },
  {
    id: '6',
    type: '가격',
    icon: '📈',
    title: '가격 알림',
    body: '에코프로 248,000원 돌파 (+3.2%)',
    detail: '설정한 알림가 245,000원 도달',
    time: '3시간 전',
    read: true,
    link: '/watchlist'
  },
  {
    id: '7',
    type: '공시',
    icon: '📋',
    title: '공시',
    body: '토비스 — 현금배당 350원 결정',
    detail: 'B등급 | 전년대비 +16.7%',
    time: '5시간 전',
    read: true,
    link: '/disclosure'
  },
  {
    id: '8',
    type: '수급',
    icon: '🏦',
    title: '수급 알림',
    body: '에코프로 — 외국인 3일 연속 순매수',
    detail: '누적 순매수 +280억',
    time: '6시간 전',
    read: true,
    link: '/watchlist'
  },
  {
    id: '9',
    type: '애널리스트',
    icon: '🎯',
    title: '목표가 변동',
    body: '삼성전자 — 미래에셋 박OO 목표가 78,000→85,000 상향',
    detail: '',
    time: '어제',
    read: true,
    link: '/stock/samsung'
  },
  {
    id: '10',
    type: 'AI시그널',
    icon: '🔥',
    title: 'AI 시그널',
    body: '에코프로 시그널 스코어 87점 돌파 — AI 주목 종목 선정',
    detail: '4개 시그널 동시 발생',
    time: '어제',
    read: true,
    link: '/watchlist'
  }
];

export const initialNotificationSettings: NotificationSettings = {
  a급공시: true,
  b급공시: false,
  인플루언서콜: true,
  애널리스트목표가: true,
  임원매매: true,
  가격알림: true,
  ai시그널: true,
  수급감지: false
};