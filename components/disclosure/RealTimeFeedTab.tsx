'use client';

import { useState, useEffect } from 'react';

interface Disclosure {
  id: string;
  corp_name: string;
  corp_code: string;
  stock_code: string;
  market: string;
  report_nm: string;
  rcept_no: string;
  rcept_dt: string;
  disclosure_type: string;
  importance: string;
  ai_summary: string;
  ai_impact: string;
  ai_impact_reason: string;
  ai_score: number;
  source: string;
  created_at: string;
}

type PeriodFilter = 'today' | 'week' | 'month' | 'all';
type ImpactFilter = '전체' | '긍정' | '부정' | '중립';

const impactColor: Record<string, { bg: string; text: string; border: string }> = {
  '긍정': { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  '부정': { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
  '중립': { bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-200' },
};

const importanceIcon: Record<string, string> = {
  high: '🔴',
  medium: '🟡',
  low: '🟢',
};

function ScoreBar({ score }: { score: number }) {
  const color = score >= 70 ? 'bg-blue-500' : score >= 40 ? 'bg-yellow-400' : 'bg-red-500';
  return (
    <div className="flex items-center gap-2 mt-2">
      <span className="text-xs text-gray-500 w-14 shrink-0">AI 점수</span>
      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-xs font-semibold text-gray-700 w-8 text-right">{score}</span>
    </div>
  );
}

export default function RealTimeFeedTab() {
  const [data, setData] = useState<Disclosure[]>([]);
  const [period, setPeriod] = useState<PeriodFilter>('all');
  const [impact, setImpact] = useState<ImpactFilter>('전체');
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetch('/invest-sns/disclosure_seed.json')
      .then(r => r.json())
      .then(setData)
      .catch(() => {});
  }, []);

  const toggle = (id: string) => {
    setExpanded(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const filtered = data.filter(d => {
    if (impact !== '전체' && d.ai_impact !== impact) return false;
    if (period === 'all') return true;
    const dt = new Date(d.rcept_dt);
    const now = new Date('2026-03-04');
    const diff = (now.getTime() - dt.getTime()) / (1000 * 60 * 60 * 24);
    if (period === 'today') return diff < 1;
    if (period === 'week') return diff < 7;
    if (period === 'month') return diff < 30;
    return true;
  });

  const periods: { key: PeriodFilter; label: string }[] = [
    { key: 'today', label: '오늘' },
    { key: 'week', label: '1주' },
    { key: 'month', label: '1개월' },
    { key: 'all', label: '전체' },
  ];

  const impacts: ImpactFilter[] = ['전체', '긍정', '부정', '중립'];

  return (
    <div className="py-4 space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        <div className="flex gap-1 bg-white rounded-xl p-1 shadow-sm">
          {periods.map(p => (
            <button
              key={p.key}
              onClick={() => setPeriod(p.key)}
              className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                period === p.key ? 'bg-gray-900 text-white' : 'text-gray-500 hover:bg-gray-100'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
        <div className="flex gap-1 bg-white rounded-xl p-1 shadow-sm">
          {impacts.map(i => (
            <button
              key={i}
              onClick={() => setImpact(i)}
              className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                impact === i ? 'bg-gray-900 text-white' : 'text-gray-500 hover:bg-gray-100'
              }`}
            >
              {i}
            </button>
          ))}
        </div>
      </div>

      {/* Results count */}
      <p className="text-sm text-gray-500">{filtered.length}건의 공시</p>

      {/* Cards */}
      <div className="space-y-3">
        {filtered.map(d => {
          const ic = impactColor[d.ai_impact] || impactColor['중립'];
          const isOpen = expanded.has(d.id);
          return (
            <div
              key={d.id}
              className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden cursor-pointer active:bg-gray-50 transition-colors"
              onClick={() => toggle(d.id)}
            >
              <div className="p-4">
                {/* Top row: badges */}
                <div className="flex items-center gap-2 mb-2">
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border ${ic.bg} ${ic.text} ${ic.border}`}>
                    {d.ai_impact}
                  </span>
                  <span className="text-sm">{importanceIcon[d.importance] || '🟢'}</span>
                  <span className="text-xs text-gray-400 bg-gray-50 px-2 py-0.5 rounded">{d.disclosure_type}</span>
                </div>

                {/* Title */}
                <h3 className="font-semibold text-gray-900 text-sm leading-snug">{d.report_nm}</h3>
                <p className="text-xs text-gray-500 mt-1">{d.corp_name} · {d.rcept_dt}</p>

                {/* Summary */}
                <p className={`text-sm text-gray-700 mt-2 leading-relaxed ${isOpen ? '' : 'line-clamp-2'}`}>
                  {d.ai_summary}
                </p>

                {/* Expanded content */}
                {isOpen && (
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <p className="text-xs font-medium text-gray-500 mb-1">💡 AI 영향 분석</p>
                    <p className="text-sm text-gray-700 leading-relaxed">{d.ai_impact_reason}</p>
                  </div>
                )}

                {/* Score bar */}
                <ScoreBar score={d.ai_score} />
              </div>
            </div>
          );
        })}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <p className="text-4xl mb-2">📭</p>
          <p>해당 조건의 공시가 없습니다</p>
        </div>
      )}
    </div>
  );
}
