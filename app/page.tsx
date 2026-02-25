'use client';

import Link from 'next/link';
import SignalSummaryCards from '../components/SignalSummaryCards';
import SignalScoreList from '../components/SignalScoreList';
import InsiderTradeCard from '../components/InsiderTradeCard';
import AnalystTargetItem, { AnalystTargetData } from '../components/AnalystTargetItem';

const analystTargets: AnalystTargetData[] = [
  { stock: 'SK하이닉스', firm: '한국투자', analyst: '김OO', prev: '180,000', next: '210,000', direction: 'up', accuracy: 62 },
  { stock: '삼성전자', firm: '미래에셋', analyst: '박OO', prev: '78,000', next: '85,000', direction: 'up', accuracy: 58 },
  { stock: 'HD한국조선', firm: 'NH투자', analyst: '이OO', prev: '170,000', next: '195,000', direction: 'up', accuracy: 71 },
];

const influencerCalls = [
  { name: '코린이아빠', initial: '코', stock: '에코프로', hitRate: 68, comment: '25만 밑에서 분할매수 추천' },
  { name: '주식하는의사', initial: '주', stock: 'SK하이닉스', hitRate: 72, comment: 'HBM 수혜 본격화, 목표 20만' },
  { name: '텔레그램큰손', initial: '텔', stock: '아이빔테크', hitRate: 58, comment: '공급계약 공시 나왔다, 단기 급등 예상' },
];

const disclosures = [
  { company: '아이빔테크놀로지', marketCap: '983억', title: '공급계약 체결 (계약금액 161억원)', ai: '매출대비 14.77%, 유사 47건 D+3 +8.2%', time: '09:32' },
  { company: '씨케이솔루션', marketCap: '1,520억', title: '자사주 300,000주 소각 결정', ai: '시총대비 2.8%, 소형주 소각 D+5 +5.1%', time: '10:15' },
];

function SectionTitle({ title, subtitle, href }: { title: string; subtitle?: string; href?: string }) {
  return (
    <div className="flex items-center justify-between mb-3">
      <div>
        <h2 className="font-bold text-[15px] text-gray-900">{title}</h2>
        {subtitle && <p className="text-xs text-gray-400 mt-0.5">{subtitle}</p>}
      </div>
      {href && (
        <Link href={href} className="text-xs text-[#00d4aa] hover:underline">전체보기 &gt;</Link>
      )}
    </div>
  );
}

export default function SignalHomePage() {
  const today = new Date();
  const days = ['일', '월', '화', '수', '목', '금', '토'];
  const dateStr = `${today.getFullYear()}.${String(today.getMonth() + 1).padStart(2, '0')}.${String(today.getDate()).padStart(2, '0')} ${days[today.getDay()]}`;

  return (
    <div className="bg-white min-h-screen">
      {/* Sticky header */}
      <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-[#eff3f4] px-4 py-3 flex items-center justify-between">
        <div>
          <h1 className="font-bold text-[15px] text-gray-900">📡 오늘의 시그널</h1>
          <p className="text-xs text-gray-400">{dateStr}</p>
        </div>
        <button className="text-gray-400 hover:text-gray-600 text-lg transition-colors">🔄</button>
      </div>

      <div className="p-4 space-y-6">
        {/* 섹션1: 요약 카드 */}
        <section>
          <SignalSummaryCards />
        </section>

        {/* 섹션2: 시그널 스코어 TOP */}
        <section>
          <SectionTitle
            title="🔥 오늘의 시그널 스코어 TOP"
            subtitle="여러 시그널이 겹치는 종목일수록 점수가 높아요"
          />
          <SignalScoreList />
        </section>

        {/* 섹션3: A등급 공시 */}
        <section>
          <SectionTitle title="📋 오늘의 A등급 공시" href="/disclosure" />
          <div className="space-y-2">
            {disclosures.map((d, i) => (
              <div key={i} className="bg-white border border-[#eff3f4] rounded-xl p-4 hover:bg-gray-50 transition-colors cursor-pointer">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] font-bold bg-[#ff4444] text-white px-2 py-0.5 rounded-full">A등급</span>
                  <span className="font-bold text-sm text-gray-900">{d.company}</span>
                  <span className="text-xs text-gray-400">{d.marketCap}</span>
                  <span className="text-xs text-gray-400 ml-auto">{d.time}</span>
                </div>
                <p className="text-sm text-gray-700 mb-1">{d.title}</p>
                <p className="text-xs text-[#00d4aa]">🤖 {d.ai}</p>
                <Link href="/disclosure" className="text-xs text-[#00d4aa] hover:underline mt-2 inline-block">상세보기 →</Link>
              </div>
            ))}
          </div>
        </section>

        {/* 섹션4: 인플루언서 핫콜 */}
        <section>
          <SectionTitle title="👤 인플루언서 오늘의 콜" href="/influencer" />
          <div className="flex gap-3 overflow-x-auto pb-2">
            {influencerCalls.map((c, i) => (
              <div key={i} className="bg-white border border-[#eff3f4] rounded-xl p-4 min-w-[220px] flex-shrink-0 hover:bg-gray-50 transition-colors cursor-pointer">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-8 h-8 rounded-full bg-[#1a1a2e] flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                    {c.initial}
                  </div>
                  <span className="font-bold text-sm text-gray-900">{c.name}</span>
                  <span className="text-[10px] bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded-full font-medium ml-auto">적중 {c.hitRate}%</span>
                </div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-bold text-sm text-gray-900">{c.stock}</span>
                  <span className="text-[10px] font-bold bg-[#dcfce7] text-[#16a34a] px-2 py-0.5 rounded-full">매수</span>
                </div>
                <p className="text-xs text-gray-500">&ldquo;{c.comment}&rdquo;</p>
              </div>
            ))}
          </div>
        </section>

        {/* 섹션5: 임원 매매 */}
        <section>
          <SectionTitle title="👔 임원 매매 감지" />
          <InsiderTradeCard />
        </section>

        {/* 섹션6: 애널리스트 목표가 */}
        <section>
          <SectionTitle title="🎯 목표가 변동" />
          <div className="bg-white border border-[#eff3f4] rounded-xl px-3">
            {analystTargets.map((d, i) => (
              <AnalystTargetItem key={i} d={d} />
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
