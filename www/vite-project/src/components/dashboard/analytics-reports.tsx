import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { analyticsAPI, type TimeRange } from "@/lib/api/analytics-api";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, AreaChart, Area, PieChart, Pie, Cell } from 'recharts';
import { MapPin, Server, Shield, Activity, Clock, AlertTriangle } from "lucide-react";
import { EmptyChart } from "@/components/ui/empty-chart";
import { Skeleton } from "@/components/ui/skeleton";

interface AnalyticsReportsProps {
    timeRange?: TimeRange;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

function ChartSkeleton() {
    return (
        <div className="h-[300px] w-full flex items-center justify-center">
            <div className="space-y-4 w-full p-8">
                <Skeleton className="h-[200px] w-full" />
                <div className="space-y-2">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-[80%]" />
                </div>
            </div>
        </div>
    );
}

export function AnalyticsReports({ timeRange = '24h' }: AnalyticsReportsProps) {
    const { data: systemImpactData, isLoading: systemLoading } = useQuery({
        queryKey: ['analytics', 'system-impact', timeRange],
        queryFn: () => analyticsAPI.getSystemImpact(timeRange)
    });

    const { data: geoData, isLoading: geoLoading } = useQuery({
        queryKey: ['analytics', 'geo', timeRange],
        queryFn: () => analyticsAPI.getGeoAnalytics(timeRange)
    });

    const { data: attackData, isLoading: attackLoading } = useQuery({
        queryKey: ['analytics', 'attack-distribution', timeRange],
        queryFn: () => analyticsAPI.getAttackDistribution(timeRange)
    });

    const { data: severityData, isLoading: severityLoading } = useQuery({
        queryKey: ['analytics', 'severity', timeRange],
        queryFn: () => analyticsAPI.getThreatSeverity(timeRange)
    });

    const { data: timeSeriesData, isLoading: timeSeriesLoading } = useQuery({
        queryKey: ['analytics', 'time-series', timeRange],
        queryFn: () => analyticsAPI.getTimeSeries('threats', '1h', timeRange)
    });

    // Transform time series data
    const hasTimeSeriesData = timeSeriesData?.data && timeSeriesData.data.length > 0 &&
        timeSeriesData.data.some(point => point.value > 0);

    // Transform severity data
    const severityDistributionData = severityData ?
        Object.entries(severityData.severity_distribution || {}).map(([name, value]) => ({
            name,
            value: typeof value === 'number' ? value : 0
        })) : [];
    const hasSeverityData = severityDistributionData.length > 0 &&
        severityDistributionData.some(item => item.value > 0);

    // Transform attack data
    const attackDistributionData = attackData ?
        Object.entries(attackData.attack_vectors || {}).map(([name, value]) => ({
            name,
            value: typeof value === 'number' ? value : 0
        })) : [];
    const hasAttackData = attackDistributionData.length > 0 &&
        attackDistributionData.some(item => item.value > 0);

    return (
        <div className="space-y-6">
            {/* Time Series and Severity Distribution */}
            <div className="grid gap-4 md:grid-cols-2">
                <Card>
                    <CardHeader>
                        <div className="flex items-center space-x-2">
                            <Activity className="h-4 w-4 text-muted-foreground" />
                            <CardTitle>Threat Activity</CardTitle>
                        </div>
                        <CardDescription>Incident activity over time</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {timeSeriesLoading ? (
                            <ChartSkeleton />
                        ) : !hasTimeSeriesData ? (
                            <EmptyChart
                                title="No activity data"
                                description="There is no activity data available for this time period."
                                icon={<Activity className="h-12 w-12 text-muted-foreground/50" />}
                            />
                        ) : (
                            <div className="h-[300px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={timeSeriesData.data}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="timestamp" />
                                        <YAxis />
                                        <Tooltip />
                                        <Area type="monotone" dataKey="value" fill="var(--primary)" fillOpacity={0.2} stroke="var(--primary)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        )}
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <div className="flex items-center space-x-2">
                            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                            <CardTitle>Severity Distribution</CardTitle>
                        </div>
                        <CardDescription>Distribution of incidents by severity level</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {severityLoading ? (
                            <ChartSkeleton />
                        ) : !hasSeverityData ? (
                            <EmptyChart
                                title="No severity data"
                                description="There is no severity distribution data available for this time period."
                                icon={<AlertTriangle className="h-12 w-12 text-muted-foreground/50" />}
                            />
                        ) : (
                            <div className="h-[300px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={severityDistributionData}
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={60}
                                            outerRadius={80}
                                            paddingAngle={5}
                                            dataKey="value"
                                        >
                                            {severityDistributionData.map((entry, index) => (
                                                <Cell key={`cell-${entry.name}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip />
                                        <Legend verticalAlign="bottom" height={36} />
                                    </PieChart>
                                </ResponsiveContainer>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Affected Assets and Incident Status */}
            <div className="grid gap-4 md:grid-cols-2">
                <Card>
                    <CardHeader>
                        <div className="flex items-center space-x-2">
                            <Server className="h-4 w-4 text-muted-foreground" />
                            <CardTitle>Affected Assets</CardTitle>
                        </div>
                        <CardDescription>Most frequently affected systems and assets</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {attackLoading ? (
                            <ChartSkeleton />
                        ) : !attackData?.input_points || Object.keys(attackData.input_points).length === 0 ? (
                            <EmptyChart
                                title="No asset data"
                                description="There is no affected asset data available for this time period."
                                icon={<Server className="h-12 w-12 text-muted-foreground/50" />}
                            />
                        ) : (
                            <div className="h-[300px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart
                                        data={Object.entries(attackData.input_points).map(([name, value]) => ({ name, value }))}
                                        margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                                        layout="horizontal"
                                    >
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis
                                            dataKey="name"
                                            angle={-45}
                                            textAnchor="end"
                                            height={100}
                                            interval={0}
                                        />
                                        <YAxis />
                                        <Tooltip />
                                        <Bar name="Incidents" dataKey="value" fill="#3b82f6" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        )}
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <div className="flex items-center space-x-2">
                            <Clock className="h-4 w-4 text-muted-foreground" />
                            <CardTitle>Incident Status</CardTitle>
                        </div>
                        <CardDescription>Current status of all incidents</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {severityLoading ? (
                            <ChartSkeleton />
                        ) : !severityData?.severity_distribution || Object.keys(severityData.severity_distribution).length === 0 ? (
                            <EmptyChart
                                title="No status data"
                                description="There is no incident status data available for this time period."
                                icon={<Clock className="h-12 w-12 text-muted-foreground/50" />}
                            />
                        ) : (
                            <div className="space-y-6">
                                <div className="h-[240px]">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart
                                            data={Object.entries(severityData.severity_distribution).map(([name, value]) => ({
                                                name: name.charAt(0).toUpperCase() + name.slice(1),
                                                value
                                            }))}
                                            margin={{ top: 20 }}
                                        >
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis dataKey="name" />
                                            <YAxis />
                                            <Tooltip />
                                            <Bar name="Count" dataKey="value" fill="#10b981">
                                                {Object.entries(severityData.severity_distribution).map((_, index) => (
                                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                ))}
                                            </Bar>
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                    <div className="flex flex-col space-y-1">
                                        <span className="text-muted-foreground">Total Incidents</span>
                                        <span className="text-xl font-bold">
                                            {Object.values(severityData.severity_distribution).reduce((a: number, b) => a + (b as number), 0)}
                                        </span>
                                    </div>
                                    <div className="flex flex-col space-y-1">
                                        <span className="text-muted-foreground">Critical Severity</span>
                                        <span className="text-xl font-bold text-destructive">
                                            {severityData.severity_distribution.critical || 0}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Attack Distribution */}
            <Card>
                <CardHeader>
                    <div className="flex items-center space-x-2">
                        <Shield className="h-4 w-4 text-muted-foreground" />
                        <CardTitle>Attack Distribution</CardTitle>
                    </div>
                    <CardDescription>Distribution of attack vectors and patterns</CardDescription>
                </CardHeader>
                <CardContent>
                    {attackLoading ? (
                        <ChartSkeleton />
                    ) : !hasAttackData ? (
                        <EmptyChart
                            title="No attack distribution data"
                            description="There is no attack distribution data available for this time period."
                            icon={<Shield className="h-12 w-12 text-muted-foreground/50" />}
                        />
                    ) : (
                        <div className="h-[300px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart margin={{ top: 20, right: 100, bottom: 20, left: 20 }}>
                                    <Pie
                                        data={attackDistributionData}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={true}
                                        outerRadius={100}
                                        fill="#8884d8"
                                        dataKey="value"
                                        nameKey="name"
                                    >
                                        {attackDistributionData.map((entry, index) => (
                                            <Cell key={`cell-${entry.name}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip formatter={(value, name) => [
                                        `${value} (${((value as number / attackDistributionData.reduce((a, b) => a + b.value, 0)) * 100).toFixed(0)}%)`,
                                        name
                                    ]} />
                                    <Legend
                                        layout="vertical"
                                        verticalAlign="middle"
                                        align="right"
                                        wrapperStyle={{ paddingLeft: "20px" }}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
} 