import { ApiKeyManager } from "@/components/auth/api-key-manager";
import { SDKDocumentation } from "@/components/integration/sdk-documentation";
import { IntegrationGuide } from "@/components/integration/integration-guide";
import { WebhookConfig } from "@/components/integration/webhook-config";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useSearchParams } from "react-router-dom";

export default function IntegrationPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const defaultTab = searchParams.get("tab") || "api-keys";

  // Update URL when tab changes
  const handleTabChange = (value: string) => {
    searchParams.set("tab", value);
    setSearchParams(searchParams);
  };

  return (
    <div className="container mx-auto py-8 space-y-8">
      <h1 className="text-3xl font-bold">Integration Center</h1>
      <p className="text-muted-foreground">
        Manage your API keys and forward event data to VESSA for security analysis
      </p>
      
      <Tabs defaultValue={defaultTab} onValueChange={handleTabChange} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="api-keys">API Keys</TabsTrigger>
          <TabsTrigger value="guide">Integration Guide</TabsTrigger>
          <TabsTrigger value="sdk-docs">SDK Documentation</TabsTrigger>
          <TabsTrigger value="webhooks">Webhooks</TabsTrigger>
        </TabsList>
        <TabsContent value="api-keys" className="mt-6">
          <ApiKeyManager />
        </TabsContent>
        <TabsContent value="guide" className="mt-6">
          <IntegrationGuide />
        </TabsContent>
        <TabsContent value="sdk-docs" className="mt-6">
          <SDKDocumentation />
        </TabsContent>
        <TabsContent value="webhooks" className="mt-6">
          <WebhookConfig />
        </TabsContent>
      </Tabs>
    </div>
  );
}