'use client';

export default function InsiderPage() {
  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* Header */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-xl font-bold text-[#191f28]">💼 임원매매</h1>
          <p className="text-sm text-[#8b95a1] mt-1">임원 및 대주주 지분 변동 추적</p>
        </div>
      </div>

      {/* Coming Soon */}
      <div className="max-w-4xl mx-auto px-4 py-16">
        <div className="text-center">
          <div className="text-8xl mb-6">💼</div>
          <h2 className="text-2xl font-bold text-[#191f28] mb-4">임원매매 센터 준비중</h2>
          <p className="text-[#8b95a1] mb-8 max-w-md mx-auto">
            기업 임원과 대주주들의 지분 매매 현황을 실시간으로 추적하고 분석하는 기능을 개발하고 있습니다.
          </p>

          {/* Preview Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
            <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
              <div className="text-3xl mb-3">📊</div>
              <h3 className="font-bold text-[#191f28] mb-2">실시간 매매 현황</h3>
              <p className="text-sm text-[#8b95a1]">
                임원과 대주주의 지분 매매 내역을 DART 연동으로 실시간 업데이트
              </p>
            </div>

            <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
              <div className="text-3xl mb-3">🎯</div>
              <h3 className="font-bold text-[#191f28] mb-2">패턴 분석</h3>
              <p className="text-sm text-[#8b95a1]">
                임원 매매와 주가 움직임의 상관관계 분석 및 시그널 생성
              </p>
            </div>

            <div className="bg-white rounded-lg border border-[#e8e8e8] p-6">
              <div className="text-3xl mb-3">🔔</div>
              <h3 className="font-bold text-[#191f28] mb-2">대량 매매 알림</h3>
              <p className="text-sm text-[#8b95a1]">
                임계치 이상의 대량 매매 발생 시 즉시 푸시 알림
              </p>
            </div>
          </div>

          {/* Sample Data Preview */}
          <div className="mt-12 max-w-2xl mx-auto">
            <h3 className="text-lg font-bold text-[#191f28] mb-6">미리보기 (샘플 데이터)</h3>
            <div className="space-y-4">
              <div className="bg-white rounded-lg border border-[#e8e8e8] p-4 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                    <span className="text-red-600 text-sm">매도</span>
                  </div>
                  <div>
                    <div className="font-medium text-[#191f28]">삼성전자 김○○ 상무</div>
                    <div className="text-sm text-[#8b95a1]">15억원 규모 • 2시간 전</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-red-600">-2.3%</div>
                  <div className="text-xs text-[#8b95a1]">영향도: 중</div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-[#e8e8e8] p-4 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 text-sm">매수</span>
                  </div>
                  <div>
                    <div className="font-medium text-[#191f28]">현대차 박○○ 전무</div>
                    <div className="text-sm text-[#8b95a1]">8억원 규모 • 1일 전</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-blue-600">+1.8%</div>
                  <div className="text-xs text-[#8b95a1]">영향도: 중</div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-12">
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-6 max-w-md mx-auto">
              <h4 className="font-bold text-purple-800 mb-2">🚀 베타 테스트 모집</h4>
              <p className="text-purple-700 text-sm">
                2024년 4분기 중 베타 테스트를 시작할 예정입니다.<br />
                먼저 체험해보고 싶다면 신청해주세요!
              </p>
              <button className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm">
                베타 테스트 신청
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}