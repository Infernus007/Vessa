import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Copy, Check, Terminal, Code, Book, Puzzle } from 'lucide-react';

export default function SDKIntegrationPage() {
  const [copied, setCopied] = React.useState<string | null>(null);

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopied(key);
    setTimeout(() => setCopied(null), 2000);
  };

  const installationCommands = {
    npm: 'npm install @vessa/sdk',
    yarn: 'yarn add @vessa/sdk',
    pnpm: 'pnpm add @vessa/sdk'
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">SDK Integration</h1>
        <p className="text-muted-foreground">Integrate VESSA security monitoring into your application</p>
      </div>

      {/* Quick Start */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Start</CardTitle>
          <CardDescription>Get started with VESSA SDK in your application</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium mb-2">1. Install the SDK</h3>
              <Tabs defaultValue="npm" className="w-full">
                <TabsList>
                  <TabsTrigger value="npm">npm</TabsTrigger>
                  <TabsTrigger value="yarn">yarn</TabsTrigger>
                  <TabsTrigger value="pnpm">pnpm</TabsTrigger>
                </TabsList>
                {Object.entries(installationCommands).map(([pkg, command]) => (
                  <TabsContent key={pkg} value={pkg}>
                    <div className="relative">
                      <pre className="bg-secondary p-4 rounded-md font-mono text-sm">
                        {command}
                      </pre>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="absolute right-2 top-2"
                        onClick={() => handleCopy(command, pkg)}
                      >
                        {copied === pkg ? (
                          <Check className="h-4 w-4" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </TabsContent>
                ))}
              </Tabs>
            </div>

            <div>
              <h3 className="text-sm font-medium mb-2">2. Initialize the SDK</h3>
              <div className="relative">
                <pre className="bg-secondary p-4 rounded-md font-mono text-sm">
{`import { VessaSDK } from '@vessa/sdk';

const vessa = new VessaSDK({
  apiKey: 'your-api-key',
  environment: 'production',
  options: {
    enableRealTimeAlerts: true,
    logLevel: 'info'
  }
});`}
                </pre>
                <Button
                  variant="ghost"
                  size="sm"
                  className="absolute right-2 top-2"
                  onClick={() => handleCopy(`import { VessaSDK } from '@vessa/sdk';

const vessa = new VessaSDK({
  apiKey: 'your-api-key',
  environment: 'production',
  options: {
    enableRealTimeAlerts: true,
    logLevel: 'info'
  }
});`, 'init')}
                >
                  {copied === 'init' ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Integration Guides */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <Terminal className="h-6 w-6 mb-2 text-primary" />
            <CardTitle>CLI Integration</CardTitle>
            <CardDescription>Integrate with your CI/CD pipeline</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Use our CLI tools to automate security scanning and monitoring in your deployment pipeline.
            </p>
            <Button variant="secondary" className="w-full">
              View CLI Guide
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <Code className="h-6 w-6 mb-2 text-primary" />
            <CardTitle>API Reference</CardTitle>
            <CardDescription>Explore the SDK API documentation</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Comprehensive API documentation with examples and use cases for all SDK features.
            </p>
            <Button variant="secondary" className="w-full">
              View API Docs
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <Book className="h-6 w-6 mb-2 text-primary" />
            <CardTitle>Examples</CardTitle>
            <CardDescription>Ready-to-use code examples</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Browse our collection of example integrations and implementations.
            </p>
            <Button variant="secondary" className="w-full">
              View Examples
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Features */}
      <Card>
        <CardHeader>
          <CardTitle>SDK Features</CardTitle>
          <CardDescription>Key capabilities of the VESSA SDK</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="flex gap-3">
              <Puzzle className="h-5 w-5 text-primary flex-shrink-0" />
              <div>
                <h4 className="text-sm font-medium">Real-time Monitoring</h4>
                <p className="text-sm text-muted-foreground">
                  Monitor security events and threats in real-time with automatic alerts.
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <Puzzle className="h-5 w-5 text-primary flex-shrink-0" />
              <div>
                <h4 className="text-sm font-medium">Threat Detection</h4>
                <p className="text-sm text-muted-foreground">
                  Advanced threat detection with ML-powered analysis.
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <Puzzle className="h-5 w-5 text-primary flex-shrink-0" />
              <div>
                <h4 className="text-sm font-medium">Custom Rules</h4>
                <p className="text-sm text-muted-foreground">
                  Create and manage custom security rules and policies.
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <Puzzle className="h-5 w-5 text-primary flex-shrink-0" />
              <div>
                <h4 className="text-sm font-medium">Analytics</h4>
                <p className="text-sm text-muted-foreground">
                  Detailed security analytics and reporting capabilities.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 