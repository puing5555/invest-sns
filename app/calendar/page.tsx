'use client';

import { useState } from 'react';

const upcomingEvents = [
  {
    id: 1,
    title: '삼성전자 3분기 실적발표',
    date: '2024-10-31',
    time: '16:00',
    type: 'earnings',
    importance: 'high',
  },
  {
    id: 2,
    title: 'SK하이닉스 임시주주총회',
    date: '2024-11-05',
    time: '14:00',
    type: 'meeting',
    importance: 'medium',
  },
  {
    id: 3,
    title: 'NAVER IR Day',
    date: '2024-11-12',
    time: '10:00',
    type: 'ir',
    importance: 'high',
  },
  {
    id: 4,
    title: '현대차 신차 발표회',
    date: '2024-11-15',
    time: '15:30',
    type: 'event',
    importance: 'medium',
  },
  {
    id: 5,
    title: 'LG에너지 배당 기준일',
    date: '2024-11-20',
    time: '종일',
    type: 'dividend',
    importance: 'low',
  },
];

const eventTypes = {
  earnings: { icon: '📊', label: '실적발표', color: 'bg-blue-100 text-blue-700' },
  meeting: { icon: '🏢', label: '주주총회', color: 'bg-green-100 text-green-700' },
  ir: { icon: '📈', label: 'IR행사', color: 'bg-purple-100 text-purple-700' },
  event: { icon: '🎉', label: '기업행사', color: 'bg-orange-100 text-orange-700' },
  dividend: { icon: '💰', label: '배당', color: 'bg-yellow-100 text-yellow-700' },
};

const importanceColors = {
  high: 'border-l-red-500',
  medium: 'border-l-orange-500',
  low: 'border-l-gray-400',
};

export default function CalendarPage() {
  const [selectedDate, setSelectedDate] = useState<string | null>(null);

  // 현재 월의 날짜들을 생성하는 간단한 함수
  const generateCalendarDays = () => {
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());

    const days = [];
    const current = new Date(startDate);

    for (let i = 0; i < 42; i++) {
      days.push(new Date(current));
      current.setDate(current.getDate() + 1);
    }

    return days;
  };

  const calendarDays = generateCalendarDays();
  const today = new Date();

  const getEventsForDate = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    return upcomingEvents.filter(event => event.date === dateStr);
  };

  return (
    <div className="min-h-screen bg-[#f4f4f4]">
      {/* Header */}
      <div className="bg-white border-b border-[#e8e8e8] px-4 py-4">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-xl font-bold text-[#191f28]">📅 캘린더</h1>
          <p className="text-sm text-[#8b95a1] mt-1">중요한 기업 일정과 이벤트</p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Calendar Grid */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
              {/* Calendar Header */}
              <div className="px-6 py-4 border-b border-[#e8e8e8]">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-bold text-[#191f28]">
                    {today.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' })}
                  </h2>
                  <div className="flex gap-2">
                    <button className="px-3 py-1 text-sm text-[#8b95a1] hover:text-[#191f28] transition-colors">
                      ‹ 이전
                    </button>
                    <button className="px-3 py-1 text-sm text-[#8b95a1] hover:text-[#191f28] transition-colors">
                      다음 ›
                    </button>
                  </div>
                </div>
              </div>

              {/* Calendar Days Header */}
              <div className="grid grid-cols-7 border-b border-[#e8e8e8]">
                {['일', '월', '화', '수', '목', '금', '토'].map((day, index) => (
                  <div
                    key={index}
                    className="p-3 text-center text-sm font-medium text-[#8b95a1] bg-[#f8f9fa]"
                  >
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar Grid */}
              <div className="grid grid-cols-7">
                {calendarDays.map((date, index) => {
                  const events = getEventsForDate(date);
                  const isToday = date.toDateString() === today.toDateString();
                  const isCurrentMonth = date.getMonth() === today.getMonth();

                  return (
                    <div
                      key={index}
                      className={`min-h-[80px] p-2 border-b border-r border-[#f0f0f0] relative ${
                        !isCurrentMonth ? 'bg-[#f8f9fa] text-[#ccc]' : 'hover:bg-[#f8f9fa]'
                      } ${isToday ? 'bg-blue-50' : ''}`}
                    >
                      <div className={`text-sm font-medium ${isToday ? 'text-blue-600' : ''}`}>
                        {date.getDate()}
                      </div>
                      
                      {events.map((event, eventIndex) => (
                        <div
                          key={eventIndex}
                          className={`mt-1 px-1 py-0.5 text-xs rounded text-white overflow-hidden ${
                            event.importance === 'high' ? 'bg-red-500' :
                            event.importance === 'medium' ? 'bg-orange-500' : 'bg-gray-400'
                          }`}
                          title={event.title}
                        >
                          {event.title.length > 8 ? event.title.substring(0, 8) + '...' : event.title}
                        </div>
                      ))}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Upcoming Events */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg border border-[#e8e8e8] overflow-hidden">
              <div className="px-4 py-3 border-b border-[#e8e8e8]">
                <h3 className="font-bold text-[#191f28]">다가오는 일정</h3>
              </div>
              <div className="divide-y divide-[#f0f0f0]">
                {upcomingEvents.slice(0, 5).map((event) => {
                  const eventType = eventTypes[event.type as keyof typeof eventTypes];
                  return (
                    <div
                      key={event.id}
                      className={`p-4 border-l-4 ${importanceColors[event.importance as keyof typeof importanceColors]} hover:bg-[#f8f9fa] transition-colors cursor-pointer`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${eventType.color}`}>
                              <span className="mr-1">{eventType.icon}</span>
                              {eventType.label}
                            </span>
                          </div>
                          <h4 className="font-semibold text-[#191f28] mb-1">{event.title}</h4>
                          <div className="text-sm text-[#8b95a1]">
                            {event.date} • {event.time}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Event Types Legend */}
            <div className="bg-white rounded-lg border border-[#e8e8e8] p-4">
              <h3 className="font-bold text-[#191f28] mb-3">일정 유형</h3>
              <div className="space-y-2">
                {Object.entries(eventTypes).map(([key, type]) => (
                  <div key={key} className="flex items-center gap-2">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${type.color}`}>
                      <span className="mr-1">{type.icon}</span>
                      {type.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Placeholder for Future Features */}
            <div className="bg-white rounded-lg border border-[#e8e8e8] p-4">
              <h3 className="font-bold text-[#191f28] mb-3">🚀 준비중인 기능</h3>
              <div className="space-y-2 text-sm text-[#8b95a1]">
                <div>• 개인 일정 추가</div>
                <div>• 알림 설정</div>
                <div>• 구글 캘린더 연동</div>
                <div>• 실적 발표 자동 추가</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}