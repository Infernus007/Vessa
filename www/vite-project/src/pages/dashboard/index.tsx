import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/lib/store/auth-store";
import { Link } from "react-router-dom";
import { BarChart, Shield, Code, AlertTriangle, Clock, Users } from "lucide-react";
import { ApiKeyPreview } from "@/components/auth/api-key-preview";
import { AnalyticsReports } from "@/components/dashboard/analytics-reports";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { analyticsAPI } from "@/lib/api/analytics-api";
import { incidentsAPI } from "@/lib/api/incidents-api";

interface Incident {
  id: string;
  title: string;
  severity: "critical" | "high" | "medium" | "low";
  status: "open" | "investigating" | "contained" | "resolved" | "closed";
  created_at: string;
}

const SEVERITY_COLORS = {
  critical: 'bg-red-500',
  high: 'bg-orange-500',
  medium: 'bg-yellow-500',
  low: 'bg-green-500'
} as const;

const STATUS_COLORS = {
  open: 'bg-red-500',
  investigating: 'bg-yellow-500',
  contained: 'bg-blue-500',
  resolved: 'bg-green-500',
  closed: 'bg-gray-500'
} as const;

export default function Dashboard() {
  const { user } = useAuthStore();
  const [recentIncidents, setRecentIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch analytics data for KPIs - using 'all' time range to include test data
  const { data: analyticsData, isLoading: analyticsLoading } = useQuery({
    queryKey: ['analytics', 'overview', 'all'],
    queryFn: () => analyticsAPI.getOverview('all')
  });

  // Fetch recent incidents using proper API client
  useEffect(() => {
    const fetchRecentIncidents = async () => {
      try {
        console.log('[Dashboard] Fetching recent incidents...');
        const data = await incidentsAPI.getRecentIncidents({ limit: 3 });
        console.log('[Dashboard] Recent incidents fetched:', data);
        console.log('[Dashboard] Number of incidents:', data.incidents?.length || 0);
        setRecentIncidents(data.incidents || []);
        setLoading(false);
      } catch (error) {
        console.error('[Dashboard] Error fetching recent incidents:', error);
        setLoading(false);
      }
    };

    fetchRecentIncidents();
  }, []);

  // Debug logging for analytics
  useEffect(() => {
    console.log('[Dashboard] Analytics data:', analyticsData);
    console.log('[Dashboard] Analytics loading:', analyticsLoading);
  }, [analyticsData, analyticsLoading]);

  // Format relative time
  const getRelativeTime = (timestamp: string) => {
    const now = new Date();
    const incidentDate = new Date(timestamp);
    const diffInHours = Math.floor((now.getTime() - incidentDate.getTime()) / (1000 * 60 * 60));

    if (diffInHours < 1) {
      const diffInMinutes = Math.floor((now.getTime() - incidentDate.getTime()) / (1000 * 60));
      return `${diffInMinutes} minute${diffInMinutes !== 1 ? 's' : ''} ago`;
    } else if (diffInHours < 24) {
      return `${diffInHours} hour${diffInHours !== 1 ? 's' : ''} ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays} day${diffInDays !== 1 ? 's' : ''} ago`;
    }
  };

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Welcome back, {user?.name || 'User'}</h1>
          <p className="text-muted-foreground">Here's what's happening with your security incidents</p>
        </div>
        <div className="flex gap-2">
          <Button asChild variant="outline">
            <Link to="/dashboard/incidents/new">
              <Shield className="mr-2 h-4 w-4" />
              Report Incident
            </Link>
          </Button>
          <Button asChild>
            <Link to="/dashboard/integration">
              <Code className="mr-2 h-4 w-4" />
              Integration Center
            </Link>
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold">{analyticsData?.total_requests || 0}</div>
            )}
            <p className="text-xs text-muted-foreground">
              {analyticsData?.blocked_requests || 0} blocked
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Block Rate</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold">{analyticsData?.block_rate?.toFixed(1) || 0}%</div>
            )}
            <p className="text-xs text-muted-foreground">
              Avg threat score: {analyticsData?.avg_threat_score?.toFixed(2) || 0}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Threat Types</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold">
                {analyticsData?.threat_distribution ? Object.keys(analyticsData.threat_distribution).length : 0}
              </div>
            )}
            <p className="text-xs text-muted-foreground">
              {analyticsData?.threat_distribution ?
                Object.entries(analyticsData.threat_distribution)
                  .sort(([, a], [, b]) => (b as number) - (a as number))
                  .slice(0, 2)
                  .map(([type, count]) => `${type}: ${count}`)
                  .join(', ') : 'No threats detected'
              }
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Analytics Reports */}
      <AnalyticsReports timeRange="all" />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Incidents</CardTitle>
            <CardDescription>Your most recent security incidents</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {loading ? (
                // Loading skeletons
                Array(3).fill(0).map((_, i) => (
                  <div key={i} className="flex items-center gap-4 p-3 border rounded-lg">
                    <Skeleton className="h-10 w-10 rounded-full" />
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-4 w-3/4" />
                      <Skeleton className="h-3 w-1/2" />
                    </div>
                    <Skeleton className="h-8 w-16" />
                  </div>
                ))
              ) : recentIncidents.length > 0 ? (
                recentIncidents.map((incident) => (
                  <div key={incident.id} className="flex items-center gap-4 p-3 border rounded-lg hover:bg-accent transition-colors">
                    <div className={`p-2 rounded-full bg-${incident.severity === 'critical' ? 'red' : incident.severity === 'high' ? 'orange' : incident.severity === 'medium' ? 'yellow' : 'green'}-100`}>
                      <AlertTriangle className={`h-4 w-4 text-${incident.severity === 'critical' ? 'red' : incident.severity === 'high' ? 'orange' : incident.severity === 'medium' ? 'yellow' : 'green'}-500`} />
                    </div>
                    <div className="flex-1">
                      <h4 className="text-sm font-medium">{incident.title}</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge className={SEVERITY_COLORS[incident.severity]}>
                          {incident.severity}
                        </Badge>
                        <Badge className={STATUS_COLORS[incident.status]}>
                          {incident.status}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {getRelativeTime(incident.created_at)}
                        </span>
                      </div>
                    </div>
                    <Button variant="ghost" size="sm" asChild>
                      <Link to={`/dashboard/incidents/${incident.id}`}>View</Link>
                    </Button>
                  </div>
                ))
              ) : (
                <div className="text-center py-6 text-muted-foreground">
                  No recent incidents found
                </div>
              )}
              <Button variant="outline" className="w-full" asChild>
                <Link to="/dashboard/incidents">View All Incidents</Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <ApiKeyPreview />

          <Card>
            <CardHeader>
              <CardTitle>Integration Status</CardTitle>
              <CardDescription>Track your integration progress</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">API Key Generated</p>
                    <p className="text-xs text-muted-foreground">Your API key is active and ready to use</p>
                  </div>
                  <div className="h-2 w-2 rounded-full bg-green-500"></div>
                </div>
                <div className="flex justify-between items-center">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">SDK Integration</p>
                    <p className="text-xs text-muted-foreground">Integrate our SDK into your application</p>
                  </div>
                  <Button variant="outline" size="sm" asChild>
                    <Link to="/dashboard/integration?tab=sdk-docs">Setup</Link>
                  </Button>
                </div>
                <div className="flex justify-between items-center">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">Webhook Configuration</p>
                    <p className="text-xs text-muted-foreground">Receive real-time notifications</p>
                  </div>
                  <Button variant="outline" size="sm" asChild>
                    <Link to="/dashboard/integration?tab=webhooks">Configure</Link>
                  </Button>
                </div>
                <Button className="w-full" asChild>
                  <Link to="/dashboard/integration">
                    <Code className="mr-2 h-4 w-4" />
                    Go to Integration Center
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}