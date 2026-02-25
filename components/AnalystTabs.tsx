interface AnalystTabsProps {
  activeTab: 'reports' | 'analysts';
  onTabChange: (tab: 'reports' | 'analysts') => void;
}

export default function AnalystTabs({ activeTab, onTabChange }: AnalystTabsProps) {
  return (
    <div className="border-b border-gray-200 bg-white">
      <div className="flex">
        <button
          onClick={() => onTabChange('reports')}
          className={`flex-1 py-3 px-4 text-center font-medium border-b-2 transition-colors ${
            activeTab === 'reports'
              ? 'border-[#00d4aa] text-[#00d4aa]'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          📄 리포트
        </button>
        <button
          onClick={() => onTabChange('analysts')}
          className={`flex-1 py-3 px-4 text-center font-medium border-b-2 transition-colors ${
            activeTab === 'analysts'
              ? 'border-[#00d4aa] text-[#00d4aa]'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          🎯 애널리스트
        </button>
      </div>
    </div>
  );
}