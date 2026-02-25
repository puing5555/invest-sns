'use client';

import React, { useState } from 'react';
import ProfileHeader from '@/components/ProfileHeader';
import ActivityList from '@/components/ActivityList';
import MyCallList from '@/components/MyCallList';
import SettingsPanel from '@/components/SettingsPanel';

type TabType = 'activity' | 'calls' | 'settings';

const ProfilePage = () => {
  const [activeTab, setActiveTab] = useState<TabType>('activity');

  const tabs = [
    { id: 'activity', label: '내 활동' },
    { id: 'calls', label: '내 콜' },
    { id: 'settings', label: '설정' },
  ] as const;

  const renderTabContent = () => {
    switch (activeTab) {
      case 'activity':
        return <ActivityList />;
      case 'calls':
        return <MyCallList />;
      case 'settings':
        return <SettingsPanel />;
      default:
        return <ActivityList />;
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Profile Header */}
      <ProfileHeader />
      
      {/* Tab Navigation */}
      <div className="px-4 mt-6">
        <div className="flex border-b border-gray-200">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              className={`flex-1 py-3 text-center font-medium relative transition-colors ${
                activeTab === tab.id
                  ? 'text-gray-900'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
              {activeTab === tab.id && (
                <div 
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#00d4aa]"
                />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="px-4 py-6">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default ProfilePage;