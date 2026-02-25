export default function AIJournalBanner() {
  return (
    <div className="bg-[#f0f4ff] border border-blue-200 rounded-lg p-4 mb-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className="text-2xl">🤖</span>
        <div>
          <p className="text-gray-800 font-medium">매일 장 마감 후 AI가 투자일지를 자동으로 생성합니다.</p>
          <p className="text-blue-600 text-sm font-medium">PRO 기능</p>
        </div>
      </div>
      <button className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors">
        PRO 업그레이드
      </button>
    </div>
  );
}