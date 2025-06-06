import React from 'react';
import { cn } from '@/lib/utils';
import { AlertTriangle, CheckCircle, Clock, Tag, Server, Shield } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { formatDistanceToNow, isValid } from 'date-fns';
import { Button } from '@/components/ui/button';

interface NotificationCardProps {
  title: string;
  message: string;
  priority: 'low' | 'medium' | 'high';
  status: 'open' | 'resolved' | 'in_progress';
  createdAt: string;
  read: boolean;
  findings: Array<{ message: string; type: string; severity: string; }>;
  affectedAssets?: string[];
  tags?: string[];
  detectionSource?: string;
  onClick?: () => void;
}

export function NotificationCard({
  title,
  message,
  priority,
  status,
  createdAt,
  read,
  findings,
  affectedAssets,
  tags,
  detectionSource,
  onClick
}: NotificationCardProps) {
  const getFormattedDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      if (!isValid(date)) {
        console.error('Invalid date:', dateStr);
        return 'Invalid date';
      }
      return formatDistanceToNow(date, { addSuffix: true });
    } catch (error) {
      console.error('Error formatting date:', error);
      return 'Invalid date';
    }
  };

  const formattedDate = getFormattedDate(createdAt);

  const priorityColors = {
    low: "bg-blue-100 text-blue-800",
    medium: "bg-yellow-100 text-yellow-800",
    high: "bg-red-100 text-red-800"
  };

  const statusColors = {
    open: "bg-red-100 text-red-800",
    in_progress: "bg-yellow-100 text-yellow-800",
    resolved: "bg-green-100 text-green-800"
  };

  return (
    <div className={cn(
      "p-4 border-b transition-colors cursor-pointer hover:bg-muted/40",
      !read && "bg-muted/30"
    )} onClick={onClick}>
      <div className="space-y-3">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <h4 className="text-sm font-medium">{title}</h4>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              {formattedDate}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className={priorityColors[priority]}>
              {priority}
            </Badge>
            <Badge variant="outline" className={statusColors[status]}>
              {status.replace('_', ' ')}
            </Badge>
          </div>
        </div>

        <p className="text-sm text-muted-foreground line-clamp-2">{message}</p>

        {findings && findings.length > 0 && (
          <div className="space-y-1">
            <p className="text-xs font-medium">Findings:</p>
            <ul className="text-xs text-muted-foreground space-y-1">
              {findings.slice(0, 3).map((finding, index) => (
                <li key={index} className="flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3 text-yellow-500" />
                  {finding.message}
                </li>
              ))}
              {findings.length > 3 && (
                <li className="text-xs text-muted-foreground">
                  +{findings.length - 3} more findings...
                </li>
              )}
            </ul>
          </div>
        )}

        <div className="flex flex-wrap gap-2 items-center text-xs">
          {detectionSource && (
            <Badge variant="outline" className="flex items-center gap-1">
              <Shield className="h-3 w-3" />
              {detectionSource.replace('_', ' ')}
            </Badge>
          )}
          
          {affectedAssets && affectedAssets.length > 0 && (
            <Badge variant="outline" className="flex items-center gap-1">
              <Server className="h-3 w-3" />
              {affectedAssets.join(', ')}
            </Badge>
          )}

          {tags && tags.length > 0 && (
            <div className="flex items-center gap-1">
              <Tag className="h-3 w-3 text-muted-foreground" />
              {tags.map((tag, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {tag.replace('_', ' ')}
                </Badge>
              ))}
            </div>
          )}
        </div>

        {!read && (
          <div className="flex justify-end">
            <Button
              variant="ghost"
              size="sm"
              className="text-xs"
            >
              Mark as Reviewed
            </Button>
          </div>
        )}
      </div>
    </div>
  );
} 