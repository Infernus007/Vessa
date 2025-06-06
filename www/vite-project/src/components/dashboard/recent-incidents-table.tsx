import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Link } from "react-router-dom";
import { incidentsAPI } from "@/lib/api/incidents-api";

const ITEMS_PER_PAGE = 5;

const statusColors = {
    open: "bg-yellow-100 text-yellow-800",
    investigating: "bg-purple-100 text-purple-800",
    resolved: "bg-green-100 text-green-800",
    closed: "bg-gray-100 text-gray-800"
} as const;

export function RecentIncidentsTable() {
    const [page, setPage] = useState(0);

    const { data, isLoading } = useQuery({
        queryKey: ['incidents', 'recent', page],
        queryFn: () => incidentsAPI.getRecentIncidents({
            limit: ITEMS_PER_PAGE,
            offset: page * ITEMS_PER_PAGE
        })
    });

    const handlePreviousPage = () => {
        setPage(prev => Math.max(0, prev - 1));
    };

    const handleNextPage = () => {
        if (data?.has_more) {
            setPage(prev => prev + 1);
        }
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Recent Incidents</CardTitle>
                <CardDescription>Latest security incidents reported in your system</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="rounded-md border">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Reported By</TableHead>
                                <TableHead>Title</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Time</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {isLoading ? (
                                <TableRow>
                                    <TableCell colSpan={5} className="h-24 text-center">
                                        Loading recent incidents...
                                    </TableCell>
                                </TableRow>
                            ) : data?.incidents.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={5} className="h-24 text-center">
                                        No incidents found.
                                    </TableCell>
                                </TableRow>
                            ) : (
                                data?.incidents.map(incident => (
                                    <TableRow key={incident.id}>
                                        <TableCell>
                                            <div className="flex items-center gap-3">
                                                <Avatar className="h-8 w-8">
                                                    <AvatarImage src={incident.user.avatar} alt={incident.user.name} />
                                                    <AvatarFallback>{incident.user.name[0]}</AvatarFallback>
                                                </Avatar>
                                                <div className="flex flex-col">
                                                    <span className="text-sm font-medium">{incident.user.name}</span>
                                                    <span className="text-xs text-muted-foreground">{incident.user.email}</span>
                                                </div>
                                            </div>
                                        </TableCell>
                                        <TableCell className="font-medium">
                                            {incident.title}
                                        </TableCell>
                                        <TableCell>
                                            <Badge 
                                                variant="secondary"
                                                className={statusColors[incident.status as keyof typeof statusColors] || "bg-gray-100 text-gray-800"}
                                            >
                                                {incident.status}
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="text-muted-foreground text-sm">
                                            {incident.timestamp}
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                asChild
                                            >
                                                <Link to={`/dashboard/incidents/${incident.id}`}>
                                                    View
                                                </Link>
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </div>
                <div className="flex items-center justify-end space-x-2 py-4">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handlePreviousPage}
                        disabled={page === 0}
                    >
                        <ChevronLeft className="h-4 w-4" />
                        Previous
                    </Button>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleNextPage}
                        disabled={!data?.has_more}
                    >
                        Next
                        <ChevronRight className="h-4 w-4" />
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}