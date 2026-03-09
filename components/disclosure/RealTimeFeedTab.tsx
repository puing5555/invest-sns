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
  // AI 모달용 확장 필드 (있으면 사용, 없으면 ai_summary에서 생성)
  verdict?: string;
  what?: string;
  so_what?: string;
  now_what?: string;
}

type GradeFilter = '전체' | 'A' | 'B' | 'C' | 'D';
type TypeFilter = '전체' | '실적' | 'CB/BW' | '자사주' | '풍문' | '수주' | '증자' | '기타';
type ImpactFilter = '전체' | '긍정' | '부정' | '중립';

// importance → 등급 매핑
const importanceToGrade: Record<string, string> = {
  high: 'A',
  medium: 'B',
  low: 'C',
};

// disclosure_type → 유형 필터 매핑 (v6 기준)
const typeToFilter: Record<string, TypeFilter> = {
  '실적': '실적',
  '전환사채': 'CB/BW',
  '자기주식': '자사주',
  '풍문': '풍문',
  '수주': '수주',
  '대규모계약': '수주',
  '단일판매공급': '수주',
  '유상증자': '증자',
  '무상증자': '증자',
  // 기타 그룹
  '합병분할': '기타',
  '배당': '기타',
  '감자': '기타',
  '법적리스크': '기타',
  '최대주주변경': '기타',
  '상장폐지': '기타',
  '기타': '기타',
};

const gradeColor: Record<string, string> = {
  A: 'bg-red-100 text-red-700 border-red-200',
  B: 'bg-orange-100 text-orange-700 border-orange-200',
  C: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  D: 'bg-gray-100 text-gray-600 border-gray-200',
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

// AI 분석 모달
function AiModal({ disclosure, onClose }: { disclosure: Disclosure; onClose: () => void }) {
  const grade = importanceToGrade[disclosure.importance] || 'C';
  const ic = impactColor[disclosure.ai_impact] || impactColor['중립'];

  // verdict/what/so_what/now_what 필드 없으면 ai_summary에서 생성
  const verdict = disclosure.verdict || disclosure.ai_impact || '중립';
  const what = disclosure.what || disclosure.ai_summary || '공시 내용을 요약 중입니다.';
  const soWhat = disclosure.so_what || disclosure.ai_impact_reason || '시장 영향을 분석 중입니다.';
  const nowWhat = disclosure.now_what || '추가 공시 모니터링이 필요합니다.';

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
          <div className="flex items-center gap-2">
            <span className={`px-2.5 py-1 rounded-lg text-xs font-bold border ${gradeColor[grade] || gradeColor['C']}`}>
              {grade}등급
            </span>
            <span className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${ic.bg} ${ic.text} ${ic.border}`}>
              {disclosure.ai_impact}
            </span>
            <span className="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded">{disclosure.disclosure_type}</span>
          </div>

          {/* AI 평결 (verdict) */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100">
            <p className="text-xs font-semibold text-blue-600 mb-1.5">🤖 AI 평결 (Verdict)</p>
            <p className="text-sm font-medium text-gray-900">{verdict}</p>
          </div>

          {/* What — 무슨 일이 있었나 */}
          <div>
            <p className="text-xs font-semibold text-gray-500 mb-1.5 flex items-center gap-1">
              <span className="w-4 h-4 bg-blue-500 text-white rounded-full text-center text-xs leading-4">1</span>
              What — 무슨 일인가
            </p>
            <p className="text-sm text-gray-700 leading-relaxed">{what}</p>
          </div>

          {/* So What — 왜 중요한가 */}
          <div>
            <p className="text-xs font-semibold text-gray-500 mb-1.5 flex items-center gap-1">
              <span className="w-4 h-4 bg-purple-500 text-white rounded-full text-center text-xs leading-4">2</span>
              So What — 왜 중요한가
            </p>
            <p className="text-sm text-gray-700 leading-relaxed">{soWhat}</p>
          </div>

          {/* Now What — 어떻게 행동할까 */}
          <div>
            <p className="text-xs font-semibold text-gray-500 mb-1.5 flex items-center gap-1">
              <span className="w-4 h-4 bg-green-500 text-white rounded-full text-center text-xs leading-4">3</span>
              Now What — 어떻게 할까
            </p>
            <p className="text-sm text-gray-700 leading-relaxed">{nowWhat}</p>
          </div>

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
    const dGrade = importanceToGrade[d.importance] || 'C';
    if (grade !== '전체' && dGrade !== grade) return false;
    if (type !== '전체') {
      const dType = typeToFilter[d.disclosure_type];
      if (dType !== type) return false;
    }
    if (impact !== '전체' && d.ai_impact !== impact) return false;
    return true;
  });

  const grades: GradeFilter[] = ['전체', 'A', 'B', 'C', 'D'];
  const types: TypeFilter[] = ['전체', '실적', 'CB/BW', '자사주', '풍문', '수주', '증자', '기타'];
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
          const dGrade = importanceToGrade[d.importance] || 'C';
          const ic = impactColor[d.ai_impact] || impactColor['중립'];
          return (
            <div
              key={d.id}
              className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden cursor-pointer active:bg-gray-50 transition-colors"
              onClick={() => setModal(d)}
            >
              <div className="p-4">
                {/* 뱃지 행 */}
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2 py-0.5 rounded text-xs font-bold border ${gradeColor[dGrade] || gradeColor['C']}`}>
                    {dGrade}
                  </span>
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border ${ic.bg} ${ic.text} ${ic.border}`}>
                    {d.ai_impact}
                  </span>
                  <span className="text-xs text-gray-400 bg-gray-50 px-2 py-0.5 rounded">{d.disclosure_type}</span>
                </div>

                {/* 제목 */}
                <h3 className="font-semibold text-gray-900 text-sm leading-snug">{d.report_nm}</h3>
                <p className="text-xs text-gray-500 mt-1">{d.corp_name} · {d.rcept_dt}</p>

                {/* 요약 (2줄) */}
                <p className="text-sm text-gray-700 mt-2 leading-relaxed line-clamp-2">
                  {d.ai_summary}
                </p>

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
