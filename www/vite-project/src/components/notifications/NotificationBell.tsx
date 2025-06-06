import React, { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';
import { notificationApi } from '@/lib/notifications/notification-api';
import { NotificationPanel } from './NotificationPanel';

export const NotificationBell: React.FC = () => {
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const fetchUnreadCount = async () => {
      try {
        const response = await notificationApi.getNotifications({ unread_only: true, limit: 1 });
        setUnreadCount(response.unread_count);
      } catch (error) {
        console.error('Failed to fetch unread count:', error);
      }
    };

    fetchUnreadCount();
    // You might want to set up a polling interval here
    const interval = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        <Bell className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 block h-4 w-4 rounded-full bg-red-500 text-xs text-white flex items-center justify-center">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-[400px] max-w-[90vw] rounded-md shadow-lg z-50">
          <NotificationPanel 
            onClose={() => setIsOpen(false)}
            onNotificationRead={() => setUnreadCount(prev => Math.max(0, prev - 1))}
          />
        </div>
      )}
    </div>
  );
}; 