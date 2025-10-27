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
  baseUrl: 'https://api.vessa.com' // Optional, defaults to production
});

// Analyze a request for threats
async function analyzeRequest(requestData) {
  try {
    const analysis = await client.analyzeRequest({
      client_ip: requestData.ip,
      request_path: requestData.path,
      request_method: requestData.method,
      request_headers: requestData.headers,
      request_body: requestData.body,
      user_agent: requestData.userAgent
    });
    
    console.log('Threat Score:', analysis.threat_score);
    console.log('Threat Type:', analysis.threat_type);
    console.log('Should Block:', analysis.should_block);
    console.log('Findings:', analysis.findings);
    
    return analysis;
  } catch (error) {
    console.error('Analysis failed:', error);
    throw error;
  }
}

// Example: Analyze a suspicious login attempt
const suspiciousRequest = {
  ip: '185.220.101.1',
  path: '/api/login',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
  },
  body: '{"username": "admin", "password": "admin123"}',
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
};

const result = await analyzeRequest(suspiciousRequest);
if (result.should_block) {
  console.log('🚨 BLOCKING REQUEST - High threat detected!');
  // Block the request in your application
}`}</code>
                  </pre>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold">Error Handling</h3>
                <div className="bg-muted p-4 rounded-md mt-2">
                  <pre className="text-sm overflow-x-auto">
                    <code>{`try {
  const analysis = await client.analyzeRequest({
    client_ip: '192.168.1.1',
    request_path: '/api/login',
    request_method: 'POST',
    request_headers: { 'Content-Type': 'application/json' },
    request_body: '{"username": "admin"}',
    user_agent: 'Mozilla/5.0'
  });
  
  // Handle the analysis result
  if (analysis.threat_score > 0.8) {
    console.log('🚨 High threat detected - blocking request');
    return { blocked: true, reason: 'High threat score' };
  } else if (analysis.threat_score > 0.5) {
    console.log('⚠️ Medium threat detected - logging for review');
    return { blocked: false, logged: true };
  } else {
    console.log('✅ Request appears safe');
    return { blocked: false, logged: false };
  }
} catch (error) {
  if (error.status === 400) {
    console.error('Invalid request data:', error.message);
  } else if (error.status === 401) {
    console.error('Authentication failed. Check your API key.');
  } else if (error.status === 429) {
    console.error('Rate limit exceeded. Please wait before retrying.');
  } else {
    console.error('Analysis failed:', error.message);
    // Fallback: allow request but log the error
    return { blocked: false, error: true };
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
    api_key='your-api-key',
    base_url='https://api.vessa.com'  # Optional, defaults to production
)

# Analyze a request for threats
def analyze_request(request_data):
    try:
        analysis = client.analyze_request(
            client_ip=request_data['ip'],
            request_path=request_data['path'],
            request_method=request_data['method'],
            request_headers=request_data['headers'],
            request_body=request_data['body'],
            user_agent=request_data['user_agent']
        )
        
        print(f"Threat Score: {analysis['threat_score']}")
        print(f"Threat Type: {analysis['threat_type']}")
        print(f"Should Block: {analysis['should_block']}")
        print(f"Findings: {analysis['findings']}")
        
        return analysis
    except Exception as e:
        print(f"Analysis failed: {e}")
        raise

# Example: Analyze a suspicious SQL injection attempt
suspicious_request = {
    'ip': '192.168.1.100',
    'path': '/api/users?search=admin OR 1=1',
    'method': 'GET',
    'headers': {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    },
    'body': '',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

result = analyze_request(suspicious_request)
if result['should_block']:
    print("🚨 BLOCKING REQUEST - High threat detected!")
    # Block the request in your application`}</code>
                  </pre>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold">Error Handling</h3>
                <div className="bg-muted p-4 rounded-md mt-2">
                  <pre className="text-sm overflow-x-auto">
                    <code>{`try:
    analysis = client.analyze_request(
        client_ip='192.168.1.1',
        request_path='/api/login',
        request_method='POST',
        request_headers={'Content-Type': 'application/json'},
        request_body='{"username": "admin"}',
        user_agent='Mozilla/5.0'
    )
    
    # Handle the analysis result
    if analysis['threat_score'] > 0.8:
        print("🚨 High threat detected - blocking request")
        return {"blocked": True, "reason": "High threat score"}
    elif analysis['threat_score'] > 0.5:
        print("⚠️ Medium threat detected - logging for review")
        return {"blocked": False, "logged": True}
    else:
        print("✅ Request appears safe")
        return {"blocked": False, "logged": False}
        
except Exception as e:
    if hasattr(e, 'status_code'):
        if e.status_code == 400:
            print(f"Invalid request data: {e}")
        elif e.status_code == 401:
            print("Authentication failed. Check your API key.")
        elif e.status_code == 429:
            print("Rate limit exceeded. Please wait before retrying.")
        else:
            print(f"Analysis failed: {e}")
    else:
        print(f"Client error: {e}")
    
    # Fallback: allow request but log the error
    return {"blocked": False, "error": True}`}</code>
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