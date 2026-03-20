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
}

type FilterType = '전체' | '자사주' | '실적' | '증자/CB' | '지분' | '기타';

const FILTERS: { label: FilterType; match: (d: Disclosure) => boolean }[] = [
  { label: '전체', match: () => true },
  { label: '자사주', match: (d) => /자기주식|자사주/.test(d.report_nm) },
  { label: '실적', match: (d) => /실적|매출액또는손익|감사보고서|사업보고서|분기보고서|반기보고서/.test(d.report_nm) },
  { label: '증자/CB', match: (d) => /증권신고|유상증자|전환사채|신주인수권|합병|분할|감자/.test(d.report_nm) },
  { label: '지분', match: (d) => /대량보유|최대주주|소유주식변동/.test(d.report_nm) },
  { label: '기타', match: () => false }, // 나머지
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

function formatDate(dt: string): string {
  if (dt.length !== 8) return dt;
  return `${dt.slice(0, 4)}.${dt.slice(4, 6)}.${dt.slice(6)}`;
}

function dartUrl(rceptNo: string): string {
  return `https://dart.fss.or.kr/dsaf001/main.do?rcpNo=${rceptNo}`;
}

export default function StockDisclosureTab({ code }: { code: string }) {
  const [filter, setFilter] = useState<FilterType>('전체');
  const [showCount, setShowCount] = useState(20);

  const stockDisclosures = useMemo(() => {
    return (disclosuresData as { disclosures: Disclosure[] }).disclosures
      .filter((d) => d.stock_code === code);
  }, [code]);

  const filtered = useMemo(() => {
    if (filter === '전체') return stockDisclosures;
    if (filter === '기타') {
      // 다른 필터에 안 걸리는 것
      const otherFilters = FILTERS.filter((f) => f.label !== '전체' && f.label !== '기타');
      return stockDisclosures.filter((d) => !otherFilters.some((f) => f.match(d)));
    }
    const f = FILTERS.find((f) => f.label === filter);
    return f ? stockDisclosures.filter(f.match) : stockDisclosures;
  }, [stockDisclosures, filter]);

  const visible = filtered.slice(0, showCount);

  if (stockDisclosures.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-4xl mb-4">📋</div>
        <h3 className="text-lg font-bold text-[#191f28] mb-2">공시 데이터 없음</h3>
        <p className="text-[#8b95a1]">이 종목의 최근 1년 주요 공시가 없습니다</p>
      </div>
    );
  }

  // 유형별 건수
  const typeCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const f of FILTERS) {
      if (f.label === '전체') {
        counts['전체'] = stockDisclosures.length;
      } else if (f.label === '기타') {
        const otherFilters = FILTERS.filter((ff) => ff.label !== '전체' && ff.label !== '기타');
        counts['기타'] = stockDisclosures.filter((d) => !otherFilters.some((ff) => ff.match(d))).length;
      } else {
        counts[f.label] = stockDisclosures.filter(f.match).length;
      }
    }
    return counts;
  }, [stockDisclosures]);

  return (
    <div className="space-y-4">
      {/* 필터 */}
      <div className="flex flex-wrap gap-2">
        {FILTERS.map((f) => (
          <button
            key={f.label}
            onClick={() => { setFilter(f.label); setShowCount(20); }}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              filter === f.label
                ? 'bg-[#3182f6] text-white'
                : 'bg-white border border-[#e8e8e8] text-[#8b95a1] hover:border-[#3182f6] hover:text-[#3182f6]'
            }`}
          >
            {f.label} {typeCounts[f.label] ? `(${typeCounts[f.label]})` : ''}
          </button>
        ))}
      </div>

      {/* 공시 목록 */}
      <div className="space-y-2">
        {visible.map((d) => {
          const typeInfo = classifyType(d.report_nm);
          return (
            <a
              key={d.rcept_no}
              href={dartUrl(d.rcept_no)}
              target="_blank"
              rel="noopener noreferrer"
              className="block bg-white rounded-lg border border-[#e8e8e8] p-4 hover:border-[#3182f6] hover:shadow-sm transition-all"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${typeInfo.color}`}>
                      {typeInfo.label}
                    </span>
                    {d.rm && d.rm.trim() && (
                      <span className="text-xs text-[#8b95a1]">[{d.rm.trim()}]</span>
                    )}
                  </div>
                  <p className="text-sm font-medium text-[#191f28] leading-snug">
                    {d.report_nm}
                  </p>
                </div>
                <div className="flex-shrink-0 text-right">
                  <div className="text-xs text-[#8b95a1]">{formatDate(d.rcept_dt)}</div>
                  <div className="text-xs text-[#3182f6] mt-1">DART →</div>
                </div>
              </div>
            </a>
          );
        })}
      </div>

      {/* 더보기 */}
      {visible.length < filtered.length && (
        <button
          onClick={() => setShowCount((c) => c + 20)}
          className="w-full py-3 text-sm font-medium text-[#3182f6] bg-white rounded-lg border border-[#e8e8e8] hover:bg-blue-50 transition-colors"
        >
          더보기 ({filtered.length - visible.length}건 남음)
        </button>
      )}
    </div>
  );
}
