interface MemoFilterProps {
  activeFilter: string;
  onFilterChange: (filter: string) => void;
}

export default function MemoFilter({ activeFilter, onFilterChange }: MemoFilterProps) {
  const filters = [
    { id: 'all', label: '전체' },
    { id: 'by-stock', label: '종목별' },
    { id: '매수근거', label: '매수근거' },
    { id: '매도근거', label: '매도근거' },
    { id: 'AI일지', label: 'AI일지' }
  ];

  return (
    <div className="flex gap-2 mb-6 overflow-x-auto">
      {filters.map((filter) => (
        <button
          key={filter.id}
          onClick={() => onFilterChange(filter.id)}
          className={`px-4 py-2 rounded-full whitespace-nowrap transition-colors ${
            activeFilter === filter.id
              ? 'bg-[#3182f6] text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          {filter.label}
        </button>
      ))}
    </div>
  );
}