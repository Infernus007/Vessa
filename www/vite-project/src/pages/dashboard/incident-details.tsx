import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertTriangle, Clock, User, Server, MapPin, Shield, Tag, Activity, AlertOctagon } from "lucide-react";
import { incidentsAPI } from "@/lib/api/incidents-api";
import { format } from "date-fns";

const statusColors = {
    open: "bg-yellow-100 text-yellow-800",
    investigating: "bg-purple-100 text-purple-800",
    resolved: "bg-green-100 text-green-800",
    closed: "bg-gray-100 text-gray-800"
} as const;

const severityColors = {
    low: "bg-blue-100 text-blue-800",
    medium: "bg-yellow-100 text-yellow-800",
    high: "bg-red-100 text-red-800",
    critical: "bg-purple-100 text-purple-800"
} as const;

export default function IncidentDetails() {
    const { id } = useParams<{ id: string }>();

    const { data: incident, isLoading } = useQuery({
        queryKey: ['incidents', id],
        queryFn: () => id ? incidentsAPI.getIncident(id) : null,
        enabled: !!id
    });

    if (isLoading) {
        return (
            <div className="container mx-auto py-8 space-y-6">
                <Skeleton className="h-8 w-64" />
                <div className="grid gap-6 md:grid-cols-2">
                    <Skeleton className="h-[200px]" />
                    <Skeleton className="h-[200px]" />
                </div>
            </div>
        );
    }

    if (!incident) {
        return (
            <div className="container mx-auto py-8">
                <Card>
                    <CardContent className="flex flex-col items-center justify-center h-[300px]">
                        <AlertTriangle className="h-12 w-12 text-muted-foreground mb-4" />
                        <h2 className="text-xl font-semibold mb-2">Incident Not Found</h2>
                        <p className="text-muted-foreground">The incident you're looking for doesn't exist or has been removed.</p>
                    </CardContent>
                </Card>
            </div>
        );
    }

    console.log(incident)
    return (
        <div className="container mx-auto py-8 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold mb-2">{incident.title}</h1>
                    <div className="flex items-center gap-4">
                        <Badge
                            variant="secondary"
                            className={statusColors[incident.status as keyof typeof statusColors]}
                        >
                            {incident.status}
                        </Badge>
                        <Badge
                            variant="secondary"
                            className={severityColors[incident.severity as keyof typeof severityColors]}
                        >
                            {incident.severity}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                            ID: {incident.id}
                        </span>
                    </div>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                {/* Main Details */}
                <Card>
                    <CardHeader>
                        <CardTitle>Incident Details</CardTitle>
                        <CardDescription>Key information about this security incident</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="space-y-1">
                            <h3 className="text-sm font-medium">Description</h3>
                            <p className="text-sm text-muted-foreground whitespace-pre-line">{incident.description}</p>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-1">
                                <h3 className="text-sm font-medium flex items-center gap-2">
                                    <Clock className="h-4 w-4" />
                                    Created At
                                </h3>
                                <p className="text-sm text-muted-foreground">
                                    {format(new Date(incident.created_at), 'PPpp')}
                                </p>
                            </div>
                            <div className="space-y-1">
                                <h3 className="text-sm font-medium flex items-center gap-2">
                                    <Shield className="h-4 w-4" />
                                    Detection Source
                                </h3>
                                <p className="text-sm text-muted-foreground">{incident.detection_source}</p>
                            </div>
                            <div className="space-y-1">
                                <h3 className="text-sm font-medium flex items-center gap-2">
                                    <Server className="h-4 w-4" />
                                    Affected Systems
                                </h3>
                                <p className="text-sm text-muted-foreground">
                                    {incident.threat_details?.risk_assessment?.potential_impact?.affected_systems?.join(', ') || incident.affected_assets?.join(', ') || 'None'}
                                </p>
                            </div>
                            <div className="space-y-1">
                                <h3 className="text-sm font-medium flex items-center gap-2">
                                    <Tag className="h-4 w-4" />
                                    Tags
                                </h3>
                                <div className="flex flex-wrap gap-2">
                                    {incident.tags.map(tag => (
                                        <Badge key={tag} variant="outline">{tag}</Badge>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Risk Assessment */}
                {incident.threat_details?.risk_assessment && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Risk Assessment</CardTitle>
                            <CardDescription>Threat analysis and risk evaluation</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-1">
                                    <h3 className="text-sm font-medium flex items-center gap-2">
                                        <Activity className="h-4 w-4" />
                                        Risk Level
                                    </h3>
                                    <Badge variant="outline" className="mt-1">
                                        {incident.threat_details.risk_assessment.level}
                                    </Badge>
                                </div>
                                <div className="space-y-1">
                                    <h3 className="text-sm font-medium flex items-center gap-2">
                                        <AlertOctagon className="h-4 w-4" />
                                        Risk Score
                                    </h3>
                                    <p className="text-sm text-muted-foreground">
                                        {incident.threat_details.risk_assessment.score}/100
                                    </p>
                                </div>
                            </div>
                            {incident.threat_details.risk_assessment.factors && incident.threat_details.risk_assessment.factors.length > 0 && (
                                <div className="space-y-2">
                                    <h3 className="text-sm font-medium">Risk Factors</h3>
                                    <ul className="space-y-2">
                                        {incident.threat_details.risk_assessment.factors.map(factor => (
                                            <li key={`${factor.factor}-${factor.weight}`} className="text-sm text-muted-foreground">
                                                • {factor.factor} (Weight: {factor.weight})
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                            {incident.threat_details.risk_assessment.potential_impact && (
                                <div className="space-y-2">
                                    <h3 className="text-sm font-medium">Potential Impact</h3>
                                    <div className="grid grid-cols-3 gap-4">
                                        <div>
                                            <p className="text-sm font-medium">Integrity</p>
                                            <p className="text-sm text-muted-foreground">
                                                {incident.threat_details.risk_assessment.potential_impact.integrity || 0}/10
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium">Availability</p>
                                            <p className="text-sm text-muted-foreground">
                                                {incident.threat_details.risk_assessment.potential_impact.availability || 0}/10
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium">Confidentiality</p>
                                            <p className="text-sm text-muted-foreground">
                                                {incident.threat_details.risk_assessment.potential_impact.confidentiality || 0}/10
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                )}

                {/* Request Details */}
                {incident.threat_details?.request_context && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Request Details</CardTitle>
                            <CardDescription>Information about the suspicious request</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {incident.threat_details.request_context.method && incident.threat_details.request_context.url && (
                                <div className="space-y-2">
                                    <h3 className="text-sm font-medium">Request URL</h3>
                                    <p className="text-sm text-muted-foreground font-mono">
                                        {incident.threat_details.request_context.method} {incident.threat_details.request_context.url}
                                    </p>
                                </div>
                            )}
                            {incident.threat_details.request_context.client_info && (
                                <div className="space-y-2">
                                    <h3 className="text-sm font-medium">Client Information</h3>
                                    <div className="grid grid-cols-2 gap-2 text-sm">
                                        {incident.threat_details.request_context.client_info.ip && (
                                            <div>
                                                <p className="font-medium">IP Address</p>
                                                <p className="text-muted-foreground">{incident.threat_details.request_context.client_info.ip}</p>
                                            </div>
                                        )}
                                        {incident.threat_details.request_context.client_info.hostname && (
                                            <div>
                                                <p className="font-medium">Hostname</p>
                                                <p className="text-muted-foreground">{incident.threat_details.request_context.client_info.hostname}</p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                            {incident.threat_details.request_context.body && (
                                <div className="space-y-2">
                                    <h3 className="text-sm font-medium">Request Body</h3>
                                    <pre className="text-sm bg-muted p-2 rounded-md overflow-auto">
                                        {JSON.stringify(incident.threat_details.request_context.body, null, 2)}
                                    </pre>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                )}

                {/* Threat Analysis */}
                {incident.threat_details?.threat_analysis && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Threat Analysis</CardTitle>
                            <CardDescription>Detailed analysis of the detected threat</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {incident.threat_details.threat_analysis.findings && incident.threat_details.threat_analysis.findings.length > 0 && (
                                <div className="space-y-2">
                                    <h3 className="text-sm font-medium">Findings</h3>
                                    <ul className="space-y-1">
                                        {incident.threat_details.threat_analysis.findings.map(finding => (
                                            <li key={finding} className="text-sm text-muted-foreground">
                                                • {finding}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                            {incident.threat_details.threat_analysis.attack_vectors?.techniques && incident.threat_details.threat_analysis.attack_vectors.techniques.length > 0 && (
                                <div className="space-y-2">
                                    <h3 className="text-sm font-medium">Attack Vectors</h3>
                                    <div className="flex flex-wrap gap-2">
                                        {incident.threat_details.threat_analysis.attack_vectors.techniques.map(technique => (
                                            <Badge key={technique} variant="outline">
                                                {technique.replace('_', ' ')}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>
                            )}
                            {incident.threat_details.detection_timeline?.steps && incident.threat_details.detection_timeline.steps.length > 0 && (
                                <div className="space-y-2">
                                    <h3 className="text-sm font-medium">Detection Timeline</h3>
                                    <div className="space-y-3">
                                        {incident.threat_details.detection_timeline.steps.map(step => (
                                            <div key={`${step.phase}-${step.timestamp}`} className="text-sm">
                                                <p className="font-medium">{step.phase}</p>
                                                <p className="text-muted-foreground">{step.action}</p>
                                                <p className="text-xs text-muted-foreground">
                                                    {format(new Date(step.timestamp), 'PPpp')}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
} 