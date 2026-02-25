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
          <h2 className="text-lg font-semibold text-[#191f28]">AI ?ÅÏÑ∏Î∂ÑÏÑù</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-[#f2f4f6] rounded-md transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-4 space-y-6">
          {/* Company Header */}
          <div>
            <h3 className="font-semibold text-[#191f28] mb-2">?ÑÏù¥ÎπîÌÖå?¨Î?Î°úÏ?</h3>
            <p className="text-sm text-gray-600">?®Ïùº?êÎß§¬∑Í≥µÍ∏âÍ≥ÑÏïΩ Ï≤¥Í≤∞</p>
          </div>

          {/* AI 3Ï§??îÏïΩ */}
          <div>
            <h4 className="font-medium text-[#191f28] mb-3">?§ñ AI 3Ï§??îÏïΩ</h4>
            <div className="space-y-2">
              <div className="flex items-start gap-2">
                <span className="text-[#3182f6] font-medium">1.</span>
                <span className="text-gray-700">Îß§Ï∂ú?ÄÎπ?14.77%Î°?A?±Í∏â Í∏∞Ï? Ï∂©Ï°±</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-[#3182f6] font-medium">2.</span>
                <span className="text-gray-700">Í≥ºÍ±∞ ?†ÏÇ¨ Í≥µÍ∏âÍ≥ÑÏïΩ 47Í±?Ï§?D+3 ?âÍ∑† +8.2%</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-[#3182f6] font-medium">3.</span>
                <span className="text-gray-700">?∏Íµ≠???úÎß§???ÑÌôòÍ≥??ôÏãú Î∞úÏÉù, ?úÎÑàÏßÄ Í∏∞Î?</span>
              </div>
            </div>
          </div>

          {/* ?µÏã¨ ?´Ïûê */}
          <div>
            <h4 className="font-medium text-[#191f28] mb-3">?ìä ?µÏã¨ ?´Ïûê</h4>
            <div className="bg-[#f2f4f6] rounded-2xl p-3">
              <table className="w-full text-sm">
                <tbody className="space-y-2">
                  <tr>
                    <td className="text-gray-600 py-1">Í≥ÑÏïΩÍ∏àÏï°</td>
                    <td className="text-right font-medium py-1">23.5??/td>
                  </tr>
                  <tr>
                    <td className="text-gray-600 py-1">Îß§Ï∂ú?ÄÎπ?/td>
                    <td className="text-right font-medium py-1">14.77%</td>
                  </tr>
                  <tr>
                    <td className="text-gray-600 py-1">?úÏ¥ù?ÄÎπ?/td>
                    <td className="text-right font-medium py-1">2.39%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Í≥ºÍ±∞ ?†ÏÇ¨ ?®ÌÑ¥ */}
          <div>
            <h4 className="font-medium text-[#191f28] mb-3">?ìà Í≥ºÍ±∞ ?†ÏÇ¨ ?®ÌÑ¥</h4>
            <div className="bg-[#f2f4f6] rounded-2xl p-3">
              <table className="w-full text-sm">
                <tbody>
                  <tr>
                    <td className="text-gray-600 py-1">ÏºÄ?¥Ïä§</td>
                    <td className="text-right font-medium py-1">47Í±?/td>
                  </tr>
                  <tr>
                    <td className="text-gray-600 py-1">?âÍ∑†?òÏùµÎ•?/td>
                    <td className="text-right font-medium py-1 text-green-600">+8.2%</td>
                  </tr>
                  <tr>
                    <td className="text-gray-600 py-1">?πÎ•†</td>
                    <td className="text-right font-medium py-1">72%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* ÏßÑÏûÖ ?Ä?¥Î∞ç */}
          <div>
            <h4 className="font-medium text-[#191f28] mb-3">??ÏßÑÏûÖ ?Ä?¥Î∞ç</h4>
            <div className="bg-[#f2f4f6] rounded-2xl p-3">
              <table className="w-full text-sm">
                <tbody>
                  <tr>
                    <td className="text-gray-600 py-1">?πÏùº</td>
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

          {/* Í¥Ä???∏ÌîåÎ£®Ïñ∏??*/}
          <div>
            <h4 className="font-medium text-[#191f28] mb-3">?ë• Í¥Ä???∏ÌîåÎ£®Ïñ∏??/h4>
            <div className="bg-blue-50 rounded-2xl p-3">
              <div className="flex items-center gap-2">
                <span className="font-medium text-blue-900">ÏΩîÎ¶∞?¥ÏïÑÎπ?/span>
                <span className="text-blue-700">&quot;Ï£ºÎ™©?†Îßå&quot;</span>
              </div>
            </div>
          </div>

          {/* Í¥Ä???†ÎÑê */}
          <div>
            <h4 className="font-medium text-[#191f28] mb-3">?ìã Í¥Ä???†ÎÑê</h4>
            <div className="bg-[#f2f4f6] rounded-2xl p-3">
              <span className="text-[#8b95a1]">?¥Îãπ?ÜÏùå</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}