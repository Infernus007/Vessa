import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { format } from 'date-fns';
import type { TimeSeriesData } from "@/lib/api/analytics-api";
import { EmptyChart } from "@/components/ui/empty-chart";
import { Activity } from "lucide-react";

interface TimeSeriesChartProps {
    data: TimeSeriesData;
    title: string;
    description?: string;
}

export function TimeSeriesChart({ data, title, description }: TimeSeriesChartProps) {
    // Check if data exists and has points
    if (!data?.data || data.data.length === 0) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>{title}</CardTitle>
                    {description && <CardDescription>{description}</CardDescription>}
                </CardHeader>
                <CardContent>
                    <EmptyChart 
                        title="No activity data"
                        description="There is no activity data available for the selected time period."
                        icon={<Activity className="h-12 w-12 text-muted-foreground/50" />}
                    />
                </CardContent>
            </Card>
        );
    }

    const formattedData = data.data.map(point => ({
        ...point,
        timestamp: format(new Date(point.timestamp), 'MMM dd HH:mm'),
    }));

    // Check if all values are zero
    const hasNonZeroData = formattedData.some(point => point.value > 0);

    if (!hasNonZeroData) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>{title}</CardTitle>
                    {description && <CardDescription>{description}</CardDescription>}
                </CardHeader>
                <CardContent>
                    <EmptyChart 
                        title="No activity detected"
                        description="All values are zero for the selected time period."
                        icon={<Activity className="h-12 w-12 text-muted-foreground/50" />}
                    />
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>{title}</CardTitle>
                {description && <CardDescription>{description}</CardDescription>}
            </CardHeader>
            <CardContent>
                <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart
                            data={formattedData}
                            margin={{
                                top: 10,
                                right: 10,
                                left: 0,
                                bottom: 20,
                            }}
                        >
                            <defs>
                                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3}/>
                                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                                </linearGradient>
                            </defs>
                            <CartesianGrid 
                                strokeDasharray="3 3" 
                                vertical={false}
                                className="stroke-muted"
                            />
                            <XAxis
                                dataKey="timestamp"
                                angle={-45}
                                textAnchor="end"
                                height={70}
                                tick={{ fill: 'currentColor', fontSize: 12 }}
                                tickLine={false}
                                axisLine={false}
                            />
                            <YAxis 
                                tick={{ fill: 'currentColor', fontSize: 12 }}
                                tickLine={false}
                                axisLine={false}
                                tickFormatter={(value) => value.toLocaleString()}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'var(--background)',
                                    borderColor: 'var(--border)',
                                    borderRadius: '8px',
                                }}
                                labelStyle={{ color: 'var(--foreground)' }}
                                itemStyle={{ color: 'var(--foreground)' }}
                            />
                            <Area
                                type="monotone"
                                dataKey="value"
                                stroke="#2563eb"
                                strokeWidth={2}
                                fill="url(#colorValue)"
                                dot={false}
                                activeDot={{
                                    r: 4,
                                    strokeWidth: 2,
                                    stroke: '#2563eb',
                                    fill: 'var(--background)'
                                }}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
} 