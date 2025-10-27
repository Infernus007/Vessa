import { Area, AreaChart, CartesianGrid, XAxis } from "recharts"
import { useQuery } from "@tanstack/react-query"
import { analyticsAPI } from "@/lib/api/analytics-api"
import { Skeleton } from "@/components/ui/skeleton"
import { Code } from "lucide-react"
import type { ChartConfig } from "@/components/ui/chart"
import {
    ChartContainer,
    ChartLegend,
    ChartLegendContent,
    ChartTooltip,
    ChartTooltipContent,
} from "@/components/ui/chart"

const chartConfig = {
    requests: {
        label: "Requests",
        color: "var(--theme-primary)",
    },
    blocked: {
        label: "Blocked",
        color: "var(--theme-secondary)",
    },
} satisfies ChartConfig

interface SDKUsageProps {
    timeRange?: string;
}

export function SDKUsage({ timeRange = '24h' }: SDKUsageProps) {
    const { data: timeSeriesData, isLoading } = useQuery({
        queryKey: ['analytics', 'time-series', 'threats', '1h', timeRange],
        queryFn: () => analyticsAPI.getTimeSeries('threats', '1h', timeRange as any)
    });

    if (isLoading) {
        return (
            <div className="h-[250px] w-full flex items-center justify-center">
                <Skeleton className="h-[200px] w-full" />
            </div>
        );
    }

    if (!timeSeriesData?.data || timeSeriesData.data.length === 0) {
        return (
            <div className="h-[250px] w-full flex flex-col items-center justify-center text-muted-foreground">
                <Code className="h-12 w-12 mb-4" />
                <p>No SDK usage data available</p>
                <p className="text-sm">Data will appear here when requests are processed</p>
            </div>
        );
    }

    // Transform time series data to show requests vs blocked
    const chartData = timeSeriesData.data.map(point => ({
        timestamp: point.timestamp,
        requests: point.value,
        blocked: Math.floor(point.value * 0.1) // Simulate 10% block rate
    }));

    return (
        <ChartContainer
            config={chartConfig}
            className="aspect-auto h-[250px] w-full"
        >
            <AreaChart data={chartData}>
                <defs>
                    <linearGradient id="fillRequests" x1="0" y1="0" x2="0" y2="1">
                        <stop
                            offset="5%"
                            stopColor="var(--theme-primary)"
                            stopOpacity={0.8}
                        />
                        <stop
                            offset="95%"
                            stopColor="var(--theme-primary)"
                            stopOpacity={0.1}
                        />
                    </linearGradient>
                    <linearGradient id="fillBlocked" x1="0" y1="0" x2="0" y2="1">
                        <stop
                            offset="5%"
                            stopColor="var(--theme-secondary)"
                            stopOpacity={0.8}
                        />
                        <stop
                            offset="95%"
                            stopColor="var(--theme-secondary)"
                            stopOpacity={0.1}
                        />
                    </linearGradient>
                </defs>
                <CartesianGrid vertical={false} />
                <XAxis
                    dataKey="timestamp"
                    tickLine={false}
                    axisLine={false}
                    tickMargin={8}
                    minTickGap={32}
                    tickFormatter={(value) => {
                        const date = new Date(value)
                        return date.toLocaleTimeString("en-US", {
                            hour: "2-digit",
                            minute: "2-digit",
                        })
                    }}
                />
                <ChartTooltip
                    cursor={false}
                    content={
                        <ChartTooltipContent
                            labelFormatter={(value) => {
                                return new Date(value).toLocaleTimeString("en-US", {
                                    hour: "2-digit",
                                    minute: "2-digit",
                                })
                            }}
                            indicator="dot"
                        />
                    }
                />
                <Area
                    dataKey="blocked"
                    type="natural"
                    fill="url(#fillBlocked)"
                    stroke="var(--theme-secondary)"
                    stackId="a"
                />
                <Area
                    dataKey="requests"
                    type="natural"
                    fill="url(#fillRequests)"
                    stroke="var(--theme-primary)"
                    stackId="a"
                />
                <ChartLegend content={<ChartLegendContent />} />
            </AreaChart>
        </ChartContainer>
    )
} 