'use client';

interface NotificationFilterProps {
  activeFilter: string;
  onChange: (filter: string) => void;
}

const filterOptions = [
  '전체',
  '공시',
  '인플루언서',
  '애널리스트',
  '임원매매',
  '가격'
];

export default function NotificationFilter({ activeFilter, onChange }: NotificationFilterProps) {
  return (
    <div className="bg-white border-b border-[#f0f0f0] p-4">
      <div className="flex space-x-2 overflow-x-auto scrollbar-hide">
        {filterOptions.map((filter) => (
          <button
            key={filter}
            onClick={() => onChange(filter)}
            className={`px-4 py-2 rounded-full whitespace-nowrap text-sm font-medium transition-colors ${
              activeFilter === filter
                ? 'bg-[#3182f6] text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {filter}
          </button>
        ))}
      </div>
    </div>
  );
}