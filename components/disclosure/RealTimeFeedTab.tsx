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
  // v6 AI 분석 필드
  grade?: string;
  verdict?: string;
  verdict_tone?: string;
  what?: string;
  so_what?: string;
  now_what_holding?: string;
  now_what_not_holding?: string;
  risk?: string;
  size_assessment?: string;
  percentile?: string;
  tags?: string[];
}

type GradeFilter = '전체' | 'A' | 'B' | 'C' | 'D';
type TypeFilter = '전체' | '실적' | 'CB' | '자사주' | '풍문' | '수주';
type ImpactFilter = '전체' | '긍정' | '부정' | '중립';

// importance → 등급 매핑 (v6 grade 없을 때 폴백)
const importanceToGrade: Record<string, string> = {
  high: 'A',
  medium: 'B',
  low: 'C',
};

// disclosure_type → 유형 필터 매핑
const typeToFilter: Record<string, TypeFilter> = {
  '실적': '실적',
  '전환사채': 'CB',
  '자기주식': '자사주',
  '풍문': '풍문',
  '대규모계약': '수주',
  '수주계약': '수주',
  '수주': '수주',
};

const gradeColor: Record<string, string> = {
  A: 'bg-red-100 text-red-700 border-red-200',
  B: 'bg-orange-100 text-orange-700 border-orange-200',
  C: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  D: 'bg-gray-100 text-gray-600 border-gray-200',
};

const gradeDesc: Record<string, string> = {
  A: '즉시행동',
  B: '24시간내',
  C: '참고',
  D: '무시',
};

const verdictToneColor: Record<string, string> = {
  bullish: 'text-green-700',
  bearish: 'text-red-700',
  neutral: 'text-gray-600',
};

const verdictToneBg: Record<string, string> = {
  bullish: 'bg-green-50 border-green-200',
  bearish: 'bg-red-50 border-red-200',
  neutral: 'bg-gray-50 border-gray-200',
};

const impactColor: Record<string, { bg: string; text: string; border: string }> = {
  '긍정': { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  '부정': { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
  '중립': { bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-200' },
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

// 보유/미보유 탭
function NowWhatTabs({ holding, notHolding }: { holding: string; notHolding: string }) {
  const [tab, setTab] = useState<'holding' | 'not'>('holding');
  return (
    <div>
      <div className="flex gap-1 mb-2">
        <button
          onClick={() => setTab('holding')}
          className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
            tab === 'holding' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-500'
          }`}
        >
          📦 보유 중
        </button>
        <button
          onClick={() => setTab('not')}
          className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
            tab === 'not' ? 'bg-gray-700 text-white' : 'bg-gray-100 text-gray-500'
          }`}
        >
          👀 미보유
        </button>
      </div>
      <p className="text-sm text-gray-700 leading-relaxed">
        {tab === 'holding' ? holding : notHolding}
      </p>
    </div>
  );
}

// AI 분석 모달 (v6)
function AiModal({ disclosure, onClose }: { disclosure: Disclosure; onClose: () => void }) {
  // v6 grade 우선, 없으면 importance 폴백
  const grade = disclosure.grade || importanceToGrade[disclosure.importance] || 'C';
  const ic = impactColor[disclosure.ai_impact] || impactColor['중립'];
  const tone = disclosure.verdict_tone || 'neutral';
  const toneBg = verdictToneBg[tone] || verdictToneBg['neutral'];
  const toneColor = verdictToneColor[tone] || verdictToneColor['neutral'];

  // v6 필드 유무
  const hasV6 = !!(disclosure.verdict && disclosure.what && disclosure.so_what);

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-white w-full sm:max-w-lg sm:mx-4 rounded-t-2xl sm:rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] overflow-y-auto"
        onClick={e => e.stopPropagation()}
      >
        {/* 모달 헤더 */}
        <div className="sticky top-0 bg-white border-b border-gray-100 px-5 py-4 flex items-start justify-between">
          <div className="flex-1 pr-3">
            <p className="text-xs text-gray-400 mb-0.5">{disclosure.corp_name} · {disclosure.rcept_dt}</p>
            <h3 className="font-semibold text-gray-900 text-sm leading-snug">{disclosure.report_nm}</h3>
          </div>
          <button onClick={onClose} className="shrink-0 text-gray-400 hover:text-gray-600 text-xl leading-none">✕</button>
        </div>

        <div className="px-5 py-4 space-y-4">
          {/* 등급 + 감성 뱃지 */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`px-2.5 py-1 rounded-lg text-xs font-bold border ${gradeColor[grade] || gradeColor['C']}`}>
              {grade}등급 · {gradeDesc[grade] || '참고'}
            </span>
            <span className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${ic.bg} ${ic.text} ${ic.border}`}>
              {disclosure.ai_impact}
            </span>
            <span className="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded">{disclosure.disclosure_type}</span>
          </div>

          {hasV6 ? (
            <>
              {/* v6: verdict */}
              <div className={`rounded-xl p-4 border ${toneBg}`}>
                <p className={`text-xs font-semibold mb-1.5 ${toneColor}`}>
                  🤖 AI 평결 · {tone === 'bullish' ? '🟢 강세' : tone === 'bearish' ? '🔴 약세' : '⚪ 중립'}
                </p>
                <p className={`text-sm font-medium ${toneColor}`}>{disclosure.verdict}</p>
              </div>

              {/* v6: what */}
              <div>
                <p className="text-xs font-semibold text-gray-500 mb-1.5 flex items-center gap-1">
                  <span className="w-4 h-4 bg-blue-500 text-white rounded-full text-center text-xs leading-4">1</span>
                  What — 무슨 일인가
                </p>
                <p className="text-sm text-gray-700 leading-relaxed">{disclosure.what}</p>
              </div>

              {/* v6: so_what */}
              <div>
                <p className="text-xs font-semibold text-gray-500 mb-1.5 flex items-center gap-1">
                  <span className="w-4 h-4 bg-purple-500 text-white rounded-full text-center text-xs leading-4">2</span>
                  So What — 숫자로 본 크기
                </p>
                <p className="text-sm text-gray-700 leading-relaxed">{disclosure.so_what}</p>
              </div>

              {/* v6: now_what 탭 */}
              {(disclosure.now_what_holding || disclosure.now_what_not_holding) && (
                <div>
                  <p className="text-xs font-semibold text-gray-500 mb-2 flex items-center gap-1">
                    <span className="w-4 h-4 bg-green-500 text-white rounded-full text-center text-xs leading-4">3</span>
                    Now What — 어떻게 할까
                  </p>
                  <NowWhatTabs
                    holding={disclosure.now_what_holding || '추가 정보 확인 필요.'}
                    notHolding={disclosure.now_what_not_holding || '진입 시점 아님.'}
                  />
                </div>
              )}

              {/* v6: risk */}
              {disclosure.risk && (
                <div className="bg-orange-50 border border-orange-200 rounded-xl p-3">
                  <p className="text-xs font-semibold text-orange-600 mb-1">⚠️ 핵심 리스크</p>
                  <p className="text-sm text-orange-800">{disclosure.risk}</p>
                </div>
              )}

              {/* v6: size_assessment + percentile */}
              {(disclosure.size_assessment || disclosure.percentile) && (
                <div className="flex items-center gap-3 text-xs text-gray-400">
                  {disclosure.size_assessment && (
                    <span className="bg-gray-50 px-2 py-1 rounded border border-gray-100">
                      규모: {disclosure.size_assessment}
                    </span>
                  )}
                  {disclosure.percentile && (
                    <span className="bg-gray-50 px-2 py-1 rounded border border-gray-100">
                      {disclosure.percentile}
                    </span>
                  )}
                </div>
              )}

              {/* v6: tags */}
              {disclosure.tags && disclosure.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {disclosure.tags.map((tag, i) => (
                    <span key={i} className="text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded-full border border-indigo-100">
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
            </>
          ) : (
            <>
              {/* 하위 호환: v6 필드 없을 때 기존 방식 */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100">
                <p className="text-xs font-semibold text-blue-600 mb-1.5">🤖 AI 평결 (Verdict)</p>
                <p className="text-sm font-medium text-gray-900">{disclosure.ai_impact || '중립'}</p>
              </div>
              <div>
                <p className="text-xs font-semibold text-gray-500 mb-1.5 flex items-center gap-1">
                  <span className="w-4 h-4 bg-blue-500 text-white rounded-full text-center text-xs leading-4">1</span>
                  What — 무슨 일인가
                </p>
                <p className="text-sm text-gray-700 leading-relaxed">{disclosure.ai_summary}</p>
              </div>
              <div>
                <p className="text-xs font-semibold text-gray-500 mb-1.5 flex items-center gap-1">
                  <span className="w-4 h-4 bg-purple-500 text-white rounded-full text-center text-xs leading-4">2</span>
                  So What — 왜 중요한가
                </p>
                <p className="text-sm text-gray-700 leading-relaxed">{disclosure.ai_impact_reason}</p>
              </div>
            </>
          )}

          {/* Score */}
          <ScoreBar score={disclosure.ai_score} />
        </div>

        {/* DART 링크 */}
        <div className="px-5 pb-5">
          <a
            href={`https://dart.fss.or.kr/dsaf001/main.do?rcpNo=${disclosure.rcept_no}`}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full text-center py-3 rounded-xl bg-gray-900 text-white text-sm font-medium hover:bg-gray-700 transition-colors"
          >
            DART 원문 보기 →
          </a>
        </div>
      </div>
    </div>
  );
}

export default function RealTimeFeedTab() {
  const [data, setData] = useState<Disclosure[]>([]);
  const [grade, setGrade] = useState<GradeFilter>('전체');
  const [type, setType] = useState<TypeFilter>('전체');
  const [impact, setImpact] = useState<ImpactFilter>('전체');
  const [modal, setModal] = useState<Disclosure | null>(null);

  useEffect(() => {
    fetch('/invest-sns/disclosure_seed.json')
      .then(r => r.json())
      .then(setData)
      .catch(() => {});
  }, []);

  const filtered = data.filter(d => {
    // v6 grade 우선, 없으면 importance 폴백
    const dGrade = d.grade || importanceToGrade[d.importance] || 'C';
    if (grade !== '전체' && dGrade !== grade) return false;
    if (type !== '전체') {
      const dType = typeToFilter[d.disclosure_type];
      if (dType !== type) return false;
    }
    if (impact !== '전체' && d.ai_impact !== impact) return false;
    return true;
  });

  const grades: GradeFilter[] = ['전체', 'A', 'B', 'C', 'D'];
  const types: TypeFilter[] = ['전체', '실적', 'CB', '자사주', '풍문', '수주'];
  const impacts: ImpactFilter[] = ['전체', '긍정', '부정', '중립'];

  return (
    <div className="py-4 space-y-3">
      {/* 필터 그룹 */}
      <div className="space-y-2">
        {/* 등급 필터 */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400 w-10 shrink-0">등급</span>
          <div className="flex gap-1 bg-white rounded-xl p-1 shadow-sm overflow-x-auto">
            {grades.map(g => (
              <button
                key={g}
                onClick={() => setGrade(g)}
                className={`px-3 py-1.5 text-sm rounded-lg transition-colors whitespace-nowrap font-medium ${
                  grade === g ? 'bg-gray-900 text-white' : 'text-gray-500 hover:bg-gray-100'
                }`}
              >
                {g}
              </button>
            ))}
          </div>
        </div>

        {/* 유형 필터 */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400 w-10 shrink-0">유형</span>
          <div className="flex gap-1 bg-white rounded-xl p-1 shadow-sm overflow-x-auto">
            {types.map(t => (
              <button
                key={t}
                onClick={() => setType(t)}
                className={`px-3 py-1.5 text-sm rounded-lg transition-colors whitespace-nowrap ${
                  type === t ? 'bg-gray-900 text-white' : 'text-gray-500 hover:bg-gray-100'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* 감성 필터 */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400 w-10 shrink-0">감성</span>
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
      </div>

      {/* 결과 수 */}
      <p className="text-sm text-gray-500">{filtered.length}건의 공시</p>

      {/* 카드 목록 */}
      <div className="space-y-3">
        {filtered.map(d => {
          const dGrade = d.grade || importanceToGrade[d.importance] || 'C';
          const ic = impactColor[d.ai_impact] || impactColor['중립'];
          // 카드에는 verdict 있으면 우선 표시
          const summaryText = d.verdict || d.ai_summary;
          return (
            <div
              key={d.id}
              className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden cursor-pointer active:bg-gray-50 transition-colors"
              onClick={() => setModal(d)}
            >
              <div className="p-4">
                {/* 뱃지 행 */}
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <span className={`px-2 py-0.5 rounded text-xs font-bold border ${gradeColor[dGrade] || gradeColor['C']}`}>
                    {dGrade}
                  </span>
                  {gradeDesc[dGrade] && (
                    <span className="text-xs text-gray-400">{gradeDesc[dGrade]}</span>
                  )}
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border ${ic.bg} ${ic.text} ${ic.border}`}>
                    {d.ai_impact}
                  </span>
                  <span className="text-xs text-gray-400 bg-gray-50 px-2 py-0.5 rounded">{d.disclosure_type}</span>
                </div>

                {/* 제목 */}
                <h3 className="font-semibold text-gray-900 text-sm leading-snug">{d.report_nm}</h3>
                <p className="text-xs text-gray-500 mt-1">{d.corp_name} · {d.rcept_dt}</p>

                {/* 요약/verdict (2줄) */}
                <p className={`text-sm mt-2 leading-relaxed line-clamp-2 ${
                  d.verdict
                    ? (d.verdict_tone === 'bullish' ? 'text-green-700 font-medium' :
                       d.verdict_tone === 'bearish' ? 'text-red-700 font-medium' :
                       'text-gray-700')
                    : 'text-gray-700'
                }`}>
                  {summaryText}
                </p>

                {/* tags */}
                {d.tags && d.tags.length > 0 && (
                  <div className="flex gap-1 mt-2 flex-wrap">
                    {d.tags.slice(0, 3).map((tag, i) => (
                      <span key={i} className="text-xs text-indigo-500 bg-indigo-50 px-1.5 py-0.5 rounded">
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}

                {/* 점수 바 */}
                <ScoreBar score={d.ai_score} />

                <p className="text-xs text-blue-500 mt-2 text-right">AI 분석 보기 →</p>
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

      {/* AI 분석 모달 */}
      {modal && <AiModal disclosure={modal} onClose={() => setModal(null)} />}
    </div>
  );
}
