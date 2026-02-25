'use client';

import { useState, useRef, useEffect } from 'react';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import InvestDNA from '@/components/InvestDNA';
import QuickQuestions from '@/components/QuickQuestions';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp?: string;
  showQuickQuestions?: boolean;
}

const initialMessages: Message[] = [
  {
    id: 1,
    text: "안녕하세요! 투자 AI 비서입니다.",
    isUser: false,
    showQuickQuestions: true,
    timestamp: "14:20"
  },
  {
    id: 2,
    text: "오늘 뭐 봐야 해?",
    isUser: true,
    timestamp: "14:22"
  },
  {
    id: 3,
    text: "오늘 체크할 거 3가지 정리했어요.\n\n1. **에코프로** — 외국인 3일 연속 순매수 전환 📈\n지난번 메모에 '25만 밑이면 분할매수' 적어두셨는데 지금 24.8만이에요.\n\n2. **아이빔테크놀로지** — 오늘 공급계약 공시 (A등급) 📋\n161억 규모, 매출대비 33%. 과거 유사 패턴 평균 +8.2%.\n\n3. **삼성전자** 주총 D-23 📅\n캘린더에 등록해두셨는데, 주총 안건 나오면 바로 알려드릴게요.\n\n추가로 궁금한 종목 있으면 말씀하세요!",
    isUser: false,
    timestamp: "14:22"
  },
  {
    id: 4,
    text: "에코프로 좀 더 분석해줘",
    isUser: true,
    timestamp: "14:25"
  },
  {
    id: 5,
    text: "에코프로 현재 상황 정리해드릴게요.\n\n📊 **현재가: 248,000원 (+3.2%)**\n🔥 **시그널 스코어: 87/100**\n- 인플루언서 3명 동시 콜 (+45)\n- 기관 순매수 3일 연속 (+20)\n- 거래량 전일대비 +180% (+12)\n- 뉴스 센티먼트 긍정 (+10)\n\n🎯 **애널리스트 컨센서스**\n- 매수 8 | 보유 3 | 매도 1\n- 평균 목표가: 310,000원 (괴리율 +25%)\n- 최근 상향: 한투 김OO (적중률 68% ★★★★)\n\n👤 **인플루언서 동향**\n- 코린이아빠: '25만 밑 분할매수' (02/20)\n- 주식하는의사: '2차전지 바닥 확인' (02/22)\n- 텔레그램큰손: '단기 30만 간다' (02/24)\n\n📝 **내 메모 (02/18)**\n'25만 밑이면 1차 매수, 22만이면 2차 매수. 목표 32만.'\n\n어떻게 하실 건가요? 추가 분석이나 다른 종목도 볼까요?",
    isUser: false,
    timestamp: "14:25"
  }
];

export default function AIBotPage() {
  const [activeTab, setActiveTab] = useState<'chat' | 'dna'>('chat');
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const chatRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (text: string) => {
    const newMessage: Message = {
      id: messages.length + 1,
      text,
      isUser: true,
      timestamp: new Date().toLocaleTimeString('ko-KR', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    };
    setMessages([...messages, newMessage]);
  };

  const handleQuickQuestion = (question: string) => {
    handleSendMessage(question);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b border-gray-200 z-10">
        <div className="p-6 text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-1">🤖 투자 AI 비서</h1>
          <p className="text-gray-600">당신의 투자를 누구보다 잘 아는 AI</p>
        </div>

        {/* Tabs */}
        <div className="flex border-t border-gray-100">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex-1 py-3 px-4 text-center font-medium transition-colors ${
              activeTab === 'chat'
                ? 'text-[#3182f6] border-b-2 border-[#3182f6] bg-green-50'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            💬 채팅
          </button>
          <button
            onClick={() => setActiveTab('dna')}
            className={`flex-1 py-3 px-4 text-center font-medium transition-colors ${
              activeTab === 'dna'
                ? 'text-[#3182f6] border-b-2 border-[#3182f6] bg-green-50'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            🧠 내 투자 DNA
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'chat' ? (
          <>
            {/* Chat Messages */}
            <div 
              ref={chatRef}
              className="flex-1 overflow-y-auto p-4 pb-6"
              style={{ height: 'calc(100vh - 200px)' }}
            >
              {messages.map((message) => (
                <div key={message.id}>
                  <ChatMessage
                    message={message.text}
                    isUser={message.isUser}
                    timestamp={message.timestamp}
                  />
                  {message.showQuickQuestions && !message.isUser && (
                    <div className="ml-11 mb-4">
                      <QuickQuestions onQuestionClick={handleQuickQuestion} />
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Chat Input */}
            <ChatInput onSend={handleSendMessage} />
          </>
        ) : (
          <div className="flex-1 overflow-y-auto bg-gray-50">
            <InvestDNA />
          </div>
        )}
      </div>
    </div>
  );
}