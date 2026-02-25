export default function AIJournalBanner() {
  return (
    <div className="bg-[#f0f4ff] border border-blue-200 rounded-2xl p-4 mb-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className="text-2xl">?¤–</span>
        <div>
          <p className="text-gray-800 font-medium">ë§¤ì¼ ??ë§ˆê° ??AIê°€ ?¬ì?¼ì?ë¥??ë™?¼ë¡œ ?ì„±?©ë‹ˆ??</p>
          <p className="text-blue-600 text-sm font-medium">PRO ê¸°ëŠ¥</p>
        </div>
      </div>
      <button className="bg-blue-600 text-white px-4 py-2 rounded-2xl font-medium hover:bg-blue-700 transition-colors">
        PRO ?…ê·¸?ˆì´??
      </button>
    </div>
  );
}