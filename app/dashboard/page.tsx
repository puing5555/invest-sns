'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';

// ============ DUMMY DATA ============
const dummyHoldings = [
  { name: '삼성전자', code: '005930', qty: 30, avgPrice: 68500, currentPrice: 74600, returnPct: 8.91 },
  { name: 'SK하이닉스', code: '000660', qty: 10, avgPrice: 175000, currentPrice: 192500, returnPct: 10.0 },
  { name: 'NVIDIA', code: 'NVDA', qty: 5, avgPrice: 700, currentPrice: 824.03, returnPct: 17.72 },
  { name: '카카오', code: '035720', qty: 20, avgPrice: 52000, currentPrice: 41300, returnPct: -20.58 },
];

const dummyWatchlist = [
  { name: '하이트진로', code: '000080', currentPrice: 21500, changePct: 2.1 },
  { name: 'CELH', code: 'CELH', currentPrice: 32.45, changePct: 0.5 },
  { name: '테슬라', code: 'TSLA', currentPrice: 267.89, changePct: -1.2 },
  { name: '한화에어로', code: '012450', currentPrice: 315000, changePct: 4.3 },
  { name: 'SOFI', code: 'SOFI', currentPrice: 12.34, changePct: 3.7 },
];

const dummyAlerts = [
  { time: '07:15', icon: '🤖', title: '삼성전자 AI 시그널', desc: '매수 시그널 3개 집중 — 반도체 업황 개선 기대감', type: 'signal' },
  { time: '06:50', icon: '📢', title: 'SK하이닉스 공시', desc: '2024년 4분기 실적 발표 — 영업이익 7.7조 원', type: 'disclosure' },
  { time: '06:30', icon: '📈', title: 'NVIDIA 목표가 상향', desc: '골드만삭스 목표가 $950 → $1,100 상향', type: 'signal' },
  { time: '06:00', icon: '⚠️', title: '카카오 손절 검토', desc: 'AI 판단: 손절 라인 도달, 포지션 재검토 필요', type: 'ai' },
];

const dummyNews = [
  { time: '08:00', source: '한경', title: '미국 반도체 수출규제 완화 시그널... 엔비디아 시간외 +3%', tag: '반도체' },
  { time: '07:30', source: '매경', title: '연준 파월 "인플레이션 둔화 확인"... 6월 금리인하 기대↑', tag: '매크로' },
  { time: '07:00', source: 'Bloomberg', title: '비트코인 $90K 돌파 임박, ETF 자금 유입 가속', tag: '크립토' },
  { time: '06:30', source: '로이터', title: '삼성전자-TSMC AI칩 수주 경쟁 격화', tag: '반도체' },
  { time: '06:00', source: '조선비즈', title: '2차전지 섹터 반등세... LG엔솔 외국인 3일 연속 순매수', tag: '2차전지' },
];

const dummyVideos = [
  { id: 1, channel: '이효석아카데미', time: '오늘 07:30', title: '반도체 사이클 2차 랠리 시작된다', category: '한국주식', summary: '필라델피아 반도체 지수가 3일 연속 상승하며 2차 랠리 신호를 보이고 있다. HBM 수요가 예상보다 강하고, SK하이닉스와 삼성전자의 실적 서프라이즈 가능성이 높다. 미국 AI 인프라 투자가 가속화되면서 메모리 수요는 하반기까지 이어질 전망.', stocks: ['SK하이닉스', '삼성전자', 'ASML'], hasSignal: true },
  { id: 2, channel: '월가아재', time: '오늘 06:00', title: '미국 고용지표 쇼크, 연준 피벗 앞당겨질까', category: '미국주식', summary: '비농업 고용이 컨센서스 대비 크게 하회하며 경기 둔화 우려가 부각됐다. 연준의 6월 금리인하 가능성이 70%까지 상승. 기술주 중심으로 반등 가능성 높으나, 경기침체 시그널과 구분해야 한다.', stocks: ['SPY', 'QQQ', 'TLT'], hasSignal: true },
  { id: 3, channel: '삼프로TV', time: '오늘 08:00', title: '[마감시황] 외국인 반도체 폭풍매수, 코스피 2600 돌파', category: '한국주식', summary: '외국인이 삼성전자와 SK하이닉스를 중심으로 4거래일 연속 순매수. 코스피가 2600선을 돌파하며 3개월 만에 최고치를 기록. 기관은 차익실현 매도세를 보이고 있으나 외국인 수급이 압도적.', stocks: ['삼성전자', 'SK하이닉스'], hasSignal: true },
  { id: 4, channel: '코인데스크코리아', time: '오늘 07:00', title: '비트코인 $85K 돌파, ETF 자금 유입 역대급', category: '크립토', summary: '비트코인 현물 ETF에 하루 $1.2B 유입되며 역대 최고 기록. 기관 투자자들의 본격적인 진입 신호로 해석. 이더리움도 $3,200 돌파하며 알트코인 랠리 기대감 상승.', stocks: ['BTC', 'ETH'], hasSignal: false },
  { id: 5, channel: '슈카월드', time: '오늘 09:00', title: '미국이 금리를 안 내리는 진짜 이유', category: '미국주식', summary: '미국 경제가 여전히 강한 고용과 소비를 보이고 있어 연준이 금리 인하를 서두르지 않는 배경을 분석. 인플레이션의 구조적 변화와 재정적자 문제까지 함께 다루며 하반기 전망을 제시.', stocks: [], hasSignal: false },
  { id: 6, channel: '소수몽키', time: '오늘 06:30', title: '테슬라 이번에는 진짜 바닥일까? FSD 12.5 분석', category: '미국주식', summary: '테슬라 FSD 12.5 업데이트가 완전자율주행에 한 걸음 더 다가갔다는 평가. 중국 시장 매출 반등과 사이버트럭 생산 정상화도 긍정적. 다만 밸류에이션 논란은 여전.', stocks: ['TSLA'], hasSignal: true },
  { id: 7, channel: 'GODofIT', time: '오늘 08:30', title: '엔비디아 실적 프리뷰: 이번에도 서프라이즈?', category: '미국주식', summary: '엔비디아 다음 주 실적 발표를 앞두고 주요 체크포인트 분석. 데이터센터 매출 YoY +200% 예상, H200/B100 전환 사이클, 중국 수출 규제 영향까지 종합 정리.', stocks: ['NVDA', 'AMD', 'AVGO'], hasSignal: true },
  { id: 8, channel: '세상학개론', time: '어제 22:00', title: '2024년에 반드시 사야 할 한국 배당주 TOP 5', category: '한국주식', summary: '고배당 + 성장성을 겸비한 한국 배당주 5개를 선정. 배당수익률 5% 이상이면서 실적 성장이 확인된 종목 위주로 분석. KT&G, 하나금융, SK텔레콤 등이 포함.', stocks: ['KT&G', '하나금융', 'SK텔레콤', '삼성화재', '맥쿼리인프라'], hasSignal: true },
  { id: 9, channel: '이효석아카데미', time: '어제 20:00', title: '비트코인 10만불 간다? 반감기 후 시나리오', category: '크립토', summary: '비트코인 반감기 이후 역사적 패턴을 분석하며 $100K 시나리오를 제시. 기관 ETF 자금 유입, 스테이블코인 시가총액 증가, 온체인 데이터 모두 긍정적 신호를 보이고 있다.', stocks: ['BTC'], hasSignal: false },
  { id: 10, channel: '리치고TV', time: '어제 19:00', title: '초보자가 절대 사면 안되는 ETF 3가지', category: '미국주식', summary: '레버리지 ETF, 인버스 ETF, 테마형 ETF의 위험성을 구체적 사례와 함께 설명. 장기 보유 시 괴리율 문제와 비용 구조를 분석하며 초보자에게 적합한 대안 ETF도 제시.', stocks: [], hasSignal: false },
];

// ============ STYLES ============
const colors = {
  bg: '#F8F9FA',
  card: '#FFFFFF',
  primary: '#1A1A2E',
  accent: '#2563EB',
  red: '#EF4444',
  blue: '#3B82F6',
  green: '#10B981',
  gray: '#6B7280',
  lightGray: '#E5E7EB',
};

const categoryColors: Record<string, { bg: string; text: string }> = {
  '한국주식': { bg: '#DBEAFE', text: '#1E40AF' },
  '미국주식': { bg: '#FEE2E2', text: '#991B1B' },
  '크립토':   { bg: '#FEF3C7', text: '#92400E' },
};

// ============ COMPONENTS ============
const TabBar = ({ active, setActive }: { active: string; setActive: (t: string) => void }) => {
  const tabs = [
    { id: 'now',    label: '지금' },
    { id: 'news',   label: '뉴스' },
    { id: 'live',   label: 'LIVE', dot: true },
    { id: 'market', label: '시장' },
  ];
  return (
    <div style={{ display: 'flex', gap: 0, borderBottom: `2px solid ${colors.lightGray}`, marginBottom: 24 }}>
      {tabs.map(t => (
        <button
          key={t.id}
          onClick={() => setActive(t.id)}
          style={{
            padding: '12px 24px', background: 'none', border: 'none',
            borderBottom: active === t.id ? `3px solid ${colors.accent}` : '3px solid transparent',
            color: active === t.id ? colors.accent : colors.gray,
            fontWeight: active === t.id ? 700 : 500, fontSize: 15, cursor: 'pointer',
            display: 'flex', alignItems: 'center', gap: 6,
            fontFamily: "'Pretendard', -apple-system, sans-serif", transition: 'all 0.2s',
          }}
        >
          {t.dot && <span style={{ width: 8, height: 8, borderRadius: '50%', background: colors.red, display: 'inline-block' }} />}
          {t.label}
        </button>
      ))}
    </div>
  );
};

const Card = ({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) => (
  <div style={{
    background: colors.card, borderRadius: 16, padding: '20px 24px', marginBottom: 16,
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)', ...style,
  }}>
    {children}
  </div>
);

const SectionHeader = ({ title, action }: { title: string; action?: string }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
    <span style={{ fontSize: 16, fontWeight: 700, color: colors.primary }}>{title}</span>
    {action && <span style={{ fontSize: 13, color: colors.accent, cursor: 'pointer' }}>{action}</span>}
  </div>
);

const FilterPill = ({ label, active, onClick, icon }: { label: string; active: boolean; onClick: () => void; icon?: string }) => (
  <button
    onClick={onClick}
    style={{
      padding: '8px 16px', borderRadius: 20,
      border: active ? 'none' : `1px solid ${colors.lightGray}`,
      background: active ? colors.accent : colors.card,
      color: active ? '#fff' : colors.gray,
      fontSize: 13, fontWeight: 600, cursor: 'pointer',
      display: 'flex', alignItems: 'center', gap: 4,
      fontFamily: "'Pretendard', -apple-system, sans-serif", transition: 'all 0.15s',
    }}
  >
    {icon && <span>{icon}</span>}
    {label}
  </button>
);

// ============ TAB: 지금 ============
// 순서: 오늘알림(없으면 숨김) → 보유종목(가로 카드) → 관심종목 → 시황
const NowTab = () => (
  <div>
    {/* 오늘 알림 — 없으면 숨김 */}
    {dummyAlerts.length > 0 && (
      <Card>
        <SectionHeader title="🔔 오늘 알림" action="전체 보기 →" />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          {dummyAlerts.map((a, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'flex-start', gap: 12,
              padding: '12px 0',
              borderBottom: i < dummyAlerts.length - 1 ? `1px solid ${colors.lightGray}` : 'none',
              cursor: 'pointer',
            }}>
              <span style={{ fontSize: 20 }}>{a.icon}</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 700, fontSize: 14, color: colors.primary }}>{a.title}</div>
                <div style={{ fontSize: 13, color: colors.gray, marginTop: 2 }}>{a.desc}</div>
              </div>
              <span style={{ fontSize: 12, color: colors.gray, whiteSpace: 'nowrap' }}>{a.time}</span>
            </div>
          ))}
        </div>
      </Card>
    )}

    {/* 보유종목 — 가로 스크롤 카드 (종목명 / 현재가 / 수익률%) */}
    <Card>
      <SectionHeader title="🧳 보유종목" action="전체보기 →" />
      <div style={{ display: 'flex', gap: 12, overflowX: 'auto', paddingBottom: 4 }}>
        {dummyHoldings.map((s, i) => (
          <div key={i} style={{
            minWidth: 130, padding: '14px 16px', borderRadius: 12,
            background: colors.bg, flexShrink: 0, textAlign: 'center',
            border: `1px solid ${colors.lightGray}`,
          }}>
            <div style={{ fontWeight: 700, fontSize: 14, color: colors.primary }}>{s.name}</div>
            <div style={{ fontSize: 12, color: colors.gray, marginTop: 2 }}>{s.code}</div>
            <div style={{ fontWeight: 700, fontSize: 15, color: colors.primary, marginTop: 8 }}>
              {typeof s.currentPrice === 'number' && s.currentPrice > 1000
                ? s.currentPrice.toLocaleString()
                : s.currentPrice}
            </div>
            <div style={{
              fontSize: 14, fontWeight: 700, marginTop: 4,
              color: s.returnPct >= 0 ? colors.red : colors.blue,
            }}>
              {s.returnPct >= 0 ? '+' : ''}{s.returnPct.toFixed(2)}%
            </div>
          </div>
        ))}
      </div>
    </Card>

    {/* 관심종목 — 가로 스크롤 카드 */}
    <Card>
      <SectionHeader title="⭐ 관심종목" action="전체보기 →" />
      <div style={{ display: 'flex', gap: 12, overflowX: 'auto', paddingBottom: 4 }}>
        {dummyWatchlist.map((s, i) => (
          <div key={i} style={{
            minWidth: 120, padding: '12px 16px', borderRadius: 12,
            background: colors.bg, textAlign: 'center', flexShrink: 0,
          }}>
            <div style={{ fontWeight: 600, fontSize: 13, color: colors.primary }}>{s.name}</div>
            <div style={{ fontSize: 12, color: colors.gray, marginTop: 2 }}>{s.code}</div>
            <div style={{
              fontSize: 14, fontWeight: 700, marginTop: 6,
              color: s.changePct >= 0 ? colors.red : colors.blue,
            }}>
              {s.changePct >= 0 ? '+' : ''}{s.changePct}%
            </div>
          </div>
        ))}
      </div>
    </Card>

    {/* 시황 */}
    <Card>
      <SectionHeader title="📊 시황" />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontWeight: 700, fontSize: 13, color: colors.gray, width: 28 }}>US</span>
          <span>S&P <b style={{ color: colors.red }}>5,782 +0.8%</b></span>
          <span>나스닥 <b style={{ color: colors.red }}>18,432 +1.2%</b></span>
          <span>다우 <b style={{ color: colors.red }}>42,890 +0.3%</b></span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontWeight: 700, fontSize: 13, color: colors.gray, width: 28 }}>KR</span>
          <span>코스피 <b style={{ color: colors.blue }}>2,578 -0.2%</b></span>
          <span>코스닥 <b style={{ color: colors.red }}>752 +0.4%</b></span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontWeight: 700, fontSize: 13, color: colors.gray, width: 28 }}>₿</span>
          <span>BTC <b style={{ color: colors.red }}>$85,420 +1.2%</b></span>
          <span>금 <b style={{ color: colors.red }}>$2,914 +0.3%</b></span>
          <span>원/달러 <b style={{ color: colors.red }}>1,455 +0.1%</b></span>
        </div>
      </div>
    </Card>
  </div>
);

// ============ TAB: 뉴스 — 공시 AI분석 삭제, 뉴스 헤드라인만 ============
const NewsTab = () => (
  <div>
    <Card>
      <SectionHeader title="📰 뉴스 헤드라인" />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
        {dummyNews.map((n, i) => (
          <div key={i} style={{
            display: 'flex', alignItems: 'center', gap: 12,
            padding: '12px 0',
            borderBottom: i < dummyNews.length - 1 ? `1px solid ${colors.lightGray}` : 'none',
            cursor: 'pointer',
          }}>
            <span style={{
              padding: '3px 8px', borderRadius: 4, fontSize: 11, fontWeight: 600,
              background: '#F3F4F6', color: '#6B7280', whiteSpace: 'nowrap',
            }}>{n.tag}</span>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 14, fontWeight: 500, color: colors.primary }}>{n.title}</div>
              <div style={{ fontSize: 12, color: colors.gray, marginTop: 2 }}>{n.source} · {n.time}</div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  </div>
);

// ============ TAB: LIVE — 카테고리: 전체/한국주식/미국주식/크립토 ============
const LiveTab = () => {
  const [filter, setFilter]     = useState('전체');
  const [catFilter, setCatFilter] = useState('전체');
  const [expanded, setExpanded]  = useState<Record<number, boolean>>({});

  const categories = ['전체', '한국주식', '미국주식', '크립토'];
  const myStocks = [
    ...dummyHoldings.map(h => h.name),
    ...dummyWatchlist.map(w => w.name),
  ];

  const filtered = dummyVideos.filter(v => {
    if (catFilter !== '전체' && v.category !== catFilter) return false;
    if (filter === '내 종목') return v.stocks.some(s => myStocks.includes(s));
    return true;
  });

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap' }}>
        <FilterPill label="내 종목" icon="⭐" active={filter === '내 종목'} onClick={() => setFilter(filter === '내 종목' ? '전체' : '내 종목')} />
        <FilterPill label="전체" active={filter === '전체' && catFilter === '전체'} onClick={() => { setFilter('전체'); setCatFilter('전체'); }} />
      </div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        {categories.map(c => (
          <FilterPill key={c} label={c} active={catFilter === c} onClick={() => setCatFilter(c)} />
        ))}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {filtered.map(v => {
          const isExpanded  = expanded[v.id];
          const catColor    = categoryColors[v.category] || { bg: '#F3F4F6', text: '#374151' };
          const hasMyStock  = v.stocks.some(s => myStocks.includes(s));

          return (
            <Card key={v.id} style={{
              border: hasMyStock ? `2px solid ${colors.accent}` : '1px solid #F3F4F6',
              background: hasMyStock ? '#F8FAFF' : colors.card,
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{
                    width: 36, height: 36, borderRadius: '50%', background: '#E5E7EB',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 14, fontWeight: 700, color: '#374151',
                  }}>
                    {v.channel[0]}
                  </div>
                  <span style={{ fontWeight: 700, fontSize: 14, color: colors.primary }}>{v.channel}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{
                    padding: '3px 8px', borderRadius: 6, fontSize: 11, fontWeight: 600,
                    background: catColor.bg, color: catColor.text,
                  }}>{v.category}</span>
                  <span style={{ fontSize: 12, color: colors.gray }}>{v.time}</span>
                </div>
              </div>

              <div style={{ fontWeight: 700, fontSize: 15, color: colors.primary, marginBottom: 8, lineHeight: 1.4 }}>
                {v.title}
              </div>

              <div style={{
                fontSize: 13, color: '#4B5563', lineHeight: 1.6, marginBottom: 10,
                overflow: 'hidden', maxHeight: isExpanded ? 'none' : 65,
              }}>
                {v.summary}
              </div>

              {v.summary.length > 100 && (
                <button
                  onClick={() => setExpanded(prev => ({ ...prev, [v.id]: !prev[v.id] }))}
                  style={{
                    background: 'none', border: 'none', color: colors.accent,
                    fontSize: 12, fontWeight: 600, cursor: 'pointer', padding: 0, marginBottom: 10,
                  }}
                >
                  {isExpanded ? '접기 ▲' : '더보기 ▼'}
                </button>
              )}

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {v.stocks.length > 0 && (
                    <>
                      <span style={{ fontSize: 12, color: colors.gray }}>📌</span>
                      {v.stocks.map((s, i) => (
                        <span key={i} style={{
                          padding: '2px 8px', borderRadius: 4, fontSize: 11, fontWeight: 600,
                          background: myStocks.includes(s) ? '#DBEAFE' : '#F3F4F6',
                          color: myStocks.includes(s) ? '#1E40AF' : '#6B7280',
                        }}>{s}</span>
                      ))}
                    </>
                  )}
                </div>
                <button style={{
                  padding: '6px 14px', borderRadius: 8, fontSize: 12, fontWeight: 600,
                  background: colors.red, color: '#fff', border: 'none', cursor: 'pointer',
                  display: 'flex', alignItems: 'center', gap: 4,
                }}>
                  🎬 영상 보기
                </button>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

// ============ TAB: 시장 ============
const MarketTab = () => (
  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
    <div style={{ fontSize: 48, marginBottom: 16 }}>📊</div>
    <div style={{ fontSize: 18, fontWeight: 700, color: colors.primary, marginBottom: 8 }}>시장 탭 준비 중</div>
    <div style={{ fontSize: 14, color: colors.gray, textAlign: 'center', lineHeight: 1.6 }}>
      Fear &amp; Greed 게이지 · 섹터별 등락<br />
      외국인/기관 수급 · 유튜버 전체 컨센서스<br />
      <span style={{ fontSize: 12, marginTop: 8, display: 'inline-block' }}>곧 출시됩니다</span>
    </div>
  </div>
);

// ============ MAIN ============
export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('now');

  useEffect(() => {
    if (!authLoading && !user) { router.push('/login'); }
  }, [user, authLoading, router]);

  if (authLoading || !user) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p style={{ color: colors.gray }}>로딩 중...</p>
      </div>
    );
  }

  return (
    <div style={{
      maxWidth: 800, margin: '0 auto', padding: '24px 16px',
      background: colors.bg, minHeight: '100vh',
      fontFamily: "'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif",
    }}>
      <div style={{ marginBottom: 8 }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, color: colors.primary, margin: 0 }}>📊 대시보드</h1>
        <p style={{ fontSize: 13, color: colors.gray, margin: '4px 0 0' }}>내 종목 현황</p>
      </div>

      <TabBar active={activeTab} setActive={setActiveTab} />

      {activeTab === 'now'    && <NowTab />}
      {activeTab === 'news'   && <NewsTab />}
      {activeTab === 'live'   && <LiveTab />}
      {activeTab === 'market' && <MarketTab />}
    </div>
  );
}
