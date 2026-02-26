'use client';

export default function EarningsPage() {
  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* Header */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-xl font-bold text-[#191f28]">📊 실적 센터</h1>
          <p className="text-sm text-[#8b95a1] mt-1">기업 실적과 컨센서스 비교 분석</p>
        </div>
      </div>

      {/* Coming Soon */}
      <div className="max-w-4xl mx-auto px-4 py-16">
        <div className="text-center">
          <div className="text-8xl mb-6">📊</div>
          <h2 className="text-2xl font-bold text-[#191f28] mb-4">실적 센터 준비중</h2>
          <p className="text-[#8b95a1] mb-8 max-w-md mx-auto">
            기업의 실적 발표와 컨센서스 비교, 예상 EPS 대비 실제 실적을 한눈에 볼 수 있는 기능을 준비하고 있습니다.
          </p>

          {/* Preview Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
            <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
              <div className="text-3xl mb-3">📈</div>
              <h3 className="font-bold text-[#191f28] mb-2">실적 캘린더</h3>
              <p className="text-sm text-[#8b95a1]">
                다가오는 실적 발표 일정과 시장 예상치를 미리 확인
              </p>
            </div>

            <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
              <div className="text-3xl mb-3">🎯</div>
              <h3 className="font-bold text-[#191f28] mb-2">컨센서스 분석</h3>
              <p className="text-sm text-[#8b95a1]">
                애널리스트들의 실적 예상치와 실제 발표 결과 비교
              </p>
            </div>

            <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
              <div className="text-3xl mb-3">💡</div>
              <h3 className="font-bold text-[#191f28] mb-2">서프라이즈 알림</h3>
              <p className="text-sm text-[#8b95a1]">
                시장 예상을 크게 웃도는 어닝 서프라이즈 즉시 알림
              </p>
            </div>
          </div>

          <div className="mt-12">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 max-w-md mx-auto">
              <h4 className="font-bold text-blue-800 mb-2">🚀 출시 예정</h4>
              <p className="text-blue-700 text-sm">
                2024년 3분기 중 베타 버전 공개 예정입니다.<br />
                관심 있으시면 알림을 받아보세요!
              </p>
              <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm">
                출시 알림 받기
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}