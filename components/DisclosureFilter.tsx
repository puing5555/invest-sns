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
  const gradeOptions = ['?„ì²´', 'A?±ê¸‰', 'B?±ê¸‰', 'C?±ê¸‰'];
  const typeOptions = ['?„ì²´', 'ê³µê¸‰ê³„ì•½', '?ì‚¬ì£?, 'ì§€ë¶„ë???, 'ë°°ë‹¹', '?´ëª…', '?¤ì ', 'ê¸°í?'];
  const sortOptions = [
    { value: 'latest', label: 'ìµœì‹ ?? },
    { value: 'marketCap', label: '?œì´?? },
    { value: 'favorability', label: '?¸ìž¬ë¹„ìœ¨?? }
  ];

  const getButtonClasses = (isSelected: boolean) => {
    return `px-3 py-1 text-sm rounded-md transition-colors ${
      isSelected
        ? 'bg-[#3182f6] text-white'
        : 'bg-[#f2f4f6] text-gray-600 hover:bg-gray-200'
    }`;
  };

  return (
    <div className="bg-white border-b border-[#f0f0f0] p-4 sticky top-0 z-10">
      {/* Search Bar */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="ì¢…ëª©ëª?ê²€??.."
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-[#3182f6] focus:border-transparent"
        />
      </div>

      {/* Grade Filter */}
      <div className="mb-3">
        <div className="text-sm font-medium text-gray-700 mb-2">?±ê¸‰</div>
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
        <div className="text-sm font-medium text-gray-700 mb-2">? í˜•</div>
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
        <div className="text-sm font-medium text-gray-700 mb-2">?•ë ¬</div>
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