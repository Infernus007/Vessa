import { TrendingUp } from "lucide-react"
import { Bar, BarChart, CartesianGrid, LabelList, XAxis } from "recharts"
import { useQuery } from "@tanstack/react-query"
import { analyticsAPI } from "@/lib/api/analytics-api"
import { Skeleton } from "@/components/ui/skeleton"

import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import type { ChartConfig } from "@/components/ui/chart"
import {
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
} from "@/components/ui/chart"

const chartConfig = {
    total: {
        label: "Total Incidents",
        color: "var(--theme-primary)",
    },
} satisfies ChartConfig

interface OverviewProps {
    timeRange?: string;
}

export function Overview({ timeRange = '24h' }: OverviewProps) {
    const { data: timeSeriesData, isLoading } = useQuery({
        queryKey: ['analytics', 'time-series', 'threats', '1h', timeRange],
        queryFn: () => analyticsAPI.getTimeSeries('threats', '1h', timeRange as any)
    });

    if (isLoading) {
        return (
            <div className="h-[300px] w-full flex items-center justify-center">
                <Skeleton className="h-[200px] w-full" />
            </div>
        );
    }

    if (!timeSeriesData?.data || timeSeriesData.data.length === 0) {
        return (
            <div className="h-[300px] w-full flex flex-col items-center justify-center text-muted-foreground">
                <TrendingUp className="h-12 w-12 mb-4" />
                <p>No incident data available</p>
                <p className="text-sm">Data will appear here when incidents are detected</p>
            </div>
        );
    }

    return (
        <ChartContainer config={chartConfig}>
            <BarChart
                accessibilityLayer
                data={timeSeriesData.data}
                margin={{
                    top: 20,
                }}
            >
                <CartesianGrid vertical={false} />
                <XAxis
                    dataKey="timestamp"
                    tickLine={false}
                    tickMargin={10}
                    axisLine={false}
                    tickFormatter={(value) => {
                        const date = new Date(value);
                        return date.toLocaleTimeString('en-US', {
                            hour: '2-digit',
                            minute: '2-digit'
                        });
                    }}
                />
                <ChartTooltip
                    cursor={false}
                    content={<ChartTooltipContent hideLabel />}
                />
                <Bar dataKey="value" fill="var(--theme-primary)" radius={8}>
                    <LabelList
                        position="top"
                        offset={12}
                        className="fill-foreground"
                        fontSize={12}
                    />
                </Bar>
            </BarChart>
        </ChartContainer>
    )
} 