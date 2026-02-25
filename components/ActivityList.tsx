import React from 'react';
import { activitiesData } from '@/data/profileData';

const ActivityList = () => {
  return (
    <div className="space-y-0">
      {activitiesData.map((activity, index) => (
        <div key={activity.id}>
          <div className="flex items-center justify-between p-4 hover:bg-[#f2f4f6] transition-colors">
            <div className="flex items-center gap-3">
              <span className="text-xl">{activity.icon}</span>
              <span className="text-[#191f28]">{activity.description}</span>
            </div>
            <span className="text-[#8b95a1] text-sm">{activity.timeAgo}</span>
          </div>
          {index < activitiesData.length - 1 && (
            <div className="border-t border-gray-100" />
          )}
        </div>
      ))}
    </div>
  );
};

export default ActivityList;