'use client';

export default function InvestDNA() {
  return (
    <div className="p-4 space-y-6">
      {/* Investment Style */}
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <div className="flex items-center mb-4">
          <span className="text-2xl mr-3">📈</span>
          <h3 className="text-lg font-semibold">투자 스타일</h3>
        </div>
        <div className="text-gray-700">
          <span className="font-medium text-[#00d4aa]">스윙 트레이더</span> (평균 보유 2~4주)
        </div>
      </div>

      {/* Preferred Sectors */}
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <div className="flex items-center mb-4">
          <span className="text-2xl mr-3">🏭</span>
          <h3 className="text-lg font-semibold">선호 섹터</h3>
        </div>
        <div className="space-y-3">
          <div className="flex items-center">
            <span className="w-16 text-sm text-gray-600">2차전지</span>
            <div className="flex-1 bg-gray-200 rounded-full h-2 mx-3">
              <div className="bg-[#00d4aa] h-2 rounded-full" style={{ width: '90%' }}></div>
            </div>
            <span className="text-sm font-medium">90%</span>
          </div>
          <div className="flex items-center">
            <span className="w-16 text-sm text-gray-600">반도체</span>
            <div className="flex-1 bg-gray-200 rounded-full h-2 mx-3">
              <div className="bg-[#00d4aa] h-2 rounded-full" style={{ width: '75%' }}></div>
            </div>
            <span className="text-sm font-medium">75%</span>
          </div>
          <div className="flex items-center">
            <span className="w-16 text-sm text-gray-600">방산</span>
            <div className="flex-1 bg-gray-200 rounded-full h-2 mx-3">
              <div className="bg-[#00d4aa] h-2 rounded-full" style={{ width: '60%' }}></div>
            </div>
            <span className="text-sm font-medium">60%</span>
          </div>
        </div>
      </div>

      {/* Risk Profile */}
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <div className="flex items-center mb-4">
          <span className="text-2xl mr-3">⚖️</span>
          <h3 className="text-lg font-semibold">리스크 성향</h3>
        </div>
        <div className="text-gray-700">
          <span className="font-medium text-orange-600">중간</span> (변동성 15~25% 종목 선호)
        </div>
      </div>

      {/* Trading Pattern */}
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <div className="flex items-center mb-4">
          <span className="text-2xl mr-3">🔄</span>
          <h3 className="text-lg font-semibold">매매 패턴</h3>
        </div>
        <div className="text-gray-700">
          공시 발생 시 진입, 수급 전환 시 청산
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Strengths */}
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <div className="flex items-center mb-4">
            <span className="text-2xl mr-3">💪</span>
            <h3 className="text-lg font-semibold">강점</h3>
          </div>
          <div className="bg-green-50 p-3 rounded-lg border border-green-200">
            <div className="text-sm text-green-800">
              <span className="font-medium">공급계약 공시 해석</span>
              <br />
              <span className="text-green-600">(관련 콜 적중률 78%)</span>
            </div>
          </div>
        </div>

        {/* Weaknesses */}
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <div className="flex items-center mb-4">
            <span className="text-2xl mr-3">⚠️</span>
            <h3 className="text-lg font-semibold">약점</h3>
          </div>
          <div className="bg-red-50 p-3 rounded-lg border border-red-200">
            <div className="text-sm text-red-800">
              <span className="font-medium">손절이 느림</span>
              <br />
              <span className="text-red-600">(평균 -12%에서 손절, 권장 -7%)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}