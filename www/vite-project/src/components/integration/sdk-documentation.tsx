import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, Github } from "lucide-react";

export function SDKDocumentation() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Integration SDKs</h1>
          <p className="text-muted-foreground">
            Integrate VESSA security incident management into your applications
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="flex items-center gap-2" onClick={() => window.open('https://github.com/vessa/sdk-examples', '_blank')}>
            <Github className="h-4 w-4" />
            Example Projects
          </Button>
        </div>
      </div>

      <Tabs defaultValue="javascript">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="javascript">JavaScript SDK</TabsTrigger>
          <TabsTrigger value="python">Python SDK</TabsTrigger>
        </TabsList>
        
        <TabsContent value="javascript" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>JavaScript SDK</CardTitle>
              <CardDescription>
                Integrate VESSA with your JavaScript or TypeScript applications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold">Installation</h3>
                <div className="bg-muted p-4 rounded-md mt-2">
                  <pre className="text-sm"><code>npm install vessa-sdk</code></pre>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold">Quick Start</h3>
                <div className="bg-muted p-4 rounded-md mt-2">
                  <pre className="text-sm overflow-x-auto">
                    <code>{`import { VessaClient } from 'vessa-sdk';

// Initialize the client with your API key
const client = new VessaClient({
  apiKey: 'your-api-key',
});

// Forward requests to the VESSA API
async function reportIncident() {
  try {
    // Simply forward the request to the API endpoint
    const response = await client.request('POST', '/api/v1/incidents', {
      // Raw data to be sent to the backend
      "event_data": {
        "source_ip": "192.168.1.1",
        "timestamp": "2023-07-15T14:22:31Z",
        "request_path": "/admin",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "headers": {
          "authorization": "Bearer ***",
          "content-type": "application/json"
        },
        "payload": "{\"action\":\"get_users\"}"
      }
    });
    
    console.log('Request sent, response:', response);
  } catch (error) {
    console.error('Failed to send request:', error);
  }
}

// Get all incidents
async function getIncidents() {
  try {
    // Simply forward the request to the API endpoint with query parameters
    const result = await client.request('GET', '/api/v1/incidents', null, {
      page: 1,
      page_size: 20
    });
    console.log(\`Found \${result.total} incidents, showing \${result.items.length}\`);
  } catch (error) {
    console.error('Failed to fetch incidents:', error);
  }
}`}</code>
                  </pre>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold">Error Handling</h3>
                <div className="bg-muted p-4 rounded-md mt-2">
                  <pre className="text-sm overflow-x-auto">
                    <code>{`try {
  await client.request('POST', '/api/v1/incidents', {
    title: 'Test incident'
    // Missing required fields will cause an error
  });
} catch (error) {
  if (error.status === 400) {
    console.error('Validation error:', error.message);
  } else if (error.status === 401) {
    console.error('Authentication error. Check your API key.');
  } else if (error.status === 403) {
    console.error('Permission denied. Your plan may not allow this operation.');
  } else {
    console.error('An unexpected error occurred:', error);
  }
}`}</code>
                  </pre>
                </div>
              </div>
              
              <div className="flex justify-end">
                <Button className="flex items-center gap-2" onClick={() => window.open('/sdk/vessa-sdk-latest.zip', '_blank')}>
                  <Download className="h-4 w-4" />
                  Download SDK
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="python" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Python SDK</CardTitle>
              <CardDescription>
                Integrate VESSA with your Python applications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold">Installation</h3>
                <div className="bg-muted p-4 rounded-md mt-2">
                  <pre className="text-sm"><code>pip install vessa-sdk</code></pre>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold">Quick Start</h3>
                <div className="bg-muted p-4 rounded-md mt-2">
                  <pre className="text-sm overflow-x-auto">
                    <code>{`from vessa_sdk import VessaClient

# Initialize the client with your API key
client = VessaClient(
    api_key='your-api-key'
)

# Report a new incident
def report_incident():
    try:
        # Simply forward the request to the API endpoint
        response = client.request(
            method="POST",
            path="/api/v1/incidents",
            data={
                # Raw data to be sent to the backend
                "event_data": {
                    "source_ip": "192.168.1.1",
                    "timestamp": "2023-07-15T14:22:31Z",
                    "request_path": "/admin",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "headers": {
                        "authorization": "Bearer ***",
                        "content-type": "application/json"
                    },
                    "payload": "{\"action\":\"get_users\"}"
                }
            }
        )
        
        print(f"Request sent, response: {response}")
    except Exception as e:
        print(f"Failed to send request: {e}")

# Get all incidents
def get_incidents():
    try:
        # Simply forward the request to the API endpoint with query parameters
        result = client.request(
            method="GET",
            path="/api/v1/incidents",
            params={"page": 1, "page_size": 20}
        )
        print(f"Found {result['total']} incidents, showing {len(result['items'])}")
    except Exception as e:
        print(f"Failed to fetch incidents: {e}")
`}</code>
                  </pre>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold">Error Handling</h3>
                <div className="bg-muted p-4 rounded-md mt-2">
                  <pre className="text-sm overflow-x-auto">
                    <code>{`try:
    client.request(
        method="POST",
        path="/api/v1/incidents",
        data={"title": "Test incident"}
        # Missing required fields will cause an error
    )
except Exception as e:
    if hasattr(e, 'status_code'):
        if e.status_code == 400:
            print(f"Validation error: {e}")
        elif e.status_code == 401:
            print("Authentication error. Check your API key.")
        elif e.status_code == 403:
            print("Permission denied. Your plan may not allow this operation.")
        else:
            print(f"An unexpected error occurred: {e}")
    else:
        print(f"Client error: {e}")
`}</code>
                  </pre>
                </div>
              </div>
              
              <div className="flex justify-end">
                <Button className="flex items-center gap-2" onClick={() => window.open('/sdk/vessa-python-sdk-latest.zip', '_blank')}>
                  <Download className="h-4 w-4" />
                  Download SDK
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}