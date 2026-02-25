'use client';

import { useState } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
}

export default function ChatInput({ onSend }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onSend(message.trim());
      setMessage('');
    }
  };

  return (
    <div className="sticky bottom-0 bg-white border-t border-gray-200 p-4">
      {/* Action icons */}
      <div className="flex space-x-4 mb-3 text-gray-400">
        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <span className="text-lg">📎</span>
        </button>
        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <span className="text-lg">📊</span>
        </button>
        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <span className="text-lg">🎤</span>
        </button>
      </div>

      {/* Input form */}
      <form onSubmit={handleSubmit} className="flex space-x-3">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="종목명, 질문, 뭐든 물어보세요..."
          className="flex-1 p-3 border border-gray-300 rounded-full focus:outline-none focus:border-[#00d4aa] focus:ring-1 focus:ring-[#00d4aa]"
        />
        <button
          type="submit"
          disabled={!message.trim()}
          className="w-12 h-12 bg-[#00d4aa] text-white rounded-full flex items-center justify-center hover:bg-[#00b88f] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </form>
    </div>
  );
}