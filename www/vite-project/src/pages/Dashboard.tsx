import React from 'react';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { TimeSeriesChart } from '@/components/charts/time-series-chart';
import { DistributionChart } from '@/components/charts/distribution-chart';
import { RecentIncidentsTable } from '@/components/dashboard/recent-incidents-table';
import { StatsCard } from '@/components/ui/stats-card';
import { analyticsAPI, type TimeRange } from '@/lib/api/analytics-api';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Activity, AlertTriangle, BarChart3, Shield } from 'lucide-react';
import { useAuthStore } from '@/lib/store/auth-store';
import { ApiKeyWarning } from '@/components/ApiKeyWarning';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ApiKeyManager } from '@/components/auth/api-key-manager';

const timeRangeOptions: { label: string; value: TimeRange }[] = [
    { label: 'Last 24 hours', value: '24h' },
    { label: 'Last 7 days', value: '7d' },
    { label: 'Last 30 days', value: '30d' },
    { label: 'All time', value: 'all' },
];

function ChartSkeleton() {
    return (
        <Card>
            <CardHeader>
                <Skeleton className="h-5 w-40" />
                <Skeleton className="h-4 w-60" />
            </CardHeader>
            <CardContent>
                <div className="h-[300px] w-full flex items-center justify-center">
                    <div className="space-y-4 w-full p-8">
                        <Skeleton className="h-[200px] w-full" />
                        <div className="space-y-2">
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-[80%]" />
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

export const Dashboard: React.FC = () => {
    const { activeApiKey } = useAuthStore();
    const [timeRange, setTimeRange] = useState<TimeRange>('24h');

    const { data: overview, isLoading: isLoadingOverview } = useQuery({
        queryKey: ['analytics', 'overview', timeRange],
        queryFn: () => analyticsAPI.getOverview(timeRange)
    });

    const { data: timeSeries, isLoading: isLoadingTimeSeries } = useQuery({
        queryKey: ['analytics', 'timeSeries', timeRange],
        queryFn: () => analyticsAPI.getTimeSeries('threats', '1h', timeRange)
    });

    const { data: attackDistribution, isLoading: isLoadingAttackDist } = useQuery({
        queryKey: ['analytics', 'attackDistribution', timeRange],
        queryFn: () => analyticsAPI.getAttackDistribution(timeRange)
    });

    const { data: severityStats, isLoading: isLoadingSeverity } = useQuery({
        queryKey: ['analytics', 'severity', timeRange],
        queryFn: () => analyticsAPI.getThreatSeverity(timeRange)
    });

    const handleTimeRangeChange = (value: string) => {
        setTimeRange(value as TimeRange);
    };

    // Transform attack distribution data
    const attackDistributionData = attackDistribution ? 
        Object.entries(attackDistribution.attack_vectors || {}).map(([name, value]) => ({
            name,
            value: typeof value === 'number' ? value : 0
        })) : [];

    // Transform severity distribution data
    const severityDistributionData = severityStats ? 
        Object.entries(severityStats.severity_distribution || {}).map(([name, value]) => ({
            name,
            value: typeof value === 'number' ? value : 0
        })) : [];

    return (
        <div className="container mx-auto px-4 py-8">
            <ApiKeyWarning />

            {activeApiKey && (
                <div className="bg-white rounded-lg shadow-sm p-4 mb-6 flex items-center justify-between">
                    <div>
                        <h2 className="text-sm font-medium text-gray-500">Active API Key</h2>
                        <p className="text-base font-medium text-gray-900">{activeApiKey.name}</p>
                    </div>
                    <div className="text-sm text-gray-500">
                        Last used: {activeApiKey.last_used ? new Date(activeApiKey.last_used).toLocaleDateString() : 'Never'}
                    </div>
                </div>
            )}

            <div className="flex items-center justify-between mb-8">
                <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
                <Select onValueChange={handleTimeRangeChange} defaultValue={timeRange}>
                    <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Select time range" />
                    </SelectTrigger>
                    <SelectContent>
                        {timeRangeOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                                {option.label}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
                <StatsCard
                    title="Total Requests"
                    value={overview?.total_requests ?? 0}
                    icon={<Activity className="h-4 w-4" />}
                    isLoading={isLoadingOverview}
                />
                <StatsCard
                    title="Average Threat Score"
                    value={(overview?.avg_threat_score ?? 0).toFixed(2)}
                    icon={<AlertTriangle className="h-4 w-4" />}
                    isLoading={isLoadingOverview}
                />
                <StatsCard
                    title="Unique Attack Vectors"
                    value={attackDistributionData.length}
                    icon={<BarChart3 className="h-4 w-4" />}
                    isLoading={isLoadingAttackDist}
                />
            </div>

            <div className="grid gap-6 md:grid-cols-2 mb-8">
                {isLoadingTimeSeries ? (
                    <ChartSkeleton />
                ) : (
                    <TimeSeriesChart
                        data={timeSeries || { data: [], metric: 'threats', interval: '1h', time_range: timeRange }}
                        title="Threat Activity"
                        description="Number of threats detected over time"
                    />
                )}
                {isLoadingAttackDist ? (
                    <ChartSkeleton />
                ) : (
                    <DistributionChart
                        data={attackDistributionData}
                        title="Attack Distribution"
                        description="Distribution of attack vectors"
                    />
                )}
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                {isLoadingSeverity ? (
                    <ChartSkeleton />
                ) : (
                    <DistributionChart
                        data={severityDistributionData}
                        title="Severity Distribution"
                        description="Distribution of threat severity levels"
                    />
                )}
                <ApiKeyManager />
            </div>

            <RecentIncidentsTable />
        </div>
    );
};

export default Dashboard; 