import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Shield, Zap, Layers, CheckCircle2, AlertTriangle, Terminal, Code, Rocket } from "lucide-react";

export function WAFDeploymentGuide() {
    return (
        <div className="space-y-6">
            {/* Hero Section */}
            <Card className="border-2 border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
                <CardHeader>
                    <div className="flex items-center gap-3 mb-2">
                        <Shield className="h-8 w-8 text-primary" />
                        <div>
                            <CardTitle className="text-2xl">VESSA Web Application Firewall</CardTitle>
                            <CardDescription className="text-base">
                                Drop-in protection for ANY application with ML-powered threat detection
                            </CardDescription>
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="flex items-start gap-3">
                            <Zap className="h-5 w-5 text-green-500 mt-1" />
                            <div>
                                <p className="font-semibold">Real-time Blocking</p>
                                <p className="text-sm text-muted-foreground">Inline request interception</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <Layers className="h-5 w-5 text-blue-500 mt-1" />
                            <div>
                                <p className="font-semibold">Zero Code Changes</p>
                                <p className="text-sm text-muted-foreground">Reverse proxy mode</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <CheckCircle2 className="h-5 w-5 text-purple-500 mt-1" />
                            <div>
                                <p className="font-semibold">95%+ Accuracy</p>
                                <p className="text-sm text-muted-foreground">ML-powered detection</p>
                            </div>
                        </div>
                    </div>
                    <Alert>
                        <Rocket className="h-4 w-4" />
                        <AlertTitle>NEW: Drop-in WAF Protection!</AlertTitle>
                        <AlertDescription>
                            Protect Node.js, Python, Java, PHP, Go, Ruby, or any web application with a single command. No code changes required.
                        </AlertDescription>
                    </Alert>
                </CardContent>
            </Card>

            {/* Deployment Modes */}
            <Card>
                <CardHeader>
                    <CardTitle>Choose Your Deployment Mode</CardTitle>
                    <CardDescription>
                        Select the integration method that best fits your use case
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Tabs defaultValue="reverse-proxy" className="w-full">
                        <TabsList className="grid w-full grid-cols-4">
                            <TabsTrigger value="reverse-proxy">
                                <Badge variant="default" className="mr-2">⭐</Badge>
                                Reverse Proxy
                            </TabsTrigger>
                            <TabsTrigger value="docker">Docker</TabsTrigger>
                            <TabsTrigger value="fastapi">FastAPI</TabsTrigger>
                            <TabsTrigger value="flask">Flask</TabsTrigger>
                        </TabsList>

                        {/* Reverse Proxy Mode */}
                        <TabsContent value="reverse-proxy" className="space-y-4 mt-4">
                            <Alert>
                                <Shield className="h-4 w-4" />
                                <AlertTitle>Recommended: Zero Code Changes</AlertTitle>
                                <AlertDescription>
                                    Protect ANY backend application (Node.js, Python, Java, PHP, Go, Ruby, etc.) without modifying your code.
                                </AlertDescription>
                            </Alert>

                            <div className="space-y-4">
                                <div>
                                    <h4 className="text-lg font-semibold mb-2 flex items-center gap-2">
                                        <Terminal className="h-5 w-5" />
                                        Quick Start (1 Minute)
                                    </h4>
                                    <div className="bg-muted p-4 rounded-md">
                                        <pre className="text-xs overflow-x-auto"><code>{`# Start VESSA WAF in front of your application
cd firewall-app
python -m services.waf.reverse_proxy \\
  --backend http://localhost:3000 \\
  --port 8080 \\
  --mode block`}</code></pre>
                                    </div>
                                    <p className="text-sm text-muted-foreground mt-2">
                                        Your app is now protected at <code>http://localhost:8080</code>
                                    </p>
                                </div>

                                <div>
                                    <h4 className="text-lg font-semibold mb-2">Architecture</h4>
                                    <div className="bg-muted p-4 rounded-md">
                                        <pre className="text-xs"><code>{`Internet → VESSA WAF (8080) → Your Application (3000)
              ↓
        Block or Allow`}</code></pre>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="text-lg font-semibold mb-2">Test Protection</h4>
                                    <div className="bg-muted p-4 rounded-md">
                                        <pre className="text-xs overflow-x-auto"><code>{`# Test SQL Injection Protection (should be blocked)
curl "http://localhost:8080/search?q=' OR '1'='1"

# Response:
{
  "error": "Forbidden",
  "message": "Request blocked by WAF",
  "threat_type": "sql_injection",
  "request_id": "a1b2c3d4"
}

# Normal request (should work)
curl "http://localhost:8080/api/data"

# Response headers include:
# X-WAF-Status: allowed
# X-WAF-Threat-Score: 0.0
# X-WAF-Analysis-Time: 5.23ms`}</code></pre>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="text-lg font-semibold mb-2">WAF Modes</h4>
                                    <div className="grid grid-cols-2 gap-3">
                                        <div className="bg-muted p-3 rounded-md">
                                            <p className="font-semibold text-sm">Block Mode (Production)</p>
                                            <code className="text-xs">--mode block</code>
                                            <p className="text-xs text-muted-foreground mt-1">Blocks malicious requests</p>
                                        </div>
                                        <div className="bg-muted p-3 rounded-md">
                                            <p className="font-semibold text-sm">Log Mode (Testing)</p>
                                            <code className="text-xs">--mode log</code>
                                            <p className="text-xs text-muted-foreground mt-1">Logs threats, doesn't block</p>
                                        </div>
                                        <div className="bg-muted p-3 rounded-md">
                                            <p className="font-semibold text-sm">Challenge Mode</p>
                                            <code className="text-xs">--mode challenge</code>
                                            <p className="text-xs text-muted-foreground mt-1">Presents CAPTCHA for suspicious</p>
                                        </div>
                                        <div className="bg-muted p-3 rounded-md">
                                            <p className="font-semibold text-sm">Simulate Mode (Dev)</p>
                                            <code className="text-xs">--mode simulate</code>
                                            <p className="text-xs text-muted-foreground mt-1">Dry-run, shows what would block</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </TabsContent>

                        {/* Docker Mode */}
                        <TabsContent value="docker" className="space-y-4 mt-4">
                            <Alert>
                                <Rocket className="h-4 w-4" />
                                <AlertTitle>One-Command Protection</AlertTitle>
                                <AlertDescription>
                                    Deploy WAF as a container to protect your existing infrastructure
                                </AlertDescription>
                            </Alert>

                            <div className="space-y-4">
                                <div>
                                    <h4 className="text-lg font-semibold mb-2">Build WAF Container</h4>
                                    <div className="bg-muted p-4 rounded-md">
                                        <pre className="text-xs overflow-x-auto"><code>{`cd firewall-app
docker build -f Dockerfile.waf -t vessa-waf .`}</code></pre>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="text-lg font-semibold mb-2">Run WAF Container</h4>
                                    <div className="bg-muted p-4 rounded-md">
                                        <pre className="text-xs overflow-x-auto"><code>{`docker run -d \\
  --name vessa-waf \\
  -p 8080:8080 \\
  -e BACKEND_URL=http://yourapp:3000 \\
  -e WAF_MODE=block \\
  -e WAF_ENABLED=true \\
  -v ./waf_config.yaml:/app/waf_config.yaml \\
  vessa-waf

# Check status
docker logs vessa-waf
curl http://localhost:8080/waf/health`}</code></pre>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="text-lg font-semibold mb-2">Docker Compose (Full Stack)</h4>
                                    <div className="bg-muted p-4 rounded-md">
                                        <pre className="text-xs overflow-x-auto"><code>{`# docker-compose.waf.yml
version: '3.8'

services:
  # Your application
  backend:
    image: your-app:latest
    expose:
      - "3000"
  
  # VESSA WAF
  waf:
    image: vessa-waf:latest
    ports:
      - "80:8080"
    environment:
      - BACKEND_URL=http://backend:3000
      - WAF_MODE=block
    depends_on:
      - backend

# Start: docker-compose -f docker-compose.waf.yml up -d`}</code></pre>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="text-lg font-semibold mb-2">Kubernetes Deployment</h4>
                                    <div className="bg-muted p-4 rounded-md">
                                        <pre className="text-xs overflow-x-auto"><code>{`apiVersion: apps/v1
kind: Deployment
metadata:
  name: vessa-waf
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: waf
        image: vessa-waf:latest
        ports:
        - containerPort: 8080
        env:
        - name: BACKEND_URL
          value: "http://backend-service:3000"
        - name: WAF_MODE
          value: "block"
---
apiVersion: v1
kind: Service
metadata:
  name: vessa-waf
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8080`}</code></pre>
                                    </div>
                                </div>
                            </div>
                        </TabsContent>

                        {/* FastAPI Mode */}
                        <TabsContent value="fastapi" className="space-y-4 mt-4">
                            <Alert>
                                <Code className="h-4 w-4" />
                                <AlertTitle>One Line Integration</AlertTitle>
                                <AlertDescription>
                                    Add WAF protection to your FastAPI app with a single line of code
                                </AlertDescription>
                            </Alert>

                            <div className="space-y-4">
                                <div>
                                    <h4 className="text-lg font-semibold mb-2">Installation</h4>
                                    <div className="bg-muted p-4 rounded-md">
                                        <pre className="text-xs overflow-x-auto"><code>{`# Install dependencies
pip install -r requirements.txt
cd ../absolution && pip install -e .`}</code></pre>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="text-lg font-semibold mb-2">Add to Your FastAPI App</h4>
                                    <div className="bg-muted p-4 rounded-md">
                                        <pre className="text-xs overflow-x-auto"><code>{`from fastapi import FastAPI
from services.waf import WAFMiddleware, WAFConfig

app = FastAPI()

# Add WAF middleware - that's it!
app.add_middleware(WAFMiddleware, config=WAFConfig())

# All your routes are now protected
@app.get("/api/data")
async def get_data():
    return {"data": "secure"}

@app.post("/api/login")
async def login(username: str, password: str):
    # SQL injection attempts are blocked automatically
    # No manual input validation needed!
    return {"token": "abc123"}`}</code></pre>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="text-lg font-semibold mb-2">Custom Configuration</h4>
                                    <div className="bg-muted p-4 rounded-md">
                                        <pre className="text-xs overflow-x-auto"><code>{`from services.waf import WAFMiddleware, WAFConfig
from services.waf.waf_config import BlockingMode

# Custom configuration
config = WAFConfig(
    mode=BlockingMode.BLOCK,
    enabled=True,
    log_blocked_requests=True,
    thresholds={
        "block": 0.80,     # Higher threshold
        "challenge": 0.60,
        "log": 0.30
    },
    ip_config={
        "whitelist": ["10.0.0.0/8"],  # Corporate network
        "blacklist": ["203.0.113.0/24"]
    }
)

app.add_middleware(WAFMiddleware, config=config)

# Check WAF status
@app.get("/waf/stats")
async def waf_stats(waf=Depends(get_waf_engine)):
    return waf.get_stats()`}</code></pre>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="text-lg font-semibold mb-2">Response Headers</h4>
                                    <p className="text-sm text-muted-foreground mb-2">
                                        WAF automatically adds headers to all responses:
                                    </p>
                                    <div className="bg-muted p-4 rounded-md">
                                        <pre className="text-xs overflow-x-auto"><code>{`X-WAF-Status: allowed | blocked | challenged
X-WAF-Threat-Score: 0.0 - 1.0
X-WAF-Threat-Type: sql_injection | xss | safe | etc.
X-WAF-Analysis-Time: 12.5ms`}</code></pre>
                                    </div>
                                </div>
                            </div>
                        </TabsContent>

                        {/* Flask Mode */}
                        <TabsContent value="flask" className="space-y-4 mt-4">
                            <Alert>
                                <Code className="h-4 w-4" />
                                <AlertTitle>Flask Integration</AlertTitle>
                                <AlertDescription>
                                    Protect your Flask application with two lines of code
                                </AlertDescription>
                            </Alert>

                            <div className="space-y-4">
                                <div>
                                    <h4 className="text-lg font-semibold mb-2">Full App Protection</h4>
                                    <div className="bg-muted p-4 rounded-md">
                                        <pre className="text-xs overflow-x-auto"><code>{`from flask import Flask
from services.waf.integrations import FlaskWAF
from services.waf import WAFConfig

app = Flask(__name__)

# Protect entire app with two lines
waf = FlaskWAF(app, config=WAFConfig())

# All routes are now protected
@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/api/data')
def get_data():
    return {'data': [1, 2, 3, 4, 5]}

@app.route('/api/login', methods=['POST'])
def login():
    # SQL injection and XSS attempts blocked automatically
    username = request.form.get('username')
    password = request.form.get('password')
    return {'token': 'abc123'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)`}</code></pre>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="text-lg font-semibold mb-2">Per-Route Protection (Decorator)</h4>
                                    <div className="bg-muted p-4 rounded-md">
                                        <pre className="text-xs overflow-x-auto"><code>{`from flask import Flask
from services.waf.integrations import FlaskWAF

app = Flask(__name__)
waf = FlaskWAF()  # Don't pass app - we'll use decorator

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/api/sensitive-data')
@waf.protect  # Protect only this route
def get_sensitive_data():
    return {'secret': 'data'}

@app.route('/api/public')
def public_data():
    return {'public': 'data'}  # Not protected`}</code></pre>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="text-lg font-semibold mb-2">WSGI Middleware (Universal)</h4>
                                    <div className="bg-muted p-4 rounded-md">
                                        <pre className="text-xs overflow-x-auto"><code>{`from flask import Flask
from services.waf.integrations import WSGIWAFMiddleware

app = Flask(__name__)

# Wrap WSGI app (works with Flask, Django, Pyramid, etc.)
app.wsgi_app = WSGIWAFMiddleware(app.wsgi_app)

# All routes protected via WSGI middleware
@app.route('/')
def index():
    return 'Protected by VESSA WAF!'`}</code></pre>
                                    </div>
                                </div>

                                <div>
                                    <h4 className="text-lg font-semibold mb-2">Get WAF Statistics</h4>
                                    <div className="bg-muted p-4 rounded-md">
                                        <pre className="text-xs overflow-x-auto"><code>{`# Add stats endpoint
@app.route('/waf/stats')
def waf_stats():
    return jsonify(waf.get_stats())

# Example response:
{
  "total_requests": 1523,
  "blocked_requests": 47,
  "allowed_requests": 1476,
  "cache_hits": 892,
  "avg_analysis_time_ms": 12.5
}`}</code></pre>
                                    </div>
                                </div>
                            </div>
                        </TabsContent>
                    </Tabs>
                </CardContent>
            </Card>

            {/* Configuration */}
            <Card>
                <CardHeader>
                    <CardTitle>WAF Configuration</CardTitle>
                    <CardDescription>Customize WAF behavior with YAML configuration</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <h4 className="text-lg font-semibold mb-2">Create waf_config.yaml</h4>
                        <div className="bg-muted p-4 rounded-md">
                            <pre className="text-xs overflow-x-auto"><code>{`# WAF Mode
mode: block  # block, log, challenge, simulate

# Threat Thresholds (0.0 to 1.0)
thresholds:
  block: 0.75      # Block if threat >= 75%
  challenge: 0.50  # Challenge if >= 50%
  log: 0.25        # Log if >= 25%

# Analysis Configuration
analysis:
  static_enabled: true     # Fast pattern matching
  ml_enabled: true         # ML detection
  ml_async: true           # Run ML async (faster)
  cache_enabled: true      # Cache results
  cache_ttl: 300           # 5 minutes

# IP Management
ip_config:
  whitelist:
    - 127.0.0.1
    - 10.0.0.0/8          # Private network
  blacklist:
    - 203.0.113.0/24      # Known bad IPs
  geo_block_countries:
    - CN  # Block China (optional)
    - RU  # Block Russia (optional)

# Rate Limiting
rate_limit:
  enabled: true
  requests_per_minute: 60
  requests_per_hour: 1000

# Excluded Paths (bypass WAF)
excluded_paths:
  - /health
  - /metrics
  - /static
  - /_next/static        # Next.js
  - /wp-admin/admin-ajax.php  # WordPress`}</code></pre>
                        </div>
                    </div>

                    <div>
                        <h4 className="text-lg font-semibold mb-2">Load Configuration</h4>
                        <div className="bg-muted p-4 rounded-md">
                            <pre className="text-xs overflow-x-auto"><code>{`# Reverse Proxy Mode
python -m services.waf.reverse_proxy \\
  --backend http://localhost:3000 \\
  --config waf_config.yaml

# Or in code
from services.waf import WAFConfig
config = WAFConfig.from_file('waf_config.yaml')
app.add_middleware(WAFMiddleware, config=config)`}</code></pre>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Protection Features */}
            <Card>
                <CardHeader>
                    <CardTitle>What VESSA WAF Protects Against</CardTitle>
                    <CardDescription>Comprehensive threat detection and blocking</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <div className="flex items-center gap-2">
                                <CheckCircle2 className="h-4 w-4 text-green-500" />
                                <span className="font-semibold">SQL Injection</span>
                            </div>
                            <p className="text-sm text-muted-foreground ml-6">
                                15+ patterns including encoded variants, UNION, OR 1=1, etc.
                            </p>
                        </div>
                        <div className="space-y-2">
                            <div className="flex items-center gap-2">
                                <CheckCircle2 className="h-4 w-4 text-green-500" />
                                <span className="font-semibold">Cross-Site Scripting (XSS)</span>
                            </div>
                            <p className="text-sm text-muted-foreground ml-6">
                                Detects script tags, event handlers, javascript:, eval(), etc.
                            </p>
                        </div>
                        <div className="space-y-2">
                            <div className="flex items-center gap-2">
                                <CheckCircle2 className="h-4 w-4 text-green-500" />
                                <span className="font-semibold">Path Traversal</span>
                            </div>
                            <p className="text-sm text-muted-foreground ml-6">
                                25+ patterns including ../, encoded variants, sensitive paths
                            </p>
                        </div>
                        <div className="space-y-2">
                            <div className="flex items-center gap-2">
                                <CheckCircle2 className="h-4 w-4 text-green-500" />
                                <span className="font-semibold">Command Injection</span>
                            </div>
                            <p className="text-sm text-muted-foreground ml-6">
                                Shell commands, pipes, redirects, backticks, $(), etc.
                            </p>
                        </div>
                        <div className="space-y-2">
                            <div className="flex items-center gap-2">
                                <CheckCircle2 className="h-4 w-4 text-green-500" />
                                <span className="font-semibold">NoSQL Injection</span>
                            </div>
                            <p className="text-sm text-muted-foreground ml-6">
                                MongoDB operators: $ne, $gt, $where, $regex, etc.
                            </p>
                        </div>
                        <div className="space-y-2">
                            <div className="flex items-center gap-2">
                                <CheckCircle2 className="h-4 w-4 text-green-500" />
                                <span className="font-semibold">Out-of-Distribution Attacks</span>
                            </div>
                            <p className="text-sm text-muted-foreground ml-6">
                                ML-based detection of novel, unknown attack patterns
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Performance & Monitoring */}
            <Card>
                <CardHeader>
                    <CardTitle>Monitoring & Performance</CardTitle>
                    <CardDescription>Track WAF performance and statistics</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <h4 className="text-lg font-semibold mb-2">Get WAF Statistics</h4>
                        <div className="bg-muted p-4 rounded-md">
                            <pre className="text-xs overflow-x-auto"><code>{`curl http://localhost:8080/waf/stats

{
  "total_requests": 1523,
  "blocked_requests": 47,
  "allowed_requests": 1476,
  "challenged_requests": 0,
  "cache_hits": 892,
  "avg_analysis_time_ms": 12.5
}`}</code></pre>
                        </div>
                    </div>

                    <div>
                        <h4 className="text-lg font-semibold mb-2">Performance Metrics</h4>
                        <div className="grid grid-cols-3 gap-3">
                            <div className="bg-muted p-3 rounded-md">
                                <p className="font-semibold text-sm">Static Analysis</p>
                                <p className="text-xl font-bold text-primary">5-10ms</p>
                                <p className="text-xs text-muted-foreground">Pattern matching</p>
                            </div>
                            <div className="bg-muted p-3 rounded-md">
                                <p className="font-semibold text-sm">ML Async</p>
                                <p className="text-xl font-bold text-primary">10-20ms</p>
                                <p className="text-xs text-muted-foreground">Background ML</p>
                            </div>
                            <div className="bg-muted p-3 rounded-md">
                                <p className="font-semibold text-sm">ML Sync</p>
                                <p className="text-xl font-bold text-primary">50-100ms</p>
                                <p className="text-xs text-muted-foreground">Full analysis</p>
                            </div>
                        </div>
                    </div>

                    <Alert>
                        <AlertTriangle className="h-4 w-4" />
                        <AlertTitle>Best Practice: Start with Log Mode</AlertTitle>
                        <AlertDescription>
                            Test with <code className="text-xs">--mode log</code> for a week to tune thresholds, then switch to <code className="text-xs">--mode block</code> for production.
                        </AlertDescription>
                    </Alert>
                </CardContent>
            </Card>
        </div>
    );
}

