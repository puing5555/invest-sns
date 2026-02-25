'use client';

interface QuickQuestionsProps {
  onQuestionClick: (question: string) => void;
}

const questions = [
  "📊 오늘 뭐 봐야 해?",
  "📋 내 관심종목 공시 요약", 
  "🎯 삼성전자 애널리스트 의견 정리",
  "💡 요즘 어떤 섹터가 좋아?"
];

export default function QuickQuestions({ onQuestionClick }: QuickQuestionsProps) {
  return (
    <div className="grid grid-cols-2 gap-2 mt-3">
      {questions.map((question, index) => (
        <button
          key={index}
          onClick={() => onQuestionClick(question)}
          className="p-3 text-sm bg-white border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-[#00d4aa] transition-all duration-200 text-left"
        >
          {question}
        </button>
      ))}
    </div>
  );
}