import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { EmptyChart } from "@/components/ui/empty-chart";
import { PieChart as PieChartIcon } from "lucide-react";

interface DistributionChartProps {
    data: Array<{
        name: string;
        value: number;
    }>;
    title: string;
    description?: string;
}

interface CustomizedLabelProps {
    cx: number;
    cy: number;
    midAngle: number;
    innerRadius: number;
    outerRadius: number;
    percent: number;
    name: string;
}

const COLORS = ['#2563eb', '#16a34a', '#dc2626', '#ca8a04', '#9333ea', '#0891b2', '#be185d'];

export function DistributionChart({ data, title, description }: DistributionChartProps) {
    // Check if data exists and has items
    if (!data || data.length === 0) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>{title}</CardTitle>
                    {description && <CardDescription>{description}</CardDescription>}
                </CardHeader>
                <CardContent>
                    <EmptyChart 
                        title="No distribution data"
                        description="There is no distribution data available for the selected time period."
                        icon={<PieChartIcon className="h-12 w-12 text-muted-foreground/50" />}
                    />
                </CardContent>
            </Card>
        );
    }

    // Calculate total value
    const total = data.reduce((sum, item) => sum + item.value, 0);

    // Check if all values are zero
    if (total === 0) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>{title}</CardTitle>
                    {description && <CardDescription>{description}</CardDescription>}
                </CardHeader>
                <CardContent>
                    <EmptyChart 
                        title="No distribution detected"
                        description="All values are zero for the selected time period."
                        icon={<PieChartIcon className="h-12 w-12 text-muted-foreground/50" />}
                    />
                </CardContent>
            </Card>
        );
    }
    
    // Group small values into "Others"
    const threshold = total * 0.05; // 5% threshold
    const processedData = data.reduce((acc, item) => {
        if (item.value >= threshold) {
            acc.mainItems.push(item);
        } else {
            acc.othersValue += item.value;
        }
        return acc;
    }, { mainItems: [] as typeof data, othersValue: 0 });

    // Add "Others" category if there are small values
    const finalData = processedData.othersValue > 0 
        ? [...processedData.mainItems, { name: 'Others', value: processedData.othersValue }]
        : processedData.mainItems;

    // Custom label renderer to prevent overlapping
    const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, name }: CustomizedLabelProps) => {
        const RADIAN = Math.PI / 180;
        const radius = innerRadius + (outerRadius - innerRadius) * 1.4; // Increase label distance
        const x = cx + radius * Math.cos(-midAngle * RADIAN);
        const y = cy + radius * Math.sin(-midAngle * RADIAN);

        // Only show label if percentage is significant enough
        if (percent < 0.05) return null;

        return (
            <text
                x={x}
                y={y}
                fill="currentColor"
                textAnchor={x > cx ? 'start' : 'end'}
                dominantBaseline="central"
                className="text-xs"
            >
                {`${name} (${(percent * 100).toFixed(0)}%)`}
            </text>
        );
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>{title}</CardTitle>
                {description && <CardDescription>{description}</CardDescription>}
            </CardHeader>
            <CardContent>
                <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={finalData}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={renderCustomizedLabel}
                                outerRadius={100}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {finalData.map((entry, index) => (
                                    <Cell 
                                        key={`cell-${entry.name}`} 
                                        fill={COLORS[index % COLORS.length]} 
                                    />
                                ))}
                            </Pie>
                            <Tooltip />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
} 