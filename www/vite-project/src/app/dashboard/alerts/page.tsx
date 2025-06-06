import React from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AlertTriangle, Bell, Filter, Search, Shield, ChevronLeft, ChevronRight } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { NotificationCard } from '@/components/notifications/NotificationCard';
import { Badge } from '@/components/ui/badge';
import { IncidentService, type GetIncidentsParams } from '@/lib/services/incident-service';
import { Skeleton } from "@/components/ui/skeleton";

function StatCardSkeleton() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-4" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-8 w-12" />
      </CardContent>
    </Card>
  );
}

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

export default function AlertsPage() {
  const queryClient = useQueryClient();
  const [filterPriority, setFilterPriority] = React.useState<string>('all');
  const [searchQuery, setSearchQuery] = React.useState('');
  const [currentPage, setCurrentPage] = React.useState(1);
  const PAGE_SIZE = 20;

  const { data, isLoading } = useQuery({
    queryKey: ['incidents', filterPriority, currentPage, PAGE_SIZE],
    queryFn: async () => {
      const params: GetIncidentsParams = {
        page: currentPage,
        page_size: PAGE_SIZE
      };
      
      if (filterPriority !== 'all') {
        params.severity = filterPriority;
      }
      
      const incidentService = new IncidentService();
      return incidentService.getAllIncidents(params);
    }
  });

  const filteredIncidents = data?.items.filter(incident => {
    const matchesSearch = searchQuery === '' || 
      incident.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      incident.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  }) ?? [];

  const stats = {
    total: data?.total_items ?? 0,
    high: data?.items.filter(n => n.severity === 'high').length ?? 0,
    medium: data?.items.filter(n => n.severity === 'medium').length ?? 0,
    low: data?.items.filter(n => n.severity === 'low').length ?? 0,
    unread: data?.items.filter(n => !n.reviewed_at).length ?? 0
  };

  const handleMarkAsRead = async (incidentId: string) => {
    try {
      const incidentService = new IncidentService();
      await incidentService.markIncidentAsReviewed(incidentId);
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
    } catch (error) {
      console.error('Failed to mark incident as reviewed:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      const incidentService = new IncidentService();
      await Promise.all(
        (data?.items ?? [])
          .filter(incident => !incident.reviewed_at)
          .map(incident => incidentService.markIncidentAsReviewed(incident.id))
      );
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
    } catch (error) {
      console.error('Failed to mark all incidents as reviewed:', error);
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Security Alerts</h1>
          <p className="text-muted-foreground">Manage and respond to security incidents</p>
        </div>
        <Button onClick={handleMarkAllAsRead} disabled={isLoading}>
          Mark All as Read
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-5">
        {isLoading ? (
          <>
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
          </>
        ) : (
          <>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Alerts</CardTitle>
                <Bell className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">High Priority</CardTitle>
                <AlertTriangle className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-500">{stats.high}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Medium Priority</CardTitle>
                <Bell className="h-4 w-4 text-yellow-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-500">{stats.medium}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Low Priority</CardTitle>
                <Shield className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-500">{stats.low}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Unread</CardTitle>
                <Badge variant="destructive" className="h-4 w-4 flex items-center justify-center p-2">
                  {stats.unread}
                </Badge>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.unread}</div>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search alerts..."
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

      {/* Alerts List */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Alerts</CardTitle>
          <CardDescription>
            {filteredIncidents.length} alerts found
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <ScrollArea className="h-[600px]">
            <div className="divide-y">
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <NotificationCardSkeleton key={i} />
                ))
              ) : (
                filteredIncidents.map((incident) => (
                  <NotificationCard
                    key={`${incident.id}-${incident.created_at}`}
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
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Pagination */}
      {!isLoading && data && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Showing {((currentPage - 1) * PAGE_SIZE) + 1} to {Math.min(currentPage * PAGE_SIZE, data.total_items)} of {data.total_items} results
          </p>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(p => Math.min(data.total_pages, p + 1))}
              disabled={currentPage === data.total_pages}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
} 