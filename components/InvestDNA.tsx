'use client';

export default function InvestDNA() {
  return (
    <div className="p-4 space-y-6">
      {/* Investment Style */}
      <div className="bg-white rounded-2xl p-6 shadow-[0_2px_8px_rgba(0,0,0,0.04)] border">
        <div className="flex items-center mb-4">
          <span className="text-2xl mr-3">?ìà</span>
          <h3 className="text-lg font-semibold">?¨Ïûê ?§Ì???/h3>
        </div>
        <div className="text-gray-700">
          <span className="font-medium text-[#3182f6]">?§Ïúô ?∏Î†à?¥Îçî</span> (?âÍ∑† Î≥¥Ïú† 2~4Ï£?
        </div>
      </div>

      {/* Preferred Sectors */}
      <div className="bg-white rounded-2xl p-6 shadow-[0_2px_8px_rgba(0,0,0,0.04)] border">
        <div className="flex items-center mb-4">
          <span className="text-2xl mr-3">?è≠</span>
          <h3 className="text-lg font-semibold">?†Ìò∏ ?πÌÑ∞</h3>
        </div>
        <div className="space-y-3">
          <div className="flex items-center">
            <span className="w-16 text-sm text-gray-600">2Ï∞®Ï†ÑÏßÄ</span>
            <div className="flex-1 bg-gray-200 rounded-full h-2 mx-3">
              <div className="bg-[#3182f6] h-2 rounded-full" style={{ width: '90%' }}></div>
            </div>
            <span className="text-sm font-medium">90%</span>
          </div>
          <div className="flex items-center">
            <span className="w-16 text-sm text-gray-600">Î∞òÎèÑÏ≤?/span>
            <div className="flex-1 bg-gray-200 rounded-full h-2 mx-3">
              <div className="bg-[#3182f6] h-2 rounded-full" style={{ width: '75%' }}></div>
            </div>
            <span className="text-sm font-medium">75%</span>
          </div>
          <div className="flex items-center">
            <span className="w-16 text-sm text-gray-600">Î∞©ÏÇ∞</span>
            <div className="flex-1 bg-gray-200 rounded-full h-2 mx-3">
              <div className="bg-[#3182f6] h-2 rounded-full" style={{ width: '60%' }}></div>
            </div>
            <span className="text-sm font-medium">60%</span>
          </div>
        </div>
      </div>

      {/* Risk Profile */}
      <div className="bg-white rounded-2xl p-6 shadow-[0_2px_8px_rgba(0,0,0,0.04)] border">
        <div className="flex items-center mb-4">
          <span className="text-2xl mr-3">?ñÔ∏è</span>
          <h3 className="text-lg font-semibold">Î¶¨Ïä§???±Ìñ•</h3>
        </div>
        <div className="text-gray-700">
          <span className="font-medium text-orange-600">Ï§ëÍ∞Ñ</span> (Î≥Ä?ôÏÑ± 15~25% Ï¢ÖÎ™© ?†Ìò∏)
        </div>
      </div>

      {/* Trading Pattern */}
      <div className="bg-white rounded-2xl p-6 shadow-[0_2px_8px_rgba(0,0,0,0.04)] border">
        <div className="flex items-center mb-4">
          <span className="text-2xl mr-3">?îÑ</span>
          <h3 className="text-lg font-semibold">Îß§Îß§ ?®ÌÑ¥</h3>
        </div>
        <div className="text-gray-700">
          Í≥µÏãú Î∞úÏÉù ??ÏßÑÏûÖ, ?òÍ∏â ?ÑÌôò ??Ï≤?Ç∞
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Strengths */}
        <div className="bg-white rounded-2xl p-6 shadow-[0_2px_8px_rgba(0,0,0,0.04)] border">
          <div className="flex items-center mb-4">
            <span className="text-2xl mr-3">?í™</span>
            <h3 className="text-lg font-semibold">Í∞ïÏ†ê</h3>
          </div>
          <div className="bg-green-50 p-3 rounded-2xl border border-green-200">
            <div className="text-sm text-green-800">
              <span className="font-medium">Í≥µÍ∏âÍ≥ÑÏïΩ Í≥µÏãú ?¥ÏÑù</span>
              <br />
              <span className="text-green-600">(Í¥Ä??ÏΩ??ÅÏ§ëÎ•?78%)</span>
            </div>
          </div>
        </div>

        {/* Weaknesses */}
        <div className="bg-white rounded-2xl p-6 shadow-[0_2px_8px_rgba(0,0,0,0.04)] border">
          <div className="flex items-center mb-4">
            <span className="text-2xl mr-3">?†Ô∏è</span>
            <h3 className="text-lg font-semibold">?ΩÏ†ê</h3>
          </div>
          <div className="bg-red-50 p-3 rounded-2xl border border-red-200">
            <div className="text-sm text-red-800">
              <span className="font-medium">?êÏ†à???êÎ¶º</span>
              <br />
              <span className="text-red-600">(?âÍ∑† -12%?êÏÑú ?êÏ†à, Í∂åÏû• -7%)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}