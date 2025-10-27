import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    AlertCircle,
    Clock,
    Shield,
    AlertTriangle,
    CheckCircle,
    Server,
    Tag,
    FileText,
    MessageSquare
} from 'lucide-react';

interface IncidentDetails {
    id: string;
    title: string;
    description: string;
    severity: "critical" | "high" | "medium" | "low";
    status: "open" | "investigating" | "contained" | "resolved" | "closed";
    detection_source: string;
    reporter_id: string;
    affected_assets: string[];
    tags: string[];
    threat_details: {
        request_context: {
            timestamp: string;
            method: string;
            url: string;
            path: string;
            headers: Record<string, string>;
            body: any;
            query_params: Record<string, string>;
            client_info: Record<string, string>;
        };
        threat_analysis: {
            overall_score: number;
            normalized_score: number;
            threat_types: string[];
            primary_threat: string;
            findings: string[];
            pattern_matches: Record<string, any>;
            attack_vectors: Record<string, any>;
        };
        risk_assessment: {
            level: string;
            score: number;
            factors: Array<{ factor: string; weight: number }>;
            potential_impact: {
                confidentiality: number;
                integrity: number;
                availability: number;
                affected_systems: string[];
            };
            mitigation_priority: "immediate" | "high" | "normal";
        };
    };
    created_at: string;
    updated_at: string;
    resolved_at?: string;
}

const STATUS_COLORS = {
    open: 'bg-red-500',
    investigating: 'bg-yellow-500',
    contained: 'bg-blue-500',
    resolved: 'bg-green-500',
    closed: 'bg-gray-500'
};

const SEVERITY_COLORS = {
    critical: 'bg-red-500',
    high: 'bg-orange-500',
    medium: 'bg-yellow-500',
    low: 'bg-green-500'
};

export function IncidentDetailsPage() {
    const { id } = useParams<{ id: string }>();
    const [incident, setIncident] = useState<IncidentDetails | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchIncidentDetails = async () => {
            try {
                const data = await incidentsAPI.getIncident(id);
                setIncident(data);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching incident details:', error);
                setLoading(false);
            }
        };

        fetchIncidentDetails();
    }, [id]);

    const handleStatusChange = async (newStatus: string) => {
        try {
            // Note: This would need to be implemented in the incidentsAPI
            // For now, just update the local state
            setIncident(prev => prev ? { ...prev, status: newStatus as IncidentDetails['status'] } : null);
        } catch (error) {
            console.error('Error updating incident status:', error);
        }
    };

    if (loading) {
        return (
            <div className="container mx-auto px-4 py-8">
                <Skeleton className="h-8 w-64 mb-4" />
                <Skeleton className="h-4 w-32 mb-8" />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Skeleton className="h-[400px]" />
                    <Skeleton className="h-[400px]" />
                </div>
            </div>
        );
    }

    if (!incident) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="text-center">
                    <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
                    <h2 className="text-2xl font-bold mb-2">Incident Not Found</h2>
                    <p className="text-gray-500">The incident you're looking for doesn't exist or you don't have permission to view it.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <div className="flex items-center gap-4 mb-2">
                        <h1 className="text-3xl font-bold">{incident.title}</h1>
                        <Badge className={SEVERITY_COLORS[incident.severity]}>
                            {incident.severity.toUpperCase()}
                        </Badge>
                        <Badge className={STATUS_COLORS[incident.status]}>
                            {incident.status.toUpperCase()}
                        </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-gray-500">
                        <div className="flex items-center gap-2">
                            <Clock className="w-4 h-4" />
                            <span>Created {new Date(incident.created_at).toLocaleString()}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Shield className="w-4 h-4" />
                            <span>Detected by {incident.detection_source}</span>
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-4">
                    <Select
                        value={incident.status}
                        onValueChange={handleStatusChange}
                    >
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Update Status" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="open">Open</SelectItem>
                            <SelectItem value="investigating">Investigating</SelectItem>
                            <SelectItem value="contained">Contained</SelectItem>
                            <SelectItem value="resolved">Resolved</SelectItem>
                            <SelectItem value="closed">Closed</SelectItem>
                        </SelectContent>
                    </Select>
                    <Button variant="outline">Export Report</Button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Threat Analysis */}
                <Card>
                    <CardHeader>
                        <CardTitle>Threat Analysis</CardTitle>
                        <CardDescription>Detailed analysis of the security incident</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-6">
                            <div>
                                <h3 className="font-semibold mb-2">Threat Score</h3>
                                <div className="flex items-center gap-4">
                                    <div className="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-red-500"
                                            style={{
                                                width: `${incident.threat_details.threat_analysis.normalized_score}%`,
                                                backgroundColor: incident.threat_details.threat_analysis.normalized_score > 75 ? '#ef4444' :
                                                    incident.threat_details.threat_analysis.normalized_score > 50 ? '#f97316' :
                                                        incident.threat_details.threat_analysis.normalized_score > 25 ? '#eab308' : '#22c55e'
                                            }}
                                        />
                                    </div>
                                    <span className="font-bold">{incident.threat_details.threat_analysis.normalized_score}%</span>
                                </div>
                            </div>

                            <div>
                                <h3 className="font-semibold mb-2">Primary Threat</h3>
                                <Badge variant="outline" className="text-red-500 border-red-500">
                                    {incident.threat_details.threat_analysis.primary_threat}
                                </Badge>
                            </div>

                            <div>
                                <h3 className="font-semibold mb-2">Key Findings</h3>
                                <ul className="space-y-2">
                                    {incident.threat_details.threat_analysis.findings.map((finding, index) => (
                                        <li key={index} className="flex items-start gap-2">
                                            <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                                            <span>{finding}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Impact Assessment */}
                <Card>
                    <CardHeader>
                        <CardTitle>Impact Assessment</CardTitle>
                        <CardDescription>Evaluation of potential system impact</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-6">
                            <div>
                                <h3 className="font-semibold mb-2">Risk Level</h3>
                                <Badge className={
                                    incident.threat_details.risk_assessment.level === 'high' ? 'bg-red-500' :
                                        incident.threat_details.risk_assessment.level === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                                }>
                                    {incident.threat_details.risk_assessment.level.toUpperCase()}
                                </Badge>
                            </div>

                            <div>
                                <h3 className="font-semibold mb-2">Affected Systems</h3>
                                <div className="flex flex-wrap gap-2">
                                    {incident.threat_details.risk_assessment.potential_impact.affected_systems.map((system, index) => (
                                        <Badge key={index} variant="outline" className="flex items-center gap-1">
                                            <Server className="w-3 h-3" />
                                            {system}
                                        </Badge>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <h3 className="font-semibold mb-2">Impact Metrics</h3>
                                <div className="grid grid-cols-3 gap-4">
                                    <div>
                                        <p className="text-sm text-gray-500 mb-1">Confidentiality</p>
                                        <div className="flex items-center gap-2">
                                            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-blue-500"
                                                    style={{ width: `${incident.threat_details.risk_assessment.potential_impact.confidentiality}%` }}
                                                />
                                            </div>
                                            <span className="text-sm font-medium">{incident.threat_details.risk_assessment.potential_impact.confidentiality}%</span>
                                        </div>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-500 mb-1">Integrity</p>
                                        <div className="flex items-center gap-2">
                                            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-blue-500"
                                                    style={{ width: `${incident.threat_details.risk_assessment.potential_impact.integrity}%` }}
                                                />
                                            </div>
                                            <span className="text-sm font-medium">{incident.threat_details.risk_assessment.potential_impact.integrity}%</span>
                                        </div>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-500 mb-1">Availability</p>
                                        <div className="flex items-center gap-2">
                                            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-blue-500"
                                                    style={{ width: `${incident.threat_details.risk_assessment.potential_impact.availability}%` }}
                                                />
                                            </div>
                                            <span className="text-sm font-medium">{incident.threat_details.risk_assessment.potential_impact.availability}%</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Request Details */}
                <Card>
                    <CardHeader>
                        <CardTitle>Request Details</CardTitle>
                        <CardDescription>Information about the suspicious request</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div>
                                <p className="text-sm font-medium text-gray-500">Method & Path</p>
                                <div className="flex items-center gap-2 mt-1">
                                    <Badge variant="outline" className="text-blue-500">
                                        {incident.threat_details.request_context.method}
                                    </Badge>
                                    <code className="text-sm bg-gray-100 px-2 py-1 rounded">
                                        {incident.threat_details.request_context.path}
                                    </code>
                                </div>
                            </div>

                            <div>
                                <p className="text-sm font-medium text-gray-500">Headers</p>
                                <pre className="mt-1 text-sm bg-gray-100 p-2 rounded overflow-x-auto">
                                    {JSON.stringify(incident.threat_details.request_context.headers, null, 2)}
                                </pre>
                            </div>

                            {incident.threat_details.request_context.body && (
                                <div>
                                    <p className="text-sm font-medium text-gray-500">Request Body</p>
                                    <pre className="mt-1 text-sm bg-gray-100 p-2 rounded overflow-x-auto">
                                        {JSON.stringify(incident.threat_details.request_context.body, null, 2)}
                                    </pre>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>

                {/* Tags and Assets */}
                <Card>
                    <CardHeader>
                        <CardTitle>Additional Information</CardTitle>
                        <CardDescription>Tags and affected assets</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-6">
                            <div>
                                <h3 className="font-semibold mb-2">Tags</h3>
                                <div className="flex flex-wrap gap-2">
                                    {incident.tags.map((tag, index) => (
                                        <Badge key={index} variant="outline" className="flex items-center gap-1">
                                            <Tag className="w-3 h-3" />
                                            {tag}
                                        </Badge>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <h3 className="font-semibold mb-2">Affected Assets</h3>
                                <div className="flex flex-wrap gap-2">
                                    {incident.affected_assets.map((asset, index) => (
                                        <Badge key={index} variant="outline" className="flex items-center gap-1">
                                            <Server className="w-3 h-3" />
                                            {asset}
                                        </Badge>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <h3 className="font-semibold mb-2">Timeline</h3>
                                <div className="space-y-3">
                                    <div className="flex items-center gap-2 text-sm">
                                        <Badge variant="outline" className="bg-blue-50">Created</Badge>
                                        <span>{new Date(incident.created_at).toLocaleString()}</span>
                                    </div>
                                    <div className="flex items-center gap-2 text-sm">
                                        <Badge variant="outline" className="bg-blue-50">Updated</Badge>
                                        <span>{new Date(incident.updated_at).toLocaleString()}</span>
                                    </div>
                                    {incident.resolved_at && (
                                        <div className="flex items-center gap-2 text-sm">
                                            <Badge variant="outline" className="bg-green-50 text-green-700">Resolved</Badge>
                                            <span>{new Date(incident.resolved_at).toLocaleString()}</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
} 