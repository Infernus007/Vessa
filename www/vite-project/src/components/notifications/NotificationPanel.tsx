import React from 'react';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useNotifications } from '@/lib/context/notification-context';
import { NotificationCard } from './NotificationCard';
import { Button } from '@/components/ui/button';
import { Bell, Check, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface NotificationPanelProps {
  onClose: () => void;
  onNotificationRead?: () => void;
}

export const NotificationPanel: React.FC<NotificationPanelProps> = ({
  onClose,
  onNotificationRead
}) => {
  const { notifications, markAsRead, markAllAsRead, unreadCount } = useNotifications();

  const handleNotificationClick = async (id: string) => {
    try {
      await markAsRead(id);
      onNotificationRead?.();
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  return (
    <Card className="w-[400px] max-w-[90vw] shadow-lg">
      {/* Header */}
      <div className="w-full px-4 py-3 flex items-center justify-between border-b sticky top-0 z-10 bg-background">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Bell className="h-5 w-5" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 h-3 w-3 bg-primary rounded-full" />
            )}
          </div>
          <div>
            <h2 className="text-sm font-medium">Notifications</h2>
            <p className="text-xs text-muted-foreground">
              {unreadCount > 0 ? `${unreadCount} unread` : 'No new notifications'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="h-8 text-xs font-medium"
              onClick={() => markAllAsRead()}
            >
              <Check className="h-3.5 w-3.5 mr-1.5" />
              Mark all read
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Notification List */}
      <ScrollArea className="h-[min(32rem,calc(100vh-12rem))] overflow-y-auto">
        <div className="w-full">
          {notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 px-4">
              <Bell className="h-8 w-8 text-muted-foreground/30 mb-3" />
              <p className="text-sm text-muted-foreground text-center">
                You're all caught up!<br />
                <span className="text-xs">No new notifications</span>
              </p>
            </div>
          ) : (
            <div className="w-full">
              {notifications.map((notification) => (
                <div 
                  key={notification.id}
                  className={cn(
                    "w-full",
                    !notification.read_at && "bg-accent/20"
                  )}
                >
                  <NotificationCard
                    title={notification.title}
                    message={notification.message}
                    priority={notification.priority}
                    createdAt={notification.created_at}
                    read={!!notification.read_at}
                    findings={notification.findings}
                    onClick={() => handleNotificationClick(notification.id)}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      </ScrollArea>
    </Card>
  );
}; 