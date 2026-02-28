'use client';

import { useState } from 'react';
import { Analyst, opinionColors, opinionLabels } from '@/data/analystData';

interface Props {
  analyst: Analyst;
}

export default function AnalystProfileClient({ analyst }: Props) {
  const [activeTab, setActiveTab] = useState('overview');

  const formatPrice = (price: number) => price.toLocaleString() + '원';
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ko-KR', {
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const successRate = analyst.totalReports > 0 ? analyst.successfulPredictions / analyst.totalReports * 100 : 0;
  const completedPerformance = analyst.recentPerformance.filter(p => p.status !== '진행중');
  const avgReturnFromPerformance = completedPerformance.length > 0 
    ? completedPerformance.reduce((sum, p) => sum + p.returnRate, 0) / completedPerformance.length 
    : 0;

  return (
    <div className="bg-[#f8f9fa] min-h-screen">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-start space-x-6">
            <div className="w-24 h-24 bg-gradient-to-br from-green-500 to-blue-600 rounded-full flex items-center justify-center text-white text-3xl font-bold">
              {analyst.name.charAt(0)}
            </div>
            
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <h1 className="text-2xl font-bold text-gray-900">{analyst.name}</h1>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                  {analyst.company}
                </span>
              </div>
              
              <div className="flex items-center space-x-4 text-sm text-gray-600 mb-4">
                <span className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                  {analyst.sector} 전문
                </span>
                <span>경력 {analyst.experienceYears}년</span>
              </div>
              
              <div className="grid grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{analyst.accuracyRate}%</div>
                  <div className="text-sm text-gray-500">적중률</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{analyst.totalReports}</div>
                  <div className="text-sm text-gray-500">총 리포트</div>
                </div>
                <div className="text-center">
                  <div className={`text-2xl font-bold ${analyst.avgReturn > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {analyst.avgReturn > 0 ? '+' : ''}{analyst.avgReturn.toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-500">평균 수익률</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{analyst.successfulPredictions}</div>
                  <div className="text-sm text-gray-500">성공 예측</div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Tabs */}
          <div className="flex space-x-8 mt-8 -mb-px">
            {[
              { id: 'overview', label: '개요', count: null },
              { id: 'reports', label: '최신 리포트', count: analyst.recentReports.length },
              { id: 'performance', label: '투자 성과', count: analyst.recentPerformance.length }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label} {tab.count !== null && (
                  <span className="text-xs bg-gray-100 px-2 py-1 rounded-full ml-1">{tab.count}</span>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* 전문 분야 */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <h3 className="text-lg font-bold text-gray-900 mb-4">전문 분야</h3>
              <div className="flex items-center space-x-4">
                <span className="px-4 py-2 bg-blue-50 text-blue-700 rounded-lg font-medium">
                  {analyst.sector}
                </span>
                <span className="text-sm text-gray-600">{analyst.company} 소속</span>
                <span className="text-sm text-gray-600">{analyst.experienceYears}년 경력</span>
              </div>
            </div>

            {/* 성과 요약 */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <h3 className="text-lg font-bold text-gray-900 mb-6">성과 요약</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-3xl font-bold text-green-600 mb-1">{analyst.accuracyRate}%</div>
                  <div className="text-sm text-gray-600">적중률</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {analyst.successfulPredictions}/{analyst.totalReports} 성공
                  </div>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className={`text-3xl font-bold mb-1 ${analyst.avgReturn > 0 ? 'text-blue-600' : 'text-red-600'}`}>
                    {analyst.avgReturn > 0 ? '+' : ''}{analyst.avgReturn.toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">평균 수익률</div>
                  <div className="text-xs text-gray-500 mt-1">
                    리포트 기반 예상 수익률
                  </div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-3xl font-bold text-gray-900 mb-1">{analyst.totalReports}</div>
                  <div className="text-sm text-gray-600">발행 리포트</div>
                  <div className="text-xs text-gray-500 mt-1">
                    최근 12개월 기준
                  </div>
                </div>
              </div>
            </div>

            {/* 최근 활동 */}
            {analyst.recentReports.length > 0 && (
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                <h3 className="text-lg font-bold text-gray-900 mb-4">최근 활동</h3>
                <div className="space-y-4">
                  {analyst.recentReports.slice(0, 3).map((report) => (
                    <div key={report.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium text-gray-900 mb-1">{report.title}</div>
                        <div className="text-sm text-gray-500">
                          목표가 {formatPrice(report.targetPrice)} · {formatDate(report.publishedAt)}
                        </div>
                      </div>
                      <div className={`px-3 py-1 rounded-full text-xs font-medium ${opinionColors[report.investmentOpinion]}`}>
                        {opinionLabels[report.investmentOpinion]}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'reports' && (
          <div className="space-y-6">
            {analyst.recentReports.map((report) => (
              <div key={report.id} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className={`px-3 py-1 rounded-full text-xs font-medium ${opinionColors[report.investmentOpinion]}`}>
                        {opinionLabels[report.investmentOpinion]}
                      </div>
                      <span className="text-sm text-gray-500">
                        {formatDate(report.publishedAt)}
                      </span>
                    </div>
                    
                    <h3 className="text-lg font-bold text-gray-900 mb-2">{report.title}</h3>
                    <p className="text-gray-600 text-sm mb-4">{report.summary}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-6 text-sm mb-4">
                  <div>
                    <span className="text-gray-500">목표가: </span>
                    <span className="font-medium">{formatPrice(report.targetPrice)}</span>
                    {report.previousTargetPrice && (
                      <span className="text-xs text-green-600 ml-1">
                        (↑{formatPrice(report.targetPrice - report.previousTargetPrice)})
                      </span>
                    )}
                  </div>
                  <div>
                    <span className="text-gray-500">현재가: </span>
                    <span className="font-medium">{formatPrice(report.currentPrice)}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">상승여력: </span>
                    <span className={`font-medium ${report.upsidePotential > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {report.upsidePotential > 0 ? '+' : ''}{report.upsidePotential.toFixed(1)}%
                    </span>
                  </div>
                </div>
                
                {report.keyPoints && report.keyPoints.length > 0 && (
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-2">핵심 포인트:</div>
                    <div className="flex flex-wrap gap-2">
                      {report.keyPoints.map((point, index) => (
                        <span key={index} className="text-sm bg-blue-50 text-blue-700 px-3 py-1 rounded-full">
                          {point}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {activeTab === 'performance' && (
          <div className="space-y-6">
            {analyst.recentPerformance.length > 0 ? (
              <>
                {/* 성과 요약 */}
                <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">투자 성과 요약</h3>
                  <div className="grid grid-cols-3 gap-6 text-center">
                    <div>
                      <div className={`text-2xl font-bold ${avgReturnFromPerformance > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {avgReturnFromPerformance > 0 ? '+' : ''}{avgReturnFromPerformance.toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-500">평균 수익률</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-gray-900">{completedPerformance.length}</div>
                      <div className="text-sm text-gray-500">완료된 투자</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-green-600">
                        {completedPerformance.filter(p => p.hitTarget).length}
                      </div>
                      <div className="text-sm text-gray-500">목표가 달성</div>
                    </div>
                  </div>
                </div>

                {/* 개별 성과 */}
                <div className="space-y-4">
                  {analyst.recentPerformance.map((performance, index) => (
                    <div key={index} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-bold text-gray-900">{performance.stock}</h4>
                        <div className="flex items-center space-x-2">
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                            performance.status === '목표달성' ? 'bg-green-100 text-green-800' :
                            performance.status === '손절' ? 'bg-red-100 text-red-800' :
                            performance.status === '진행중' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {performance.status}
                          </span>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">진입가: </span>
                          <span className="font-medium">{formatPrice(performance.entryPrice)}</span>
                        </div>
                        {performance.exitPrice && (
                          <div>
                            <span className="text-gray-500">청산가: </span>
                            <span className="font-medium">{formatPrice(performance.exitPrice)}</span>
                          </div>
                        )}
                        <div>
                          <span className="text-gray-500">수익률: </span>
                          <span className={`font-medium ${performance.returnRate > 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {performance.returnRate > 0 ? '+' : ''}{performance.returnRate.toFixed(1)}%
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-500">기간: </span>
                          <span className="font-medium">
                            {performance.daysToTarget ? `${performance.daysToTarget}일` : '진행중'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="bg-white rounded-xl p-12 shadow-sm border border-gray-100 text-center">
                <div className="text-gray-500 mb-2">📊</div>
                <p className="text-gray-600">투자 성과 데이터가 준비 중입니다.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}