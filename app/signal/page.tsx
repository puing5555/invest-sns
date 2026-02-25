'use client';

import { useState } from 'react';
import Link from 'next/link';
import SignalSummary from '../../components/SignalSummary';
import DisclosureCard, { DisclosureData } from '../../components/DisclosureCard';
import InfluencerCallCard, { InfluencerCallData } from '../../components/InfluencerCallCard';
import AnalystCard, { AnalystData } from '../../components/AnalystCard';
import AISignalCard, { AISignalData } from '../../components/AISignalCard';

const disclosures: DisclosureData[] = [
  { company: '아이빔테크놀로지', marketCap: '983억', title: '공급계약 체결 (계약금액 145억원)', ai: '매출대비 14.77%, 유사 D+3 +8.2%', time: '09:32', bullPercent: 78 },
  { company: '와이엠씨', marketCap: '1,337억', title: '자사주 500,000주 소각 결정', ai: '시총대비 3.75%, 소형주 대규모', time: '10:05', bullPercent: 92 },
  { company: '세아제강지주', marketCap: '4,200억', title: '기업가치 제고 계획 예고', ai: 'PBR 0.38, 예고→확정 36%', time: '10:30', bullPercent: 85 },
];

const influencerCalls: InfluencerCallData[] = [
  { name: '코린이아빠', initial: '코', hitRate: 72, stock: '에코프로', action: '매수', returnRate: '+4.2% (D+3)' },
  { name: '박두환', initial: '박', hitRate: 68, stock: '비트코인', action: '매수', returnRate: '+12.5% (D+3)' },
  { name: '이효석', initial: '이', hitRate: 65, stock: 'NVIDIA', action: '매수', returnRate: '-2.1% (D+3)' },
  { name: '주식쟁이김과장', initial: '김', hitRate: 71, stock: '삼성전자', action: '매수', returnRate: '+1.8% (D+3)' },
];

const analysts: AnalystData[] = [
  { stock: '삼성전자', firm: '한국투자', analyst: '김OO', prevTarget: '85,000', newTarget: '92,000', direction: 'up', gap: '+18.2%' },
  { stock: 'SK하이닉스', firm: '미래에셋', analyst: '박OO', prevTarget: '200,000', newTarget: '220,000', direction: 'up', gap: '+12.5%' },
  { stock: '에코프로', firm: 'NH투자', analyst: '이OO', prevTarget: '350,000', newTarget: '310,000', direction: 'down', gap: '+8.7%' },
  { stock: '현대차', firm: '삼성증권', analyst: '최OO', prevTarget: '280,000', newTarget: '300,000', direction: 'up', gap: '+15.1%' },
];

const aiSignals: AISignalData[] = [
  { stock: '아이빔테크놀로지', score: 87, summary: '공급계약+외국인순매수+인플루언서콜', tags: ['공시', '수급', '인플루언서'] },
  { stock: '삼성전자', score: 74, summary: '애널 4곳 목표가 상향+기관 순매수 전환', tags: ['애널', '수급'] },
];

const TABS = ['오늘의 시그널', '주간 TOP'] as const;

function SectionHeader({ title, href }: { title: string; href: string }) {
  return (
    <div className="flex items-center justify-between mb-3">
      <h3 className="font-bold text-[15px] text-gray-900">{title}</h3>
      <Link href={href} className="text-xs text-[#00d4aa] hover:underline">
        전체보기 &gt;
      </Link>
    </div>
  );
}

export default function SignalPage() {
  const [activeTab, setActiveTab] = useState<string>('오늘의 시그널');

  return (
    <div className="bg-white min-h-screen">
      {/* Tabs */}
      <div className="flex border-b border-[#eff3f4] sticky top-0 bg-white/80 backdrop-blur-md z-10">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className="flex-1 py-3.5 text-[15px] font-medium text-gray-500 hover:bg-gray-50 transition-colors relative"
          >
            <span className={activeTab === tab ? 'font-bold text-gray-900' : ''}>{tab}</span>
            {activeTab === tab && (
              <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-16 h-1 rounded-full bg-[#00d4aa]" />
            )}
          </button>
        ))}
      </div>

      {activeTab === '오늘의 시그널' ? (
        <div className="p-4 space-y-4">
          {/* 섹션1: 요약 */}
          <SignalSummary />

          {/* 섹션2: A등급 공시 */}
          <section>
            <SectionHeader title="🔴 A등급 공시" href="/disclosure" />
            <div className="space-y-2">
              {disclosures.map((d, i) => (
                <DisclosureCard key={i} d={d} />
              ))}
            </div>
          </section>

          {/* 섹션3: 인플루언서 콜 */}
          <section>
            <SectionHeader title="👤 인플루언서 콜" href="/influencer" />
            <div className="flex gap-3 overflow-x-auto pb-2">
              {influencerCalls.map((d, i) => (
                <InfluencerCallCard key={i} d={d} />
              ))}
            </div>
          </section>

          {/* 섹션4: 애널리스트 목표가 */}
          <section>
            <SectionHeader title="🎯 애널리스트 목표가" href="/signal" />
            <div className="bg-white border border-[#eff3f4] rounded-lg px-3">
              {analysts.map((d, i) => (
                <AnalystCard key={i} d={d} />
              ))}
            </div>
          </section>

          {/* 섹션5: AI 주목 */}
          <section>
            <SectionHeader title="🤖 AI 주목" href="/signal" />
            <div className="grid grid-cols-2 gap-3">
              {aiSignals.map((d, i) => (
                <AISignalCard key={i} d={d} />
              ))}
            </div>
          </section>
        </div>
      ) : (
        <div className="flex items-center justify-center h-60 text-gray-400 text-sm">
          준비중
        </div>
      )}
    </div>
  );
}
