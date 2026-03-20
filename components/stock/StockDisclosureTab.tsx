'use client';

import { useState, useMemo } from 'react';
import disclosuresData from '@/data/disclosures.json';

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
  sentiment?: string | null;
}

type FilterType = '주요' | '전체' | '자사주' | '실적' | '증자/CB' | '지분' | '기타';

const NOISE_RE = /최대주주등소유주식변동|기타경영사항\(자율공시\)|주주총회소집|정기주주총회결과|주주총회소집결의|주주총회소집공고/;

function isKeyDisclosure(d: Disclosure): boolean {
  const s = d.sentiment;
  return (s === '호재' || s === '악재' || s === '확인필요') && !NOISE_RE.test(d.report_nm);
}

const FILTERS: { label: FilterType; match: (d: Disclosure) => boolean }[] = [
  { label: '주요', match: isKeyDisclosure },
  { label: '전체', match: () => true },
  { label: '자사주', match: (d) => /자기주식|자사주/.test(d.report_nm) },
  { label: '실적', match: (d) => /실적|매출액또는손익|감사보고서|사업보고서|분기보고서|반기보고서/.test(d.report_nm) },
  { label: '증자/CB', match: (d) => /증권신고|유상증자|전환사채|신주인수권|합병|분할|감자/.test(d.report_nm) },
  { label: '지분', match: (d) => /대량보유|최대주주|소유주식변동/.test(d.report_nm) },
  { label: '기타', match: () => false },
];

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

function sentimentStyle(s: string | null | undefined): { badge: string; border: string; bg: string } | null {
  if (s === '호재') return { badge: 'bg-green-600 text-white', border: 'border-green-400', bg: 'bg-green-50' };
  if (s === '악재') return { badge: 'bg-red-600 text-white', border: 'border-red-400', bg: 'bg-red-50' };
  if (s === '확인필요') return { badge: 'bg-amber-500 text-white', border: 'border-amber-400', bg: 'bg-amber-50' };
  return null;
}

function formatDate(dt: string): string {
  if (dt.length !== 8) return dt;
  return `${dt.slice(4, 6)}.${dt.slice(6)}`;
}

function fullDate(dt: string): string {
  if (dt.length !== 8) return dt;
  return `${dt.slice(0, 4)}.${dt.slice(4, 6)}.${dt.slice(6)}`;
}

function dartUrl(rceptNo: string): string {
  return `https://dart.fss.or.kr/dsaf001/main.do?rcpNo=${rceptNo}`;
}

export default function StockDisclosureTab({ code }: { code: string }) {
  const [filter, setFilter] = useState<FilterType>('주요');
  const [showCount, setShowCount] = useState(20);

  const stockDisclosures = useMemo(() => {
    return (disclosuresData as { disclosures: Disclosure[] }).disclosures
      .filter((d) => d.stock_code === code);
  }, [code]);

  // 최근 3개월 하이라이트 (최대 3건)
  const highlights = useMemo(() => {
    const d = new Date();
    d.setMonth(d.getMonth() - 3);
    const cutoff = d.toISOString().slice(0, 10).replace(/-/g, '');
    return stockDisclosures
      .filter((d) => d.rcept_dt >= cutoff && isKeyDisclosure(d))
      .slice(0, 3);
  }, [stockDisclosures]);

  const filtered = useMemo(() => {
    if (filter === '전체') return stockDisclosures;
    if (filter === '기타') {
      const others = FILTERS.filter((f) => f.label !== '전체' && f.label !== '기타' && f.label !== '주요');
      return stockDisclosures.filter((d) => !others.some((f) => f.match(d)) && !isKeyDisclosure(d));
    }
    const f = FILTERS.find((f) => f.label === filter);
    return f ? stockDisclosures.filter(f.match) : stockDisclosures;
  }, [stockDisclosures, filter]);

  const visible = filtered.slice(0, showCount);

  if (stockDisclosures.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-[#e8e8e8] p-12 text-center">
        <div className="text-4xl mb-4">📋</div>
        <h3 className="text-lg font-bold text-[#191f28] mb-2">공시 데이터 없음</h3>
        <p className="text-[#8b95a1]">이 종목의 최근 1년 주요 공시가 없습니다</p>
      </div>
    );
  }

  const typeCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const f of FILTERS) {
      if (f.label === '전체') {
        counts['전체'] = stockDisclosures.length;
      } else if (f.label === '주요') {
        counts['주요'] = stockDisclosures.filter(isKeyDisclosure).length;
      } else if (f.label === '기타') {
        const others = FILTERS.filter((ff) => ff.label !== '전체' && ff.label !== '기타' && ff.label !== '주요');
        counts['기타'] = stockDisclosures.filter((d) => !others.some((ff) => ff.match(d)) && !isKeyDisclosure(d)).length;
      } else {
        counts[f.label] = stockDisclosures.filter(f.match).length;
      }
    }
    return counts;
  }, [stockDisclosures]);

  return (
    <div className="space-y-3">
      {/* 하이라이트 */}
      {highlights.length > 0 && (
        <div className="space-y-2">
          {highlights.map((h) => {
            const summary = h.ai_summary || h.detail_summary || h.report_nm;
            const style = sentimentStyle(h.sentiment);
            return (
              <a
                key={`hl-${h.rcept_no}`}
                href={dartUrl(h.rcept_no)}
                target="_blank"
                rel="noopener noreferrer"
                className={`block rounded-xl p-3 border-l-4 ${style?.border || 'border-gray-300'} ${style?.bg || 'bg-gray-50'} hover:shadow-md transition-shadow cursor-pointer`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-sm font-bold text-[#191f28] flex-shrink-0">{formatDate(h.rcept_dt)}</span>
                  <span className="text-sm text-[#191f28] flex-1 leading-snug">{summary}</span>
                  {style && (
                    <span className={`flex-shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${style.badge}`}>
                      {h.sentiment}
                    </span>
                  )}
                </div>
              </a>
            );
          })}
        </div>
      )}

      {/* 필터 */}
      <div className="flex flex-wrap gap-2">
        {FILTERS.map((f) => (
          <button
            key={f.label}
            onClick={() => { setFilter(f.label); setShowCount(20); }}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              filter === f.label
                ? 'bg-[#3182f6] text-white'
                : 'bg-white border border-[#e8e8e8] text-[#8b95a1] hover:border-[#3182f6] hover:text-[#3182f6]'
            }`}
          >
            {f.label}{typeCounts[f.label] ? ` ${typeCounts[f.label]}` : ''}
          </button>
        ))}
      </div>

      {/* 공시 리스트 */}
      <div className="bg-white rounded-xl shadow-sm border border-[#e8e8e8]">
        {visible.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-sm text-[#8b95a1]">해당 유형의 공시가 없습니다</p>
          </div>
        ) : (
          <div className="divide-y divide-[#e8e8e8]">
            {visible.map((d) => {
              const typeInfo = classifyType(d.report_nm);
              const style = sentimentStyle(d.sentiment);
              const summary = d.ai_summary || d.detail_summary;
              return (
                <a
                  key={d.rcept_no}
                  href={dartUrl(d.rcept_no)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 px-4 py-3 hover:bg-[#f2f4f6] transition-colors cursor-pointer group"
                  title={d.report_nm}
                >
                  <span className="text-xs text-[#8b95a1] flex-shrink-0 w-12">{formatDate(d.rcept_dt)}</span>
                  <span className={`flex-shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${typeInfo.color}`}>
                    {typeInfo.label}
                  </span>
                  {style && (
                    <span className={`flex-shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${style.badge}`}>
                      {d.sentiment === '확인필요' ? '확인' : d.sentiment}
                    </span>
                  )}
                  <span className="text-sm text-[#191f28] flex-1 truncate">
                    {summary || d.report_nm}
                  </span>
                  <span className="flex-shrink-0 text-[#8b95a1] opacity-0 group-hover:opacity-100 transition-opacity text-xs">
                    🔗
                  </span>
                </a>
              );
            })}
          </div>
        )}
      </div>

      {/* 더보기 */}
      {visible.length < filtered.length && (
        <button
          onClick={() => setShowCount((c) => c + 20)}
          className="w-full py-3 text-sm font-medium text-[#3182f6] bg-white rounded-xl border border-[#e8e8e8] hover:bg-blue-50 transition-colors"
        >
          더보기 ({filtered.length - visible.length}건 남음)
        </button>
      )}
    </div>
  );
}
