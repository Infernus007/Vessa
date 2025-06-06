import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Steps, Step } from "@/components/ui/steps";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { InfoIcon } from "lucide-react";

export function IntegrationGuide() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Integration Guide</CardTitle>
        <CardDescription>
          Follow these steps to integrate VESSA with your applications
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <Alert>
          <InfoIcon className="h-4 w-4" />
          <AlertTitle>Before you begin</AlertTitle>
          <AlertDescription>
            Make sure you have an active API key. If you don't have one, generate it from the API Keys tab.
          </AlertDescription>
        </Alert>
        
        <Steps>
          <Step title="Install the SDK">
            <div className="space-y-2">
              <p>Choose your preferred language and install the SDK:</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-muted p-4 rounded-md">
                  <h4 className="text-sm font-semibold mb-2">JavaScript</h4>
                  <pre className="text-xs"><code>npm install vessa-sdk</code></pre>
                </div>
                
                <div className="bg-muted p-4 rounded-md">
                  <h4 className="text-sm font-semibold mb-2">Python</h4>
                  <pre className="text-xs"><code>pip install vessa-sdk</code></pre>
                </div>
              </div>
            </div>
          </Step>
          
          <Step title="Initialize the client">
            <div className="space-y-2">
              <p>Initialize the VESSA client with your API key:</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-muted p-4 rounded-md">
                  <h4 className="text-sm font-semibold mb-2">JavaScript</h4>
                  <pre className="text-xs overflow-x-auto"><code>{`import { VessaClient } from 'vessa-sdk';

const client = new VessaClient({
  apiKey: 'your-api-key',
});`}</code></pre>
                </div>
                
                <div className="bg-muted p-4 rounded-md">
                  <h4 className="text-sm font-semibold mb-2">Python</h4>
                  <pre className="text-xs overflow-x-auto"><code>{`from vessa_sdk import VessaClient

client = VessaClient(
    api_key='your-api-key'
)`}</code></pre>
                </div>
              </div>
            </div>
          </Step>
          
          <Step title="Forward event data">
            <div className="space-y-2">
              <p>Forward raw event data to the VESSA API:</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-muted p-4 rounded-md">
                  <h4 className="text-sm font-semibold mb-2">JavaScript</h4>
                  <pre className="text-xs overflow-x-auto"><code>{`// Forward raw event data
await client.request('POST', '/api/v1/events', {
  event_data: {
    source_ip: '192.168.1.1',
    timestamp: new Date().toISOString(),
    request_path: '/admin',
    user_agent: 'Mozilla/5.0',
    headers: {
      authorization: 'Bearer ***'
    },
    payload: JSON.stringify({action: 'get_users'})
  }
});`}</code></pre>
                </div>
                
                <div className="bg-muted p-4 rounded-md">
                  <h4 className="text-sm font-semibold mb-2">Python</h4>
                  <pre className="text-xs overflow-x-auto"><code>{`# Forward raw event data
import json
from datetime import datetime

client.request(
    method="POST",
    path="/api/v1/events",
    data={
        "event_data": {
            "source_ip": "192.168.1.1",
            "timestamp": datetime.now().isoformat(),
            "request_path": "/admin",
            "user_agent": "Mozilla/5.0",
            "headers": {
                "authorization": "Bearer ***"
            },
            "payload": json.dumps({"action": "get_users"})
        }
    }
)`}</code></pre>
                </div>
              </div>
            </div>
          </Step>
          
          <Step title="Monitor and manage">
            <div className="space-y-2">
              <p>Use the VESSA dashboard to monitor and manage security incidents:</p>
              
              <ul className="list-disc pl-5 space-y-1 text-sm">
                <li>View all incidents detected from your raw event data</li>
                <li>Assign incidents to team members</li>
                <li>Track incident resolution progress</li>
                <li>Generate reports and analytics</li>
              </ul>
            </div>
          </Step>
        </Steps>
      </CardContent>
    </Card>
  );
}