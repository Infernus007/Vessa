import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface RateLimitIndicatorProps {
  limit: number;
  remaining: number;
  resetTime: number;
}

export const RateLimitIndicator: React.FC<RateLimitIndicatorProps> = ({
  limit,
  remaining,
  resetTime,
}) => {
  const percentage = (remaining / limit) * 100;
  const isLow = percentage < 20;
  const resetDate = new Date(resetTime * 1000);
  const waitSeconds = Math.ceil((resetDate.getTime() - Date.now()) / 1000);

  return (
    <div className="flex items-center space-x-2">
      <div className="flex-1">
        <div className="flex justify-between text-xs text-gray-600 mb-1">
          <span>{remaining} requests remaining</span>
          <span>Reset in {waitSeconds}s</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${
              isLow ? 'bg-red-500' : 'bg-green-500'
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      {isLow && (
        <AlertTriangle
          className="h-5 w-5 text-red-500"
          aria-label="Rate limit running low"
        />
      )}
    </div>
  );
}; 