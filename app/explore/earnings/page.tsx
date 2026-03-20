'use client';

export default function EarningsPage() {
  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-xl font-bold text-[#191f28]">📊 실적 센터</h1>
          <p className="text-sm text-[#8b95a1] mt-1">어닝 서프라이즈/쇼크 + 발표 예정</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-16">
        <div className="text-center">
          <div className="text-8xl mb-6">📊</div>
          <h2 className="text-2xl font-bold text-[#191f28] mb-4">DART 연동 준비중</h2>
          <p className="text-[#8b95a1] max-w-md mx-auto">
            DART 정기공시 기반으로 어닝 서프라이즈/쇼크와 실적 발표 일정을 제공할 예정입니다.
          </p>
        </div>
      </div>
    </div>
  );
}
