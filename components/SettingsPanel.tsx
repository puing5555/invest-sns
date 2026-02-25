import React, { useState } from 'react';

interface ToggleProps {
  enabled: boolean;
  onChange: (enabled: boolean) => void;
}

const Toggle: React.FC<ToggleProps> = ({ enabled, onChange }) => {
  return (
    <button
      onClick={() => onChange(!enabled)}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
        enabled ? 'bg-green-500' : 'bg-gray-300'
      }`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
          enabled ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  );
};

interface SettingItemProps {
  title: string;
  children: React.ReactNode;
}

const SettingItem: React.FC<SettingItemProps> = ({ title, children }) => {
  return (
    <div className="flex items-center justify-between py-3">
      <span className="text-gray-900">{title}</span>
      {children}
    </div>
  );
};

const SettingsPanel = () => {
  const [settings, setSettings] = useState({
    darkMode: false,
    notifications: true,
    emailNotifications: true,
    publicProfile: true,
    publicAccuracy: true,
  });

  const updateSetting = (key: keyof typeof settings) => (value: boolean) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="space-y-6">
      {/* Settings List */}
      <div className="bg-white rounded-lg border divide-y divide-gray-100">
        <div className="p-4">
          <SettingItem title="다크모드">
            <Toggle 
              enabled={settings.darkMode} 
              onChange={updateSetting('darkMode')} 
            />
          </SettingItem>
          
          <SettingItem title="알림 수신">
            <Toggle 
              enabled={settings.notifications} 
              onChange={updateSetting('notifications')} 
            />
          </SettingItem>
          
          <SettingItem title="텔레그램 연동">
            <button className="px-4 py-2 bg-blue-500 text-white rounded-md text-sm hover:bg-blue-600 transition-colors">
              연동하기
            </button>
          </SettingItem>
          
          <SettingItem title="이메일 알림">
            <Toggle 
              enabled={settings.emailNotifications} 
              onChange={updateSetting('emailNotifications')} 
            />
          </SettingItem>
          
          <SettingItem title="프로필 공개">
            <Toggle 
              enabled={settings.publicProfile} 
              onChange={updateSetting('publicProfile')} 
            />
          </SettingItem>
          
          <SettingItem title="콜 적중률 공개">
            <Toggle 
              enabled={settings.publicAccuracy} 
              onChange={updateSetting('publicAccuracy')} 
            />
          </SettingItem>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="space-y-3">
        <button className="w-full py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
          로그아웃
        </button>
        <button className="w-full py-3 text-gray-500 hover:text-gray-700 transition-colors">
          회원탈퇴
        </button>
      </div>
    </div>
  );
};

export default SettingsPanel;