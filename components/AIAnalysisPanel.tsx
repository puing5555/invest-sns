'use client';

interface AIAnalysisPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AIAnalysisPanel({ isOpen, onClose }: AIAnalysisPanelProps) {
  if (!isOpen) return null;

  return (
    <>
      {/* Dark overlay */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />
      
      {/* Panel */}
      <div className="fixed right-0 top-0 h-full w-96 bg-white z-50 shadow-xl transform transition-transform duration-300 ease-in-out overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">AI 상세분석</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-md transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-4 space-y-6">
          {/* Company Header */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">아이빔테크놀로지</h3>
            <p className="text-sm text-gray-600">단일판매·공급계약 체결</p>
          </div>

          {/* AI 3줄 요약 */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3">🤖 AI 3줄 요약</h4>
            <div className="space-y-2">
              <div className="flex items-start gap-2">
                <span className="text-[#00d4aa] font-medium">1.</span>
                <span className="text-gray-700">매출대비 14.77%로 A등급 기준 충족</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-[#00d4aa] font-medium">2.</span>
                <span className="text-gray-700">과거 유사 공급계약 47건 중 D+3 평균 +8.2%</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-[#00d4aa] font-medium">3.</span>
                <span className="text-gray-700">외국인 순매수 전환과 동시 발생, 시너지 기대</span>
              </div>
            </div>
          </div>

          {/* 핵심 숫자 */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3">📊 핵심 숫자</h4>
            <div className="bg-gray-50 rounded-lg p-3">
              <table className="w-full text-sm">
                <tbody className="space-y-2">
                  <tr>
                    <td className="text-gray-600 py-1">계약금액</td>
                    <td className="text-right font-medium py-1">23.5억</td>
                  </tr>
                  <tr>
                    <td className="text-gray-600 py-1">매출대비</td>
                    <td className="text-right font-medium py-1">14.77%</td>
                  </tr>
                  <tr>
                    <td className="text-gray-600 py-1">시총대비</td>
                    <td className="text-right font-medium py-1">2.39%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* 과거 유사 패턴 */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3">📈 과거 유사 패턴</h4>
            <div className="bg-gray-50 rounded-lg p-3">
              <table className="w-full text-sm">
                <tbody>
                  <tr>
                    <td className="text-gray-600 py-1">케이스</td>
                    <td className="text-right font-medium py-1">47건</td>
                  </tr>
                  <tr>
                    <td className="text-gray-600 py-1">평균수익률</td>
                    <td className="text-right font-medium py-1 text-green-600">+8.2%</td>
                  </tr>
                  <tr>
                    <td className="text-gray-600 py-1">승률</td>
                    <td className="text-right font-medium py-1">72%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* 진입 타이밍 */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3">⏰ 진입 타이밍</h4>
            <div className="bg-gray-50 rounded-lg p-3">
              <table className="w-full text-sm">
                <tbody>
                  <tr>
                    <td className="text-gray-600 py-1">당일</td>
                    <td className="text-right font-medium py-1 text-green-600">+2.1%</td>
                  </tr>
                  <tr>
                    <td className="text-gray-600 py-1">D+2</td>
                    <td className="text-right font-medium py-1 text-green-600">+5.4%</td>
                  </tr>
                  <tr>
                    <td className="text-gray-600 py-1">D+3</td>
                    <td className="text-right font-medium py-1 text-green-600">+8.2%</td>
                  </tr>
                  <tr>
                    <td className="text-gray-600 py-1">D+5</td>
                    <td className="text-right font-medium py-1 text-green-600">+6.8%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* 관련 인플루언서 */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3">👥 관련 인플루언서</h4>
            <div className="bg-blue-50 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <span className="font-medium text-blue-900">코린이아빠</span>
                <span className="text-blue-700">&quot;주목할만&quot;</span>
              </div>
            </div>
          </div>

          {/* 관련 애널 */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3">📋 관련 애널</h4>
            <div className="bg-gray-50 rounded-lg p-3">
              <span className="text-gray-500">해당없음</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}