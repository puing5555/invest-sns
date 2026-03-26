'use client';

import { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import disclosuresData from '@/data/disclosures.json';

// ── 타입 ──
interface Disclosure {
  stock_code: string;
  corp_name: string;
  report_nm: string;
  rcept_no: string;
  rcept_dt: string;
  pblntf_ty: string;
  rm: string;
  detail_summary?: string | null;
  ai_summary?: string | null;
  ai_analysis?: string | null;
  sentiment?: string | null;
}

// ── 유틸리티 ──
const NOISE_RE = /최대주주등소유주식변동|기타경영사항\(자율공시\)|주주총회소집|정기주주총회결과|주주총회소집결의|주주총회소집공고/;

function isKeyDisclosure(d: Disclosure): boolean {
  const s = d.sentiment;
  return (s === '호재' || s === '악재' || s === '확인필요') && !NOISE_RE.test(d.report_nm);
}

function classifyType(nm: string): { label: string; color: string } {
  if (/자기주식|자사주/.test(nm)) return { label: '자사주', color: 'bg-blue-100 text-blue-700' };
  if (/실적|매출액또는손익|감사보고서/.test(nm)) return { label: '실적', color: 'bg-orange-100 text-orange-700' };
  if (/증권신고|유상증자|전환사채|신주인수권|합병|분할|감자/.test(nm)) return { label: '증자/CB', color: 'bg-red-100 text-red-700' };
  if (/대량보유|최대주주|소유주식변동/.test(nm)) return { label: '지분', color: 'bg-purple-100 text-purple-700' };
  if (/주주총회|배당/.test(nm)) return { label: '주총/배당', color: 'bg-green-100 text-green-700' };
  if (/기업가치제고/.test(nm)) return { label: '밸류업', color: 'bg-teal-100 text-teal-700' };
  if (/공정공시/.test(nm)) return { label: '공정공시', color: 'bg-yellow-100 text-yellow-700' };
  return { label: '기타', color: 'bg-gray-100 text-gray-600' };
}

function sentimentBadge(s: string | null | undefined): { text: string; color: string } | null {
  if (s === '호재') return { text: '호재', color: 'bg-red-50 text-red-600' };
  if (s === '악재') return { text: '악재', color: 'bg-blue-50 text-blue-600' };
  if (s === '확인필요') return { text: '확인', color: 'bg-amber-50 text-amber-600' };
  return null;
}

function formatDate(dt: string): string {
  if (dt.length !== 8) return dt;
  return `${dt.slice(0, 4)}.${dt.slice(4, 6)}.${dt.slice(6)}`;
}

function shortDate(dt: string): string {
  if (dt.length !== 8) return dt;
  return `${parseInt(dt.slice(4, 6))}/${parseInt(dt.slice(6))}`;
}

function toYmd(d: Date): string {
  return `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`;
}

type PeriodTab = 'today' | 'week' | 'month' | 'search';
type TypeFilter = '전체' | '자사주' | '실적' | '증자/CB' | '지분';

const PERIOD_TABS: { id: PeriodTab; label: string }[] = [
  { id: 'today', label: '오늘' },
  { id: 'week', label: '이번 주' },
  { id: 'month', label: '이번 달' },
  { id: 'search', label: '공시검색' },
];

const TYPE_MATCHERS: { label: TypeFilter; match: (d: Disclosure) => boolean; icon: string; cardColor: string }[] = [
  { label: '자사주', match: (d) => /자기주식|자사주/.test(d.report_nm), icon: '🔵', cardColor: 'bg-blue-50 border-blue-200' },
  { label: '실적', match: (d) => /실적|매출액또는손익|감사보고서|사업보고서|분기보고서|반기보고서/.test(d.report_nm), icon: '📊', cardColor: 'bg-orange-50 border-orange-200' },
  { label: '증자/CB', match: (d) => /증권신고|유상증자|전환사채|신주인수권|합병|분할|감자/.test(d.report_nm), icon: '💰', cardColor: 'bg-red-50 border-red-200' },
  { label: '지분', match: (d) => /대량보유|최대주주|소유주식변동/.test(d.report_nm), icon: '👤', cardColor: 'bg-purple-50 border-purple-200' },
];

// ── 날짜별 그룹핑 ──
function groupByDate(items: Disclosure[]): { date: string; items: Disclosure[] }[] {
  const groups: { date: string; items: Disclosure[] }[] = [];
  for (const d of items) {
    const last = groups[groups.length - 1];
    if (last && last.date === d.rcept_dt) {
      last.items.push(d);
    } else {
      groups.push({ date: d.rcept_dt, items: [d] });
    }
  }
  return groups;
}

// ── 메인 컴포넌트 ──
export default function DisclosurePage() {
  const router = useRouter();
  const [periodTab, setPeriodTab] = useState<PeriodTab>('today');
  const [typeFilter, setTypeFilter] = useState<TypeFilter>('전체');
  const [searchQuery, setSearchQuery] = useState('');

  const allDisclosures = useMemo(() => {
    const items = (disclosuresData as { disclosures: Disclosure[] }).disclosures;
    return [...items].sort((a, b) => b.rcept_dt.localeCompare(a.rcept_dt));
  }, []);

  const today = useMemo(() => toYmd(new Date()), []);
  const weekAgo = useMemo(() => toYmd(new Date(Date.now() - 7 * 86400000)), []);
  const monthAgo = useMemo(() => toYmd(new Date(Date.now() - 30 * 86400000)), []);

  const allKey = useMemo(() => allDisclosures.filter(isKeyDisclosure), [allDisclosures]);

  // 기간별 범위 시작일
  const periodStart = periodTab === 'today' ? today : periodTab === 'week' ? weekAgo : monthAgo;

  // ── 오늘 탭: fallback 로직 ──
  const { todayItems, todayLabel } = useMemo(() => {
    const items = allKey.filter((d) => d.rcept_dt === today);
    if (items.length > 0) return { todayItems: items, todayLabel: '오늘' };
    const latestDate = allKey[0]?.rcept_dt;
    if (!latestDate) return { todayItems: [], todayLabel: '' };
    return {
      todayItems: allKey.filter((d) => d.rcept_dt === latestDate),
      todayLabel: `${formatDate(latestDate)} 기준`,
    };
  }, [allKey, today]);

  // ── 기간별 주요 공시 (week/month) ──
  const periodItems = useMemo(() => {
    if (periodTab === 'today' || periodTab === 'search') return [];
    return allKey.filter((d) => d.rcept_dt >= periodStart && d.rcept_dt <= today);
  }, [allKey, periodTab, periodStart, today]);

  // ── 유형별 건수: 해당 기간 전체 공시 기준 ──
  const periodAllForCounts = useMemo(() => {
    if (periodTab === 'search') return [];
    const start = periodTab === 'today' ? (todayItems[0]?.rcept_dt || today) : periodStart;
    const end = periodTab === 'today' ? start : today;
    return allDisclosures.filter((d) => d.rcept_dt >= start && d.rcept_dt <= end);
  }, [allDisclosures, periodTab, periodStart, today, todayItems]);

  const typeCounts = useMemo(
    () => TYPE_MATCHERS.map((t) => ({ ...t, count: periodAllForCounts.filter(t.match).length })),
    [periodAllForCounts],
  );

  // ── 유형 필터 적용 ──
  const applyTypeFilter = (items: Disclosure[]): Disclosure[] => {
    if (typeFilter === '전체') return items;
    const matcher = TYPE_MATCHERS.find((t) => t.label === typeFilter)?.match;
    return matcher ? items.filter(matcher) : items;
  };

  // ── 공시검색: 전체 5,307건 검색 ──
  const searchResults = useMemo(() => {
    if (periodTab !== 'search') return [];
    let items = allDisclosures;
    // 유형 필터
    if (typeFilter !== '전체') {
      const matcher = TYPE_MATCHERS.find((t) => t.label === typeFilter)?.match;
      if (matcher) items = items.filter(matcher);
    }
    // 키워드 검색
    if (searchQuery.trim()) {
      const q = searchQuery.trim().toLowerCase();
      items = items.filter(
        (d) => d.corp_name?.toLowerCase().includes(q) || d.report_nm?.toLowerCase().includes(q),
      );
    }
    return items.slice(0, 200);
  }, [allDisclosures, periodTab, typeFilter, searchQuery]);

  // ── 표시할 그룹 ──
  const displayGroups = useMemo(() => {
    if (periodTab === 'today') return groupByDate(applyTypeFilter(todayItems));
    if (periodTab === 'search') return groupByDate(searchResults);
    return groupByDate(applyTypeFilter(periodItems));
  }, [periodTab, todayItems, periodItems, searchResults, typeFilter]);

  const totalCount = useMemo(() => {
    return displayGroups.reduce((sum, g) => sum + g.items.length, 0);
  }, [displayGroups]);

  const handleClick = (d: Disclosure) => {
    router.push(`/stock/${d.stock_code}?tab=disclosure`);
  };

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* 헤더 */}
      <div className="bg-white border-b border-[#e8e8e8]">
        <div className="max-w-4xl mx-auto px-4 pt-4 pb-0">
          <h1 className="text-xl font-bold text-[#191f28]">📋 공시</h1>
          <p className="text-sm text-[#8b95a1] mt-1">DART 기반 주요 공시 요약 · {allDisclosures.length.toLocaleString()}건</p>

          {/* 기간 탭 */}
          <div className="flex gap-0 mt-4 -mb-px">
            {PERIOD_TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => { setPeriodTab(tab.id); setTypeFilter('전체'); }}
                className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
                  periodTab === tab.id
                    ? 'border-[#3182f6] text-[#3182f6]'
                    : 'border-transparent text-[#8b95a1] hover:text-[#4e5968]'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-4 space-y-4">
        {/* 공시검색 탭: 검색바 + 유형 필터 */}
        {periodTab === 'search' ? (
          <div className="space-y-3">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="종목명 또는 키워드 검색..."
              className="w-full px-4 py-2.5 bg-white border border-[#e8e8e8] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#3182f6] focus:border-transparent"
            />
            <div className="flex gap-2 overflow-x-auto pb-1">
              {['전체' as TypeFilter, ...TYPE_MATCHERS.map((t) => t.label)].map((label) => (
                <button
                  key={label}
                  onClick={() => setTypeFilter(label)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
                    typeFilter === label
                      ? 'bg-[#3182f6] text-white'
                      : 'bg-white border border-[#e8e8e8] text-[#4e5968] hover:border-[#c0c0c0]'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* 유형별 건수 카드 */
          <div className="grid grid-cols-4 gap-2">
            {typeCounts.map((t) => (
              <button
                key={t.label}
                onClick={() => setTypeFilter(typeFilter === t.label ? '전체' : t.label)}
                className={`rounded-lg border p-3 text-center transition-all ${
                  typeFilter === t.label
                    ? 'ring-2 ring-[#3182f6] ' + t.cardColor
                    : 'bg-white border-[#e8e8e8] hover:border-[#d0d0d0]'
                }`}
              >
                <div className="text-lg">{t.icon}</div>
                <div className="text-xs font-medium text-[#333] mt-1">{t.label}</div>
                <div className="text-sm font-bold text-[#191f28]">{t.count}건</div>
              </button>
            ))}
          </div>
        )}

        {/* 결과 헤더 */}
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-[#191f28]">
            {periodTab === 'today' && <>🔔 주요 공시 {todayLabel && <span className="font-normal text-[#8b95a1]">({todayLabel})</span>}</>}
            {periodTab === 'week' && '📅 이번 주 주요 공시'}
            {periodTab === 'month' && '📅 이번 달 주요 공시'}
            {periodTab === 'search' && `🔍 검색 결과`}
          </h2>
          <span className="text-xs text-[#8b95a1]">
            {totalCount}건
            {typeFilter !== '전체' && (
              <button onClick={() => setTypeFilter('전체')} className="ml-2 text-[#3182f6] underline">
                필터 해제
              </button>
            )}
          </span>
        </div>

        {/* 공시 리스트 */}
        {displayGroups.length === 0 ? (
          <div className="bg-white rounded-lg border border-[#e8e8e8] p-8 text-center text-[#8b95a1]">
            {periodTab === 'search' ? '검색 결과가 없습니다' : '주요 공시가 없습니다'}
          </div>
        ) : (
          <div className="space-y-4">
            {displayGroups.map((group) => (
              <div key={group.date}>
                <div className="text-xs font-medium text-[#8b95a1] mb-2">{formatDate(group.date)}</div>
                <div className="space-y-2">
                  {group.items.map((d) => (
                    <DisclosureCard key={d.rcept_no} d={d} onClick={() => handleClick(d)} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ── 카드 컴포넌트 ──
function DisclosureCard({ d, onClick }: { d: Disclosure; onClick: () => void }) {
  const type = classifyType(d.report_nm);
  const badge = sentimentBadge(d.sentiment);
  const summary = d.ai_summary || d.detail_summary || d.report_nm;

  return (
    <button
      onClick={onClick}
      className="w-full text-left bg-white rounded-lg border border-[#e8e8e8] p-4 hover:border-[#c0c0c0] transition-colors"
    >
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span className="font-bold text-sm text-[#191f28]">{d.corp_name}</span>
            <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${type.color}`}>{type.label}</span>
            {badge && <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${badge.color}`}>{badge.text}</span>}
          </div>
          <p className="text-sm text-[#4e5968] line-clamp-2">{summary}</p>
          <div className="flex items-center gap-2 mt-2 text-xs text-[#8b95a1]">
            <span>{shortDate(d.rcept_dt)}</span>
            <span>·</span>
            <span>{d.stock_code}</span>
          </div>
        </div>
        <div className="text-[#8b95a1] text-sm mt-1">→</div>
      </div>
    </button>
  );
}
