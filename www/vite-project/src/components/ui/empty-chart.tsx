import React from 'react';
import { BarChart3 } from 'lucide-react';

interface EmptyChartProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
}

export function EmptyChart({ 
  title, 
  description = "No data available for this time period", 
  icon = <BarChart3 className="h-12 w-12 text-muted-foreground/50" />
}: EmptyChartProps) {
  return (
    <div className="flex h-[300px] w-full flex-col items-center justify-center rounded-md border border-dashed p-8 text-center animate-in fade-in-50">
      <div className="mx-auto flex max-w-[420px] flex-col items-center justify-center text-center">
        {icon}
        <h3 className="mt-4 text-lg font-semibold">{title}</h3>
        <p className="mt-2 text-sm text-muted-foreground">
          {description}
        </p>
      </div>
    </div>
  );
} 