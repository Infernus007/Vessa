import { useState} from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useAuthStore } from '@/lib/store/auth-store';
import { authApi } from '@/lib/api/auth';
import { Copy, RefreshCw, XCircle, Download, Code, Check } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { toast } from "sonner";

export function ApiKeyManager() {
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const { activeApiKey, setActiveApiKey } = useAuthStore();

  // Fetch API key on component mount if not already in store
  const { data, isLoading: isLoadingKey } = useQuery({
    queryKey: ['apiKey'],
    queryFn: authApi.getApiKey,
    // Only fetch if we don't already have an API key
    enabled: !activeApiKey
  });

  // Set API key in store if we have one
  if (data && !activeApiKey) {
    setActiveApiKey(data);
  }

  const regenerateKeyMutation = useMutation({
    mutationFn: authApi.regenerateApiKey,
    onSuccess: (data) => {
      setActiveApiKey(data);
      setError(null);
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to regenerate API key');
    },
  });

  const revokeKeyMutation = useMutation({
    mutationFn: authApi.revokeApiKey,
    onSuccess: () => {
      setActiveApiKey(null);
      setError(null);
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to revoke API key');
    },
  });

  const copyToClipboard = async () => {
    if (activeApiKey?.key) {
      try {
        await navigator.clipboard.writeText(activeApiKey.key);
        setCopied(true);
        toast.success('API key copied to clipboard');
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        setError('Failed to copy API key to clipboard');
        toast.error('Failed to copy API key');
      }
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>API Key Management</CardTitle>
        <CardDescription>
          Generate and manage API keys to integrate with VESSA services
        </CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {activeApiKey?.key ? (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs font-mono bg-muted px-2 py-1 rounded-md flex-1 overflow-hidden">
                <span className="truncate">{activeApiKey.key}</span>
              </Badge>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="outline" size="icon" onClick={copyToClipboard} className={copied ? "text-green-500" : ""}>
                      {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{copied ? 'Copied!' : 'Copy API key'}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-2">
              <Button 
                variant="outline" 
                onClick={() => regenerateKeyMutation.mutate()} 
                disabled={regenerateKeyMutation.isPending}
                className="flex items-center gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                {regenerateKeyMutation.isPending ? 'Regenerating...' : 'Regenerate Key'}
              </Button>
              <Button 
                variant="destructive" 
                onClick={() => revokeKeyMutation.mutate()} 
                disabled={revokeKeyMutation.isPending}
                className="flex items-center gap-2"
              >
                <XCircle className="h-4 w-4" />
                {revokeKeyMutation.isPending ? 'Revoking...' : 'Revoke Key'}
              </Button>
            </div>
          </div>
        ) : (
          <div className="text-center py-4">
            {isLoadingKey ? (
              <p>Loading your API key...</p>
            ) : (
              <>
                <p className="mb-4">You don't have an active API key.</p>
                <Button 
                  onClick={() => regenerateKeyMutation.mutate()} 
                  disabled={regenerateKeyMutation.isPending}
                >
                  {regenerateKeyMutation.isPending ? 'Generating...' : 'Generate API Key'}
                </Button>
              </>
            )}
          </div>
        )}
      </CardContent>
      
      {activeApiKey?.key && (
        <CardFooter className="flex-col items-start">
          <h4 className="text-sm font-semibold mb-2">Integration Options</h4>
          <Tabs defaultValue="js" className="w-full">
            <TabsList className="grid grid-cols-2">
              <TabsTrigger value="js">JavaScript</TabsTrigger>
              <TabsTrigger value="python">Python</TabsTrigger>
            </TabsList>
            <TabsContent value="js" className="space-y-4">
              <div className="bg-muted p-4 rounded-md">
                <pre className="text-xs overflow-x-auto">
                  <code>{`// Install the SDK
npm install vessa-sdk

// Initialize the client
import { VessaClient } from 'vessa-sdk';

const client = new VessaClient({
  apiKey: '${activeApiKey.key?.substring(0, 10)}...',
});

// Report an incident
client.incidents.create({
  title: 'Security breach detected',
  description: 'Unauthorized access detected from IP 192.168.1.1',
  severity: 'high'
});`}</code>
                </pre>
              </div>
              <div className="flex justify-between">
                <Button variant="outline" className="flex items-center gap-2" onClick={() => window.open('/docs/js-sdk', '_blank')}>
                  <Code className="h-4 w-4" />
                  View JS SDK Documentation
                </Button>
                <Button variant="outline" className="flex items-center gap-2" onClick={() => window.open('/sdk/vessa-sdk-latest.zip', '_blank')}>
                  <Download className="h-4 w-4" />
                  Download SDK
                </Button>
              </div>
            </TabsContent>
            <TabsContent value="python" className="space-y-4">
              <div className="bg-muted p-4 rounded-md">
                <pre className="text-xs overflow-x-auto">
                  <code>{`# Install the SDK
pip install vessa-sdk

# Initialize the client
from vessa_sdk import VessaClient

client = VessaClient(
    api_key='${activeApiKey.key?.substring(0, 10)}...'
)

# Report an incident
client.incidents.create(
    title='Security breach detected',
    description='Unauthorized access detected from IP 192.168.1.1',
    severity='high'
)`}</code>
                </pre>
              </div>
              <div className="flex justify-between">
                <Button variant="outline" className="flex items-center gap-2" onClick={() => window.open('/docs/python-sdk', '_blank')}>
                  <Code className="h-4 w-4" />
                  View Python SDK Documentation
                </Button>
                <Button variant="outline" className="flex items-center gap-2" onClick={() => window.open('/sdk/vessa-sdk-latest.tar.gz', '_blank')}>
                  <Download className="h-4 w-4" />
                  Download SDK
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        </CardFooter>
      )}
    </Card>
  );
}