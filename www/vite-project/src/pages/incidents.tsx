import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Filter, Search } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { NotificationCard } from '@/components/notifications/NotificationCard';
import { type AnalyticsData, type RecentIncidentsResponse, incidentsAPI } from '@/lib/api/incidents-api';
import { useToast } from '@/components/ui/use-toast';
import { Skeleton } from '@/components/ui/skeleton';
import { useAuthStore } from '@/lib/store/auth-store';

function NotificationCardSkeleton() {
  return (
    <div className="p-4 border-b">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Skeleton className="h-5 w-48" />
          <Skeleton className="h-5 w-24" />
        </div>
        <Skeleton className="h-4 w-full" />
        <div className="flex items-center gap-2">
          <Skeleton className="h-6 w-16" />
          <Skeleton className="h-6 w-16" />
        </div>
      </div>
    </div>
  );
}

export function IncidentsPage() {
  const [filterPriority, setFilterPriority] = React.useState<string>('all');
  const [searchQuery, setSearchQuery] = React.useState('');
  const [currentPage, setCurrentPage] = React.useState(1);
  const PAGE_SIZE = 20;
  const { toast } = useToast();
  const userId = useAuthStore(state => state.user?.id);
  
  // Fetch incidents
  const { data: incidentsData, isLoading: isLoadingIncidents } = useQuery<RecentIncidentsResponse>({
    queryKey: ['incidents', filterPriority, currentPage],
    queryFn: () => incidentsAPI.getRecentIncidents({
      limit: PAGE_SIZE,
      offset: (currentPage - 1) * PAGE_SIZE
    })
  });

  // Fetch analytics
  const { data: analyticsData, isLoading: isLoadingAnalytics } = useQuery<AnalyticsData>({
    queryKey: ['incidents-analytics'],
    queryFn: () => userId ? incidentsAPI.getAnalytics(userId) : Promise.reject('No user ID'),
    enabled: !!userId
  });

  const filteredIncidents = React.useMemo(() => {
    if (!incidentsData?.incidents) return [];
    return incidentsData.incidents.filter((incident) => {
      const matchesSearch = searchQuery === '' || 
        incident.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        incident.description.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesSearch;
    });
  }, [incidentsData?.incidents, searchQuery]);

  const handleMarkAsRead = async (incidentId: string) => {
    try {
      await incidentsAPI.markIncidentAsReviewed(incidentId);
      toast({
        title: "Success",
        description: "Incident marked as reviewed",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to mark incident as reviewed",
        variant: "destructive",
      });
    }
  };

  const stats = React.useMemo(() => {
    if (!analyticsData) return {
      total: 0,
      by_severity: {},
      by_status: {},
      severityData: [],
      statusData: []
    };

    const { reported_incidents } = analyticsData;
    
    // Convert severity and status data to arrays for rendering
    const severityData = Object.entries(reported_incidents.by_severity).map(([key, value]) => ({
      severity: key,
      count: value
    }));

    const statusData = Object.entries(reported_incidents.by_status).map(([key, value]) => ({
      status: key,
      count: value
    }));

    return {
      total: reported_incidents.total,
      by_severity: reported_incidents.by_severity,
      by_status: reported_incidents.by_status,
      severityData,
      statusData
    };
  }, [analyticsData]);

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Security Incidents</h1>
          <p className="text-muted-foreground">View and manage security incidents</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Incidents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        {stats.severityData.map(({ severity, count }) => (
          <Card key={severity}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium capitalize">{severity} Severity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{count}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search incidents..."
                  className="pl-8"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>
            <Select value={filterPriority} onValueChange={setFilterPriority}>
              <SelectTrigger className="w-[180px]">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Filter by priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priorities</SelectItem>
                <SelectItem value="high">High Priority</SelectItem>
                <SelectItem value="medium">Medium Priority</SelectItem>
                <SelectItem value="low">Low Priority</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Incidents List */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Incidents</CardTitle>
          <CardDescription>
            {filteredIncidents.length} incidents found
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <ScrollArea className="h-[600px]">
            <div className="divide-y">
              {isLoadingIncidents ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <NotificationCardSkeleton key={i} />
                ))
              ) : filteredIncidents.length > 0 ? (
                filteredIncidents.map((incident) => (
                  <NotificationCard
                    key={incident.id}
                    title={incident.title}
                    message={incident.description}
                    priority={incident.severity}
                    status={incident.status}
                    createdAt={incident.created_at}
                    read={!!incident.reviewed_at}
                    findings={incident.findings}
                    affectedAssets={incident.affected_assets}
                    tags={incident.tags}
                    detectionSource={incident.detection_source}
                    onClick={() => handleMarkAsRead(incident.id)}
                  />
                ))
              ) : (
                <div className="p-8 text-center text-muted-foreground">
                  No incidents found
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Pagination */}
      {!isLoadingIncidents && incidentsData && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Showing {((currentPage - 1) * PAGE_SIZE) + 1} to {Math.min(currentPage * PAGE_SIZE, incidentsData.total_count)} of {incidentsData.total_count} results
          </p>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(p => p + 1)}
              disabled={!incidentsData.has_more}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
} 