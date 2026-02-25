import React from 'react';
import { profileData } from '@/data/profileData';

const ProfileHeader = () => {
  return (
    <div className="relative">
      {/* Gradient background */}
      <div 
        className="h-32 w-full"
        style={{
          background: 'linear-gradient(135deg, #3182f6, #00b4d8)',
        }}
      />
      
      {/* White card overlapping the gradient */}
      <div className="relative -mt-8 mx-4">
        <div className="bg-white rounded-2xl shadow-lg p-6">
          {/* Avatar and basic info */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gray-300 rounded-full flex items-center justify-center text-2xl font-bold text-gray-600">
                ??              </div>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h1 className="text-xl font-bold">{profileData.nickname}</h1>
                  <button className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-[#f2f4f6]">
                    ?òÏ†ï
                  </button>
                </div>
                <p className="text-[#8b95a1] text-sm">Í∞Ä?ÖÏùº: {profileData.joinDate}</p>
              </div>
            </div>
          </div>
          
          {/* Bio */}
          <div className="flex items-center gap-2 mb-4">
            <p className="text-gray-700">{profileData.bio}</p>
            <button className="px-2 py-1 text-xs border border-gray-300 rounded hover:bg-[#f2f4f6]">
              ?òÏ†ï
            </button>
          </div>
          
          {/* Stats */}
          <div className="flex gap-6 text-center">
            <div>
              <div className="font-bold text-lg">{profileData.followers}</div>
              <div className="text-[#8b95a1] text-sm">?îÎ°ú??/div>
            </div>
            <div className="border-l border-gray-200 pl-6">
              <div className="font-bold text-lg">{profileData.following}</div>
              <div className="text-[#8b95a1] text-sm">?îÎ°ú??/div>
            </div>
            <div className="border-l border-gray-200 pl-6">
              <div className="font-bold text-lg">{profileData.calls}Í±?/div>
              <div className="text-[#8b95a1] text-sm">ÏΩ?/div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileHeader;