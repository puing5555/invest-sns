'use client';

import type { NotificationSettings } from '@/data/notificationData';

interface NotificationSettingsProps {
  isOpen: boolean;
  onClose: () => void;
  settings: NotificationSettings;
  onSettingsChange: (settings: NotificationSettings) => void;
}

const settingLabels = [
  { key: 'a급공시' as keyof NotificationSettings, label: 'A등급 공시 알림' },
  { key: 'b급공시' as keyof NotificationSettings, label: 'B등급 공시 알림' },
  { key: '인플루언서콜' as keyof NotificationSettings, label: '인플루언서 콜 알림' },
  { key: '애널리스트목표가' as keyof NotificationSettings, label: '애널리스트 목표가 변동' },
  { key: '임원매매' as keyof NotificationSettings, label: '임원/대주주 매매' },
  { key: '가격알림' as keyof NotificationSettings, label: '가격 알림' },
  { key: 'ai시그널' as keyof NotificationSettings, label: 'AI 시그널 (70점+)' },
  { key: '수급감지' as keyof NotificationSettings, label: '수급 이상 감지' },
];

export default function NotificationSettings({ 
  isOpen, 
  onClose, 
  settings, 
  onSettingsChange 
}: NotificationSettingsProps) {
  if (!isOpen) return null;

  const handleToggle = (key: keyof NotificationSettings) => {
    onSettingsChange({
      ...settings,
      [key]: !settings[key]
    });
  };

  const handleSave = () => {
    // In a real app, this would save to backend
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Dark overlay */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50" 
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">알림 설정</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Settings List */}
        <div className="p-6 space-y-4">
          {settingLabels.map(({ key, label }) => (
            <div key={key} className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-900">{label}</span>
              <button
                onClick={() => handleToggle(key)}
                className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-[#3182f6] focus:ring-offset-2 ${
                  settings[key] ? 'bg-[#3182f6]' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    settings[key] ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200">
          <button
            onClick={handleSave}
            className="w-full bg-[#3182f6] text-white py-3 px-4 rounded-lg font-medium hover:bg-[#00c49a] transition-colors"
          >
            저장
          </button>
        </div>
      </div>
    </div>
  );
}