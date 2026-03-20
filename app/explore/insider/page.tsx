'use client';

export default function InsiderPage() {
  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-xl font-bold text-[#191f28]">💼 임원/대주주</h1>
          <p className="text-sm text-[#8b95a1] mt-1">최근 내부자 매수 TOP + 대주주 지분 변동</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-16">
        <div className="text-center">
          <div className="text-8xl mb-6">💼</div>
          <h2 className="text-2xl font-bold text-[#191f28] mb-4">DART 연동 준비중</h2>
          <p className="text-[#8b95a1] max-w-md mx-auto">
            DART 지분공시 기반으로 임원/대주주 매매 현황과 내부자 매수 TOP을 제공할 예정입니다.
          </p>
        </div>
      </div>
    </div>
  );
}
