'use client';

import Link from 'next/link';
import { Notification } from '@/data/notificationData';

interface NotificationItemProps {
  notification: Notification;
  onMarkAsRead: (id: string) => void;
}

const getIconColor = (type: string) => {
  switch (type) {
    case '공시': return 'text-blue-500';
    case '?�플루언??: return 'text-purple-500';
    case '?�원매매': return 'text-orange-500';
    case '?�널리스??: return 'text-green-500';
    case '가�?: return 'text-red-500';
    case '?�급': return 'text-cyan-500';
    case 'AI?�그??: return 'text-yellow-500';
    default: return 'text-[#8b95a1]';
  }
};

export default function NotificationItem({ notification, onMarkAsRead }: NotificationItemProps) {
  const handleClick = () => {
    if (!notification.read) {
      onMarkAsRead(notification.id);
    }
  };

  return (
    <Link href={notification.link} onClick={handleClick}>
      <div className={`p-4 border-b border-[#f0f0f0] hover:bg-[#f2f4f6] transition-colors ${
        notification.read ? 'bg-white' : 'bg-[#f0faf5]'
      }`}>
        <div className="flex items-start space-x-3">
          {/* Unread indicator */}
          {!notification.read && (
            <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0">
              <span className="sr-only">??/span>
            </div>
          )}
          
          {/* Icon */}
          <div className={`text-lg flex-shrink-0 mt-1 ${getIconColor(notification.type)}`}>
            {notification.icon}
          </div>
          
          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-[#191f28]">
                    {notification.title}
                  </span>
                  {!notification.read && (
                    <span className="text-green-600 font-bold">??/span>
                  )}
                </div>
                <p className="text-sm text-gray-800 mt-1">
                  {notification.body}
                </p>
                {notification.detail && (
                  <p className="text-xs text-gray-600 mt-1">
                    {notification.detail}
                  </p>
                )}
              </div>
              <span className="text-xs text-[#8b95a1] flex-shrink-0 ml-2">
                {notification.time}
              </span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}