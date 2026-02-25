'use client';

import { useState } from 'react';
import { newsData, NewsData } from '../../data/newsData';
import NewsCard from '../../components/NewsCard';
import NewsFilter from '../../components/NewsFilter';
import NewsDetail from '../../components/NewsDetail';

export default function NewsPage() {
  const [activeFilter, setActiveFilter] = useState('all');
  const [selectedNews, setSelectedNews] = useState<NewsData | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);

  const handleNewsClick = (news: NewsData) => {
    setSelectedNews(news);
    setIsDetailOpen(true);
  };

  const handleCloseDetail = () => {
    setIsDetailOpen(false);
    setSelectedNews(null);
  };

  // Separate urgent and regular news
  const urgentNews = newsData.filter(news => news.urgent);
  const regularNews = newsData.filter(news => !news.urgent);

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            📰 뉴스
          </h1>
          <p className="text-gray-600">
            AI가 골라주는 투자 뉴스
          </p>
        </div>

        {/* Filter */}
        <NewsFilter
          activeFilter={activeFilter}
          onFilterChange={setActiveFilter}
        />

        {/* Urgent News Section */}
        {urgentNews.length > 0 && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <span className="mr-2">🔴</span>
              긴급 뉴스
            </h2>
            <div className="space-y-4">
              {urgentNews.map((news) => (
                <NewsCard
                  key={news.id}
                  news={news}
                  onClick={handleNewsClick}
                />
              ))}
            </div>
          </div>
        )}

        {/* Regular News Section */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            최신 뉴스
          </h2>
          <div className="space-y-4">
            {regularNews.map((news) => (
              <NewsCard
                key={news.id}
                news={news}
                onClick={handleNewsClick}
              />
            ))}
          </div>
        </div>

        {/* Load More Button */}
        <div className="text-center">
          <button className="px-6 py-3 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors">
            더 많은 뉴스 보기
          </button>
        </div>
      </div>

      {/* Detail Panel */}
      <NewsDetail
        news={selectedNews}
        isOpen={isDetailOpen}
        onClose={handleCloseDetail}
      />
    </div>
  );
}