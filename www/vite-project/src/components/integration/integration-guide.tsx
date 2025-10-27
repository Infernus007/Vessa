import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { InfoIcon, CheckCircle2 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export function IntegrationGuide() {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>VESSA API Integration Guide</CardTitle>
          <CardDescription>
            Integrate VESSA security analysis directly into your applications using our REST API
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <Alert className="border-primary">
            <CheckCircle2 className="h-4 w-4 text-primary" />
            <AlertTitle>NEW: WAF Deployment Mode Available!</AlertTitle>
            <AlertDescription>
              Looking for zero-code protection? Check out the <strong>WAF Deployment</strong> tab for drop-in firewall protection that requires no API integration.
              For API-based analysis, continue reading below.
            </AlertDescription>
          </Alert>

          <Alert>
            <InfoIcon className="h-4 w-4" />
            <AlertTitle>Authentication Required</AlertTitle>
            <AlertDescription>
              All API requests require authentication using Bearer tokens or API keys. Generate your API key from the API Keys tab.
            </AlertDescription>
          </Alert>

          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                Base URL
              </h3>
              <div className="bg-muted p-4 rounded-md">
                <code className="text-sm">https://api.vessa.io/api/v1</code>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                Authentication Headers
              </h3>
              <div className="bg-muted p-4 rounded-md">
                <pre className="text-xs overflow-x-auto"><code>{`Authorization: Bearer YOUR_JWT_TOKEN
# OR
X-API-Key: YOUR_API_KEY`}</code></pre>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Core Endpoints */}
      <Card>
        <CardHeader>
          <CardTitle>Core Security Endpoints</CardTitle>
          <CardDescription>Main endpoints for threat analysis and incident management</CardDescription>
        </CardHeader>
        <CardContent className="space-y-8">

          {/* Health Check */}
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">GET</span>
              <code className="text-sm font-mono">/health</code>
            </div>
            <p className="text-sm text-muted-foreground">Check API health and model status</p>

            <Tabs defaultValue="response" className="w-full">
              <TabsList>
                <TabsTrigger value="response">Response</TabsTrigger>
                <TabsTrigger value="example">cURL Example</TabsTrigger>
              </TabsList>
              <TabsContent value="response" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "status": "healthy",
  "version": "1.0.0",
  "model_status": "loaded"
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="example" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`curl https://api.vessa.io/api/v1/health`}</code></pre>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          {/* Analyze Request */}
          <div className="space-y-3 border-t pt-6">
            <div className="flex items-center gap-3">
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-semibold">POST</span>
              <code className="text-sm font-mono">/analyze</code>
            </div>
            <p className="text-sm text-muted-foreground">Analyze a request for security threats (primary endpoint)</p>

            <Tabs defaultValue="request" className="w-full">
              <TabsList>
                <TabsTrigger value="request">Request Body</TabsTrigger>
                <TabsTrigger value="response">Response</TabsTrigger>
                <TabsTrigger value="example">cURL Example</TabsTrigger>
              </TabsList>
              <TabsContent value="request" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "client_ip": "192.168.1.100",
  "request_path": "/api/users/1",
  "request_method": "POST",
  "request_headers": {
    "User-Agent": "Mozilla/5.0...",
    "Content-Type": "application/json"
  },
  "request_body": "{\\"username\\": \\"admin\\', OR 1=1--\\"}"
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="response" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "threat_score": 0.95,
  "threat_type": "sql_injection",
  "findings": [
    "SQL injection pattern detected in request body",
    "Malicious payload: OR 1=1--"
  ],
  "should_block": true
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="example" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`curl -X POST https://api.vessa.io/api/v1/analyze \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "client_ip": "192.168.1.100",
    "request_path": "/api/users",
    "request_method": "POST",
    "request_headers": {"User-Agent": "curl/7.68.0"},
    "request_body": "test payload"
  }'`}</code></pre>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          {/* Create Incident */}
          <div className="space-y-3 border-t pt-6">
            <div className="flex items-center gap-3">
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-semibold">POST</span>
              <code className="text-sm font-mono">/incidents/</code>
            </div>
            <p className="text-sm text-muted-foreground">Create a new security incident</p>

            <Tabs defaultValue="request" className="w-full">
              <TabsList>
                <TabsTrigger value="request">Request Body</TabsTrigger>
                <TabsTrigger value="response">Response</TabsTrigger>
                <TabsTrigger value="example">cURL Example</TabsTrigger>
              </TabsList>
              <TabsContent value="request" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "title": "SQL Injection Attempt",
  "description": "Detected SQL injection in login form",
  "severity": "critical",
  "affected_assets": ["web-server", "database"],
  "tags": ["sql-injection", "authentication"],
  "detection_source": "automated",
  "reporter_id": "user-uuid"
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="response" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "id": "89f10b6e-45e5-4c21-bfdf-dfe1f502b229",
  "title": "SQL Injection Attempt",
  "description": "Detected SQL injection in login form",
  "severity": "critical",
  "status": "open",
  "detection_source": "automated",
  "affected_assets": ["web-server", "database"],
  "tags": ["sql-injection", "authentication"],
  "created_at": "2025-10-27T12:00:00Z",
  "updated_at": "2025-10-27T12:00:00Z",
  "resolved_at": null,
  "resolution_notes": null,
  "threat_details": {},
  "mitigation_steps": null,
  "false_positive": false,
  "reporter_id": "user-uuid",
  "assigned_to": null
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="example" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`curl -X POST https://api.vessa.io/api/v1/incidents/ \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "title": "SQL Injection Attempt",
    "description": "Detected in login form",
    "severity": "critical",
    "detection_source": "automated"
  }'`}</code></pre>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          {/* Get Recent Incidents */}
          <div className="space-y-3 border-t pt-6">
            <div className="flex items-center gap-3">
              <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">GET</span>
              <code className="text-sm font-mono">/incidents/recent</code>
            </div>
            <p className="text-sm text-muted-foreground">Get recent security incidents (limit: 50)</p>

            <Tabs defaultValue="response" className="w-full">
              <TabsList>
                <TabsTrigger value="response">Response</TabsTrigger>
                <TabsTrigger value="example">cURL Example</TabsTrigger>
              </TabsList>
              <TabsContent value="response" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "incidents": [
    {
      "id": "89f10b6e-45e5-4c21-bfdf-dfe1f502b229",
      "title": "SQL Injection Attempt",
      "description": "Detected SQL injection in login form",
      "severity": "critical",
      "status": "open",
      "detection_source": "automated",
      "affected_assets": ["web-server", "database"],
      "tags": ["sql-injection", "authentication"],
      "created_at": "2025-10-27T12:00:00Z",
      "updated_at": "2025-10-27T12:00:00Z",
      "resolved_at": null,
      "resolution_notes": null,
      "threat_details": {},
      "reporter_id": "user-uuid",
      "assigned_to": null,
      "reviewed_at": null,
      "findings": []
    }
  ],
  "total": 1
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="example" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`curl -X GET https://api.vessa.io/api/v1/incidents/recent \\
  -H "Authorization: Bearer YOUR_TOKEN"`}</code></pre>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          {/* Get Incident Details */}
          <div className="space-y-3 border-t pt-6">
            <div className="flex items-center gap-3">
              <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">GET</span>
              <code className="text-sm font-mono">/incidents/&#123;incident_id&#125;</code>
            </div>
            <p className="text-sm text-muted-foreground">Get details of a specific incident</p>

            <Tabs defaultValue="response" className="w-full">
              <TabsList>
                <TabsTrigger value="response">Response</TabsTrigger>
                <TabsTrigger value="example">cURL Example</TabsTrigger>
              </TabsList>
              <TabsContent value="response" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "id": "89f10b6e-45e5-4c21-bfdf-dfe1f502b229",
  "title": "SQL Injection Attempt",
  "description": "Detected SQL injection in login form",
  "severity": "critical",
  "status": "open",
  "detection_source": "automated",
  "affected_assets": ["web-server", "database"],
  "tags": ["sql-injection", "authentication"],
  "created_at": "2025-10-27T12:00:00Z",
  "updated_at": "2025-10-27T12:00:00Z",
  "resolved_at": null,
  "resolution_notes": null,
  "threat_details": {
    "threat_type": "sql_injection",
    "threat_score": 0.95,
    "risk_assessment": {
      "risk_level": "critical",
      "risk_score": 95,
      "risk_factors": ["High threat score", "Critical severity"],
      "potential_impact": {
        "confidentiality": 9,
        "integrity": 8,
        "availability": 6,
        "affected_systems": ["database", "auth-service"]
      }
    },
    "request_context": {
      "method": "POST",
      "url": "/api/login",
      "client_ip": "192.168.1.100",
      "user_agent": "Mozilla/5.0"
    }
  },
  "mitigation_steps": null,
  "false_positive": false,
  "reporter_id": "user-uuid",
  "assigned_to": null
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="example" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`curl -X GET https://api.vessa.io/api/v1/incidents/INCIDENT_ID \\
  -H "Authorization: Bearer YOUR_TOKEN"`}</code></pre>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          {/* Update Incident */}
          <div className="space-y-3 border-t pt-6">
            <div className="flex items-center gap-3">
              <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-xs font-semibold">PUT</span>
              <code className="text-sm font-mono">/incidents/&#123;incident_id&#125;</code>
            </div>
            <p className="text-sm text-muted-foreground">Update an existing incident</p>

            <Tabs defaultValue="request" className="w-full">
              <TabsList>
                <TabsTrigger value="request">Request Body</TabsTrigger>
                <TabsTrigger value="response">Response</TabsTrigger>
                <TabsTrigger value="example">cURL Example</TabsTrigger>
              </TabsList>
              <TabsContent value="request" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "status": "resolved",
  "resolution_notes": "False positive - legitimate traffic",
  "false_positive": true
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="response" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "id": "89f10b6e-45e5-4c21-bfdf-dfe1f502b229",
  "title": "SQL Injection Attempt",
  "status": "resolved",
  "resolution_notes": "False positive - legitimate traffic",
  "false_positive": true,
  "resolved_at": "2025-10-27T13:00:00Z",
  ...
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="example" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`curl -X PUT https://api.vessa.io/api/v1/incidents/INCIDENT_ID \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"status": "resolved"}'`}</code></pre>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </CardContent>
      </Card>

      {/* Analytics Endpoints */}
      <Card>
        <CardHeader>
          <CardTitle>Analytics & Reporting Endpoints</CardTitle>
          <CardDescription>Access threat analytics and security metrics</CardDescription>
        </CardHeader>
        <CardContent className="space-y-8">

          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">GET</span>
              <code className="text-sm font-mono">/incidents/analytics/overview</code>
            </div>
            <p className="text-sm text-muted-foreground">Get comprehensive threat analytics overview</p>

            <Tabs defaultValue="params" className="w-full">
              <TabsList>
                <TabsTrigger value="params">Query Parameters</TabsTrigger>
                <TabsTrigger value="response">Response</TabsTrigger>
                <TabsTrigger value="example">cURL Example</TabsTrigger>
              </TabsList>
              <TabsContent value="params" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`?time_range=24h|7d|30d|all`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="response" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "total_incidents": 150,
  "open_incidents": 45,
  "resolved_incidents": 105,
  "critical_incidents": 12,
  "high_incidents": 28,
  "medium_incidents": 67,
  "low_incidents": 43,
  "avg_resolution_time_hours": 4.5,
  "block_rate": 0.85,
  "time_range": "24h"
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="example" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`curl -X GET "https://api.vessa.io/api/v1/incidents/analytics/overview?time_range=24h" \\
  -H "Authorization: Bearer YOUR_TOKEN"`}</code></pre>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          <div className="space-y-3 border-t pt-6">
            <div className="flex items-center gap-3">
              <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">GET</span>
              <code className="text-sm font-mono">/incidents/analytics/attack-distribution</code>
            </div>
            <p className="text-sm text-muted-foreground">Get attack type distribution statistics</p>

            <Tabs defaultValue="response" className="w-full">
              <TabsList>
                <TabsTrigger value="response">Response</TabsTrigger>
                <TabsTrigger value="example">cURL Example</TabsTrigger>
              </TabsList>
              <TabsContent value="response" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "attack_types": [
    {"type": "sql_injection", "count": 45, "percentage": 30.0},
    {"type": "xss", "count": 38, "percentage": 25.3},
    {"type": "path_traversal", "count": 30, "percentage": 20.0},
    {"type": "command_injection", "count": 22, "percentage": 14.7},
    {"type": "other", "count": 15, "percentage": 10.0}
  ],
  "total_attacks": 150
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="example" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`curl -X GET "https://api.vessa.io/api/v1/incidents/analytics/attack-distribution?time_range=7d" \\
  -H "Authorization: Bearer YOUR_TOKEN"`}</code></pre>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          <div className="space-y-3 border-t pt-6">
            <div className="flex items-center gap-3">
              <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">GET</span>
              <code className="text-sm font-mono">/incidents/analytics/severity</code>
            </div>
            <p className="text-sm text-muted-foreground">Get severity distribution statistics</p>

            <Tabs defaultValue="response" className="w-full">
              <TabsList>
                <TabsTrigger value="response">Response</TabsTrigger>
                <TabsTrigger value="example">cURL Example</TabsTrigger>
              </TabsList>
              <TabsContent value="response" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "severity_distribution": [
    {"severity": "critical", "count": 12, "percentage": 8.0},
    {"severity": "high", "count": 28, "percentage": 18.7},
    {"severity": "medium", "count": 67, "percentage": 44.7},
    {"severity": "low", "count": 43, "percentage": 28.6}
  ],
  "total_incidents": 150,
  "avg_severity_score": 5.8
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="example" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`curl -X GET "https://api.vessa.io/api/v1/incidents/analytics/severity?time_range=30d" \\
  -H "Authorization: Bearer YOUR_TOKEN"`}</code></pre>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          <div className="space-y-3 border-t pt-6">
            <div className="flex items-center gap-3">
              <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">GET</span>
              <code className="text-sm font-mono">/incidents/analytics/time-series</code>
            </div>
            <p className="text-sm text-muted-foreground">Get time-series threat activity data</p>

            <Tabs defaultValue="response" className="w-full">
              <TabsList>
                <TabsTrigger value="response">Response</TabsTrigger>
                <TabsTrigger value="example">cURL Example</TabsTrigger>
              </TabsList>
              <TabsContent value="response" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "time_series": [
    {
      "timestamp": "2025-10-27T00:00:00Z",
      "total_incidents": 23,
      "critical": 2,
      "high": 6,
      "medium": 10,
      "low": 5
    },
    {
      "timestamp": "2025-10-27T01:00:00Z",
      "total_incidents": 18,
      "critical": 1,
      "high": 4,
      "medium": 8,
      "low": 5
    }
  ],
  "granularity": "hourly"
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="example" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`curl -X GET "https://api.vessa.io/api/v1/incidents/analytics/time-series?time_range=24h" \\
  -H "Authorization: Bearer YOUR_TOKEN"`}</code></pre>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </CardContent>
      </Card>

      {/* Authentication Endpoints */}
      <Card>
        <CardHeader>
          <CardTitle>Authentication Endpoints</CardTitle>
          <CardDescription>Manage authentication and API keys</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">

          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-semibold">POST</span>
              <code className="text-sm font-mono">/auth/login</code>
            </div>
            <p className="text-sm text-muted-foreground">Authenticate and obtain JWT token</p>
            <Tabs defaultValue="request" className="w-full">
              <TabsList>
                <TabsTrigger value="request">Request</TabsTrigger>
                <TabsTrigger value="response">Response</TabsTrigger>
                <TabsTrigger value="example">cURL Example</TabsTrigger>
              </TabsList>
              <TabsContent value="request" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "email": "user@example.com",
  "password": "your_password"
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="response" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "admin"
  }
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="example" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`curl -X POST https://api.vessa.io/api/v1/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'`}</code></pre>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          <div className="space-y-3 border-t pt-6">
            <div className="flex items-center gap-3">
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-semibold">POST</span>
              <code className="text-sm font-mono">/auth/register</code>
            </div>
            <p className="text-sm text-muted-foreground">Register a new user account</p>
            <Tabs defaultValue="request" className="w-full">
              <TabsList>
                <TabsTrigger value="request">Request</TabsTrigger>
                <TabsTrigger value="response">Response</TabsTrigger>
                <TabsTrigger value="example">cURL Example</TabsTrigger>
              </TabsList>
              <TabsContent value="request" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "email": "newuser@example.com",
  "password": "secure_password",
  "name": "Jane Smith",
  "company": "Acme Corp"
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="response" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "new-user-uuid",
    "email": "newuser@example.com",
    "name": "Jane Smith",
    "role": "user"
  }
}`}</code></pre>
                </div>
              </TabsContent>
              <TabsContent value="example" className="mt-2">
                <div className="bg-muted p-4 rounded-md">
                  <pre className="text-xs overflow-x-auto"><code>{`curl -X POST https://api.vessa.io/api/v1/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "newuser@example.com",
    "password": "secure_password",
    "name": "Jane Smith"
  }'`}</code></pre>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </CardContent>
      </Card>

      {/* Implementation Example */}
      <Card>
        <CardHeader>
          <CardTitle>Implementation Examples</CardTitle>
          <CardDescription>Quick start examples for common use cases</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">

          <div className="space-y-3">
            <h4 className="text-sm font-semibold">Python Example (Flask Middleware)</h4>
            <div className="bg-muted p-4 rounded-md">
              <pre className="text-xs overflow-x-auto"><code>{`import requests
from flask import request, jsonify

VESSA_API_URL = "https://api.vessa.io/api/v1"
API_TOKEN = "your_api_token_here"

def analyze_request_middleware():
    # Collect request data
    payload = {
        "client_ip": request.remote_addr,
        "request_path": request.path,
        "request_method": request.method,
        "request_headers": dict(request.headers),
        "request_body": request.get_data(as_text=True)
    }
    
    # Send to VESSA API
    response = requests.post(
        f"{VESSA_API_URL}/analyze",
        json=payload,
        headers={"Authorization": f"Bearer {API_TOKEN}"}
    )
    
    result = response.json()
    
    # Block if threat detected
    if result.get("should_block"):
        return jsonify({"error": "Request blocked"}), 403
    
    # Log high-risk requests
    if result.get("threat_score", 0) > 0.7:
        print(f"⚠️  High-risk request: {result['threat_type']}")
    
    return None  # Continue processing`}</code></pre>
            </div>
          </div>

          <div className="space-y-3 border-t pt-6">
            <h4 className="text-sm font-semibold">Node.js Example (Express Middleware)</h4>
            <div className="bg-muted p-4 rounded-md">
              <pre className="text-xs overflow-x-auto"><code>{`const axios = require('axios');

const VESSA_API_URL = 'https://api.vessa.io/api/v1';
const API_TOKEN = 'your_api_token_here';

async function vessaAnalyzer(req, res, next) {
    try {
        const payload = {
            client_ip: req.ip,
            request_path: req.path,
            request_method: req.method,
            request_headers: req.headers,
            request_body: JSON.stringify(req.body)
        };
        
        const response = await axios.post(
            \`\${VESSA_API_URL}/analyze\`,
            payload,
            { 
              headers: { 
                'Authorization': \`Bearer \${API_TOKEN}\` 
              } 
            }
        );
        
        const result = response.data;
        
        if (result.should_block) {
            return res.status(403).json({ 
              error: 'Request blocked' 
            });
        }
        
        if (result.threat_score > 0.7) {
            console.log(\`⚠️  High-risk: \${result.threat_type}\`);
        }
        
        next();
    } catch (error) {
        console.error('VESSA analysis error:', error);
        next(); // Fail open - allow request
    }
}

app.use(vessaAnalyzer);`}</code></pre>
            </div>
          </div>

          <div className="space-y-3 border-t pt-6">
            <h4 className="text-sm font-semibold">Go Example (HTTP Middleware)</h4>
            <div className="bg-muted p-4 rounded-md">
              <pre className="text-xs overflow-x-auto"><code>{`package main

import (
    "bytes"
    "encoding/json"
    "net/http"
)

const (
    VESSAAPIUrl = "https://api.vessa.io/api/v1"
    APIToken    = "your_api_token_here"
)

func VessaMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        payload := map[string]interface{}{
            "client_ip":       r.RemoteAddr,
            "request_path":    r.URL.Path,
            "request_method":  r.Method,
            "request_headers": r.Header,
        }
        
        body, _ := json.Marshal(payload)
        req, _ := http.NewRequest("POST", 
            VESSAAPIUrl+"/analyze", 
            bytes.NewBuffer(body))
        req.Header.Set("Authorization", "Bearer "+APIToken)
        req.Header.Set("Content-Type", "application/json")
        
        client := &http.Client{}
        resp, err := client.Do(req)
        if err != nil {
            next.ServeHTTP(w, r) // Fail open
            return
        }
        defer resp.Body.Close()
        
        var result map[string]interface{}
        json.NewDecoder(resp.Body).Decode(&result)
        
        if shouldBlock, ok := result["should_block"].(bool); ok && shouldBlock {
            http.Error(w, "Request blocked", http.StatusForbidden)
            return
        }
        
        next.ServeHTTP(w, r)
    })
}`}</code></pre>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Error Responses */}
      <Card>
        <CardHeader>
          <CardTitle>Error Responses</CardTitle>
          <CardDescription>Common error codes and their meanings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="grid grid-cols-3 gap-4 text-sm font-semibold border-b pb-2">
              <div>Status Code</div>
              <div>Meaning</div>
              <div>Common Cause</div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm py-2 border-b">
              <div className="font-mono">400</div>
              <div>Bad Request</div>
              <div>Invalid request payload or missing required fields</div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm py-2 border-b">
              <div className="font-mono">401</div>
              <div>Unauthorized</div>
              <div>Missing, expired, or invalid authentication token</div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm py-2 border-b">
              <div className="font-mono">403</div>
              <div>Forbidden</div>
              <div>Insufficient permissions or API key limits exceeded</div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm py-2 border-b">
              <div className="font-mono">404</div>
              <div>Not Found</div>
              <div>Resource doesn't exist or endpoint URL is incorrect</div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm py-2 border-b">
              <div className="font-mono">429</div>
              <div>Too Many Requests</div>
              <div>Rate limit exceeded - retry after cooldown period</div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm py-2">
              <div className="font-mono">500</div>
              <div>Server Error</div>
              <div>Internal server issue - contact support if persists</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Rate Limits */}
      <Card>
        <CardHeader>
          <CardTitle>Rate Limits</CardTitle>
          <CardDescription>API usage limits and best practices</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="font-semibold">Standard Plan</p>
                <p className="text-muted-foreground">1,000 requests/hour</p>
              </div>
              <div>
                <p className="font-semibold">Professional Plan</p>
                <p className="text-muted-foreground">10,000 requests/hour</p>
              </div>
              <div>
                <p className="font-semibold">Enterprise Plan</p>
                <p className="text-muted-foreground">Unlimited requests</p>
              </div>
              <div>
                <p className="font-semibold">Burst Limit</p>
                <p className="text-muted-foreground">100 requests/second</p>
              </div>
            </div>
          </div>
          <Alert>
            <InfoIcon className="h-4 w-4" />
            <AlertDescription>
              Rate limit headers are included in all responses: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
}
