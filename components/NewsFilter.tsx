interface NewsFilterProps {
  activeFilter: string;
  onFilterChange: (filter: string) => void;
}

export default function NewsFilter({ activeFilter, onFilterChange }: NewsFilterProps) {
  const filters = [
    { id: 'all', label: '전체' },
    { id: 'my-stocks', label: '내 관심종목' },
    { id: 'market', label: '시장전체' },
    { id: 'sector', label: '섹터별' },
    { id: 'global', label: '글로벌' },
  ];

  return (
    <div className="flex gap-1 mb-6 p-1 bg-gray-100 rounded-lg w-fit">
      {filters.map((filter) => (
        <button
          key={filter.id}
          onClick={() => onFilterChange(filter.id)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeFilter === filter.id
              ? 'bg-[#3182f6] text-white shadow-sm'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          {filter.label}
        </button>
      ))}
    </div>
  );
}