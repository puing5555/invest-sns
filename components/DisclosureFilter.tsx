'use client';

interface DisclosureFilterProps {
  searchTerm: string;
  onSearchChange: (term: string) => void;
  grade: string;
  onGradeChange: (grade: string) => void;
  type: string;
  onTypeChange: (type: string) => void;
  sort: string;
  onSortChange: (sort: string) => void;
}

export default function DisclosureFilter({
  searchTerm,
  onSearchChange,
  grade,
  onGradeChange,
  type,
  onTypeChange,
  sort,
  onSortChange
}: DisclosureFilterProps) {
  const gradeOptions = ['전체', 'A등급', 'B등급', 'C등급'];
  const typeOptions = ['전체', '공급계약', '자사주', '지분변동', '배당', '해명', '실적', '기타'];
  const sortOptions = [
    { value: 'latest', label: '최신순' },
    { value: 'marketCap', label: '시총순' },
    { value: 'favorability', label: '호재비율순' }
  ];

  const getButtonClasses = (isSelected: boolean) => {
    return `px-3 py-1 text-sm rounded-md transition-colors ${
      isSelected
        ? 'bg-[#00d4aa] text-white'
        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
    }`;
  };

  return (
    <div className="bg-white border-b border-[#eff3f4] p-4 sticky top-0 z-10">
      {/* Search Bar */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="종목명 검색..."
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#00d4aa] focus:border-transparent"
        />
      </div>

      {/* Grade Filter */}
      <div className="mb-3">
        <div className="text-sm font-medium text-gray-700 mb-2">등급</div>
        <div className="flex gap-2 flex-wrap">
          {gradeOptions.map((option) => (
            <button
              key={option}
              onClick={() => onGradeChange(option)}
              className={getButtonClasses(grade === option)}
            >
              {option}
            </button>
          ))}
        </div>
      </div>

      {/* Type Filter */}
      <div className="mb-3">
        <div className="text-sm font-medium text-gray-700 mb-2">유형</div>
        <div className="flex gap-2 flex-wrap">
          {typeOptions.map((option) => (
            <button
              key={option}
              onClick={() => onTypeChange(option)}
              className={getButtonClasses(type === option)}
            >
              {option}
            </button>
          ))}
        </div>
      </div>

      {/* Sort Filter */}
      <div>
        <div className="text-sm font-medium text-gray-700 mb-2">정렬</div>
        <div className="flex gap-2 flex-wrap">
          {sortOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => onSortChange(option.value)}
              className={getButtonClasses(sort === option.value)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}