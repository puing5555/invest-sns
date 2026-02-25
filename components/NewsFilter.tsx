interface NewsFilterProps {
  activeFilter: string;
  onFilterChange: (filter: string) => void;
}

export default function NewsFilter({ activeFilter, onFilterChange }: NewsFilterProps) {
  const filters = [
    { id: 'all', label: '?„ì²´' },
    { id: 'my-stocks', label: '??ê´€?¬ì¢…ëª? },
    { id: 'market', label: '?œìž¥?„ì²´' },
    { id: 'sector', label: '?¹í„°ë³? },
    { id: 'global', label: 'ê¸€ë¡œë²Œ' },
  ];

  return (
    <div className="flex gap-1 mb-6 p-1 bg-[#f2f4f6] rounded-2xl w-fit">
      {filters.map((filter) => (
        <button
          key={filter.id}
          onClick={() => onFilterChange(filter.id)}
          className={`px-4 py-2 rounded-2xl text-sm font-medium transition-colors ${
            activeFilter === filter.id
              ? 'bg-[#3182f6] text-white shadow-[0_2px_8px_rgba(0,0,0,0.04)]'
              : 'bg-[#f2f4f6] text-gray-600 hover:bg-gray-200'
          }`}
        >
          {filter.label}
        </button>
      ))}
    </div>
  );
}