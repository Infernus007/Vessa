import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

export interface StatsCardProps {
    title: string;
    value: number | string;
    description?: string;
    icon?: React.ReactNode;
    trend?: {
        value: number;
        label: string;
        positive?: boolean;
    };
    isLoading?: boolean;
    className?: string;
}

export function StatsCard({ 
    title, 
    value, 
    description, 
    icon, 
    trend,
    isLoading = false,
    className 
}: StatsCardProps) {
    return (
        <Card className={cn("overflow-hidden", className)}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                    {isLoading ? <Skeleton className="h-4 w-[100px]" /> : title}
                </CardTitle>
                {icon && (
                    <div className="opacity-70">
                        {isLoading ? <Skeleton className="h-4 w-4" /> : icon}
                    </div>
                )}
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">
                    {isLoading ? (
                        <Skeleton className="h-8 w-[120px]" />
                    ) : (
                        typeof value === 'number' ? value.toLocaleString() : value
                    )}
                </div>
                {(description || trend) && (
                    <p className="text-xs text-muted-foreground">
                        {description}
                        {trend && (
                            <span className={cn(
                                "ml-2",
                                trend.positive ? "text-green-600" : "text-red-600"
                            )}>
                                {trend.positive ? "↑" : "↓"} {trend.value}% {trend.label}
                            </span>
                        )}
                    </p>
                )}
            </CardContent>
        </Card>
    );
} 