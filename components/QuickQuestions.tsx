'use client';

interface QuickQuestionsProps {
  onQuestionClick: (question: string) => void;
}

const questions = [
  "?“Š ?¤ëŠ˜ ë­?ë´ì•¼ ??",
  "?“‹ ??ê´€?¬ì¢…ëª?ê³µì‹œ ?”ì•½", 
  "?¯ ?¼ì„±?„ì ? ë„ë¦¬ìŠ¤???˜ê²¬ ?•ë¦¬",
  "?’¡ ?”ì¦˜ ?´ë–¤ ?¹í„°ê°€ ì¢‹ì•„?"
];

export default function QuickQuestions({ onQuestionClick }: QuickQuestionsProps) {
  return (
    <div className="grid grid-cols-2 gap-2 mt-3">
      {questions.map((question, index) => (
        <button
          key={index}
          onClick={() => onQuestionClick(question)}
          className="p-3 text-sm bg-white border border-gray-200 rounded-2xl hover:bg-[#f2f4f6] hover:border-[#3182f6] transition-all duration-200 text-left"
        >
          {question}
        </button>
      ))}
    </div>
  );
}