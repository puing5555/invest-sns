'use client';

import type { NotificationSettings } from '@/data/notificationData';

interface NotificationSettingsProps {
  isOpen: boolean;
  onClose: () => void;
  settings: NotificationSettings;
  onSettingsChange: (settings: NotificationSettings) => void;
}

const settingLabels = [
  { key: 'aê¸‰ê³µ?? as keyof NotificationSettings, label: 'A?±ê¸‰ ê³µì‹œ ?Œë¦¼' },
  { key: 'bê¸‰ê³µ?? as keyof NotificationSettings, label: 'B?±ê¸‰ ê³µì‹œ ?Œë¦¼' },
  { key: '?¸í”Œë£¨ì–¸?œì½œ' as keyof NotificationSettings, label: '?¸í”Œë£¨ì–¸??ì½??Œë¦¼' },
  { key: '? ë„ë¦¬ìŠ¤?¸ëª©?œê?' as keyof NotificationSettings, label: '? ë„ë¦¬ìŠ¤??ëª©í‘œê°€ ë³€?? },
  { key: '?„ì›ë§¤ë§¤' as keyof NotificationSettings, label: '?„ì›/?€ì£¼ì£¼ ë§¤ë§¤' },
  { key: 'ê°€ê²©ì•Œë¦? as keyof NotificationSettings, label: 'ê°€ê²??Œë¦¼' },
  { key: 'ai?œê·¸?? as keyof NotificationSettings, label: 'AI ?œê·¸??(70??)' },
  { key: '?˜ê¸‰ê°ì?' as keyof NotificationSettings, label: '?˜ê¸‰ ?´ìƒ ê°ì?' },
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
      <div className="relative bg-white rounded-2xl shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-[#191f28]">?Œë¦¼ ?¤ì •</h2>
          <button
            onClick={onClose}
            className="text-[#8b95a1] hover:text-gray-600 transition-colors"
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
              <span className="text-sm font-medium text-[#191f28]">{label}</span>
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
            className="w-full bg-[#3182f6] text-white py-3 px-4 rounded-2xl font-medium hover:bg-[#00c49a] transition-colors"
          >
            ?€??
          </button>
        </div>
      </div>
    </div>
  );
}