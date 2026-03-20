'use client';

import { useState, useMemo } from 'react';
import disclosuresData from '@/data/disclosures.json';

interface DisclosureDetail {
  detail_type?: string;
  shares?: number | null;
  new_shares?: number | null;
  amount?: number | null;
  fund_total?: number | null;
  period_start?: string | null;
  period_end?: string | null;
  purpose?: string;
  method?: string;
}

interface Disclosure {
  stock_code: string;
  corp_name: string;
  report_nm: string;
  rcept_no: string;
  rcept_dt: string;
  pblntf_ty: string;
  rm: string;
  detail?: DisclosureDetail;
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

function sentimentBadge(s: string | null | undefined): { icon: string; color: string } | null {
  if (!s) return null;
  if (s === '호재') return { icon: '호재', color: 'bg-red-50 text-red-600' };
  if (s === '악재') return { icon: '악재', color: 'bg-blue-50 text-blue-600' };
  if (s === '확인필요') return { icon: '확인', color: 'bg-amber-50 text-amber-600' };
  return null;
}

function sentimentDot(s: string | null | undefined): string {
  if (s === '호재') return 'text-red-500';
  if (s === '악재') return 'text-blue-500';
  if (s === '확인필요') return 'text-amber-500';
  return 'text-gray-400';
}

function formatDate(dt: string): string {
  if (dt.length !== 8) return dt;
  return `${dt.slice(0, 4)}.${dt.slice(4, 6)}.${dt.slice(6)}`;
}

function shortDate(dt: string): string {
  if (dt.length !== 8) return dt;
  return `${parseInt(dt.slice(4, 6))}/${parseInt(dt.slice(6))}`;
}

function dartUrl(rceptNo: string): string {
  return `https://dart.fss.or.kr/dsaf001/main.do?rcpNo=${rceptNo}`;
}

function hasDetailData(d: Disclosure): boolean {
  return !!(d.detail || d.ai_summary || d.detail_summary);
}

// ── 모달 ──
function DisclosureModal({ d, onClose }: { d: Disclosure; onClose: () => void }) {
  const typeInfo = classifyType(d.report_nm);
  const badge = sentimentBadge(d.sentiment);
  const detail = d.detail;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40" />
      <div
        className="bg-white rounded-xl p-5 w-full max-w-md relative z-10 max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 헤더 */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${typeInfo.color}`}>
              {typeInfo.label}
            </span>
            {badge && (
              <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${badge.color}`}>
                {badge.icon}
              </span>
            )}
            <span className="text-xs text-[#8b95a1]">{formatDate(d.rcept_dt)}</span>
          </div>
          <button onClick={onClose} className="text-[#8b95a1] hover:text-[#191f28] text-lg">
            ✕
          </button>
        </div>

        {/* 제목 */}
        <h3 className="text-base font-bold text-[#191f28] mb-3 leading-snug">
          {d.report_nm}
        </h3>

        {/* AI 해석 */}
        {d.ai_summary && (
          <div className="bg-blue-50 rounded-lg p-3 mb-3">
            <p className="text-sm text-blue-800 leading-relaxed">{d.ai_summary}</p>
          </div>
        )}

        {/* 상세 데이터 */}
        {detail && (
          <div className="bg-gray-50 rounded-lg p-3 mb-3">
            <h4 className="text-xs font-medium text-[#8b95a1] mb-2">상세 정보</h4>
            <div className="space-y-1">
              {detail.detail_type === 'treasury_acquire' && (
                <>
                  {detail.shares && <DetailRow label="취득 주식수" value={`${detail.shares.toLocaleString()}주`} />}
                  {detail.amount && <DetailRow label="취득 금액" value={formatKrAmount(detail.amount)} />}
                  {detail.period_start && detail.period_end && (
                    <DetailRow label="취득 기간" value={`${detail.period_start} ~ ${detail.period_end}`} />
                  )}
                  {detail.purpose && <DetailRow label="목적" value={detail.purpose} />}
                  {detail.method && <DetailRow label="방법" value={detail.method} />}
                </>
              )}
              {detail.detail_type === 'treasury_dispose' && (
                <>
                  {detail.shares && <DetailRow label="처분 주식수" value={`${detail.shares.toLocaleString()}주`} />}
                  {detail.amount && <DetailRow label="처분 금액" value={formatKrAmount(detail.amount)} />}
                  {detail.period_start && detail.period_end && (
                    <DetailRow label="처분 기간" value={`${detail.period_start} ~ ${detail.period_end}`} />
                  )}
                  {detail.purpose && <DetailRow label="목적" value={detail.purpose} />}
                </>
              )}
              {detail.detail_type === 'capital_increase' && (
                <>
                  {detail.new_shares && <DetailRow label="신주 발행" value={`${detail.new_shares.toLocaleString()}주`} />}
                  {detail.fund_total && <DetailRow label="자금 총액" value={formatKrAmount(detail.fund_total)} />}
                  {detail.face_value && <DetailRow label="액면가" value={`${detail.face_value.toLocaleString()}원`} />}
                  {detail.method && <DetailRow label="증자 방식" value={detail.method} />}
                </>
              )}
            </div>
          </div>
        )}

        {/* detail_summary (detail 없지만 summary 있는 경우) */}
        {!detail && d.detail_summary && (
          <div className="bg-gray-50 rounded-lg p-3 mb-3">
            <p className="text-sm text-[#191f28]">{d.detail_summary}</p>
          </div>
        )}

        {/* DART 원문 링크 */}
        <a
          href={dartUrl(d.rcept_no)}
          target="_blank"
          rel="noopener noreferrer"
          className="block w-full text-center py-2 text-sm font-medium text-[#3182f6] bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
        >
          DART 원문 보기
        </a>
      </div>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start gap-2">
      <span className="text-xs text-[#8b95a1] flex-shrink-0 w-20">{label}</span>
      <span className="text-xs text-[#191f28] font-medium">{value}</span>
    </div>
  );
}

function formatKrAmount(n: number): string {
  if (n >= 1_0000_0000_0000) return `${(n / 1_0000_0000_0000).toFixed(1)}조원`;
  if (n >= 1_0000_0000) return `${Math.round(n / 1_0000_0000).toLocaleString()}억원`;
  return `${n.toLocaleString()}원`;
}

// ── 메인 ──
export default function StockDisclosureTab({ code }: { code: string }) {
  const [filter, setFilter] = useState<FilterType>('주요');
  const [showCount, setShowCount] = useState(20);
  const [modalItem, setModalItem] = useState<Disclosure | null>(null);

  const stockDisclosures = useMemo(() => {
    return (disclosuresData as { disclosures: Disclosure[] }).disclosures
      .filter((d) => d.stock_code === code);
  }, [code]);

  const highlights = useMemo(() => {
    const d = new Date();
    d.setMonth(d.getMonth() - 3);
    const cutoff = d.toISOString().slice(0, 10).replace(/-/g, '');
    return stockDisclosures
      .filter((d) => d.rcept_dt >= cutoff && isKeyDisclosure(d))
      .slice(0, 5);
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
      <div className="text-center py-12">
        <div className="text-4xl mb-4">📋</div>
        <h3 className="text-lg font-bold text-[#191f28] mb-2">공시 데이터 없음</h3>
        <p className="text-[#8b95a1]">이 종목의 최근 1년 주요 공시가 없습니다</p>
      </div>
    );
  }

  const typeCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const f of FILTERS) {
      if (f.label === '전체') counts['전체'] = stockDisclosures.length;
      else if (f.label === '주요') counts['주요'] = stockDisclosures.filter(isKeyDisclosure).length;
      else if (f.label === '기타') {
        const others = FILTERS.filter((ff) => ff.label !== '전체' && ff.label !== '기타' && ff.label !== '주요');
        counts['기타'] = stockDisclosures.filter((d) => !others.some((ff) => ff.match(d)) && !isKeyDisclosure(d)).length;
      } else counts[f.label] = stockDisclosures.filter(f.match).length;
    }
    return counts;
  }, [stockDisclosures]);

  function handleClick(d: Disclosure) {
    if (hasDetailData(d)) {
      setModalItem(d);
    } else {
      window.open(dartUrl(d.rcept_no), '_blank');
    }
  }

  return (
    <div className="space-y-4">
      {/* 모달 */}
      {modalItem && <DisclosureModal d={modalItem} onClose={() => setModalItem(null)} />}

      {/* 상단 요약 */}
      {highlights.length > 0 && (
        <div className="bg-white rounded-lg border border-[#e8e8e8] p-4">
          <h4 className="text-xs font-medium text-[#8b95a1] mb-3">최근 3개월 주요 이벤트</h4>
          <div className="space-y-2">
            {highlights.map((h) => {
              const summary = h.ai_summary || h.detail_summary || h.report_nm;
              const dotColor = sentimentDot(h.sentiment);
              return (
                <div
                  key={`hl-${h.rcept_no}`}
                  className="flex items-start gap-2 hover:bg-gray-50 rounded px-1 py-0.5 transition-colors cursor-pointer"
                  onClick={() => handleClick(h)}
                >
                  <span className={`mt-1 ${dotColor}`}>●</span>
                  <span className="text-sm text-[#191f28] flex-1 leading-snug">{summary}</span>
                  <span className="text-xs text-[#8b95a1] flex-shrink-0">({shortDate(h.rcept_dt)})</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

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
        {visible.length === 0 && (
          <div className="text-center py-8">
            <p className="text-sm text-[#8b95a1]">해당 유형의 공시가 없습니다</p>
          </div>
        )}
        {visible.map((d) => {
          const typeInfo = classifyType(d.report_nm);
          const badge = sentimentBadge(d.sentiment);
          const summary = d.ai_summary || d.detail_summary;
          const clickable = hasDetailData(d);
          return (
            <div
              key={d.rcept_no}
              onClick={() => handleClick(d)}
              className="block bg-white rounded-lg border border-[#e8e8e8] p-4 hover:border-[#3182f6] hover:shadow-sm transition-all cursor-pointer"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${typeInfo.color}`}>
                      {typeInfo.label}
                    </span>
                    {badge && (
                      <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${badge.color}`}>
                        {badge.icon}
                      </span>
                    )}
                    {d.rm && d.rm.trim() && (
                      <span className="text-xs text-[#8b95a1]">[{d.rm.trim()}]</span>
                    )}
                  </div>
                  {summary ? (
                    <>
                      <p className="text-sm font-medium text-[#191f28] leading-snug">{summary}</p>
                      <p className="text-xs text-[#8b95a1] mt-1">{d.report_nm}</p>
                    </>
                  ) : (
                    <p className="text-sm font-medium text-[#191f28] leading-snug">{d.report_nm}</p>
                  )}
                </div>
                <div className="flex-shrink-0 text-right">
                  <div className="text-xs text-[#8b95a1]">{formatDate(d.rcept_dt)}</div>
                  <div className="text-xs text-[#8b95a1] mt-1">{clickable ? '상세' : 'DART'}</div>
                </div>
              </div>
            </div>
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
