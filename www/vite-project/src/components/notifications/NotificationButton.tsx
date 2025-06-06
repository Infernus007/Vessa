import React from 'react';
import { Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { NotificationBadge } from './NotificationBadge';
import { useNotifications } from '@/lib/context/notification-context';
import { cn } from '@/lib/utils';

interface NotificationButtonProps {
  onClick: () => void;
  className?: string;
}

export const NotificationButton: React.FC<NotificationButtonProps> = ({
  onClick,
  className
}) => {
  const { unreadCount } = useNotifications();

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="icon"
        onClick={onClick}
        className={cn(
          "relative hover:bg-accent",
          unreadCount > 0 && "animate-pulse",
          className
        )}
      >
        <Bell className="h-5 w-5" />
        <span className="sr-only">Notifications</span>
      </Button>
      <NotificationBadge count={unreadCount} />
    </div>
  );
}; 