import { ApiKeyManager } from "@/components/auth/api-key-manager";
import { IntegrationGuide } from "@/components/integration/integration-guide";
import { WAFDeploymentGuide } from "@/components/integration/waf-deployment-guide";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useSearchParams } from "react-router-dom";

export default function IntegrationPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const defaultTab = searchParams.get("tab") || "waf";

  // Update URL when tab changes
  const handleTabChange = (value: string) => {
    searchParams.set("tab", value);
    setSearchParams(searchParams);
  };

  return (
    <div className="container mx-auto py-8 space-y-8">
      <h1 className="text-3xl font-bold">Integration Center</h1>
      <p className="text-muted-foreground">
        Deploy VESSA WAF to protect your applications or integrate our security analysis API
      </p>

      <Tabs defaultValue={defaultTab} onValueChange={handleTabChange} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="waf">WAF Deployment</TabsTrigger>
          <TabsTrigger value="api-keys">API Keys</TabsTrigger>
          <TabsTrigger value="guide">API Documentation</TabsTrigger>
        </TabsList>
        <TabsContent value="waf" className="mt-6">
          <WAFDeploymentGuide />
        </TabsContent>
        <TabsContent value="api-keys" className="mt-6">
          <ApiKeyManager />
        </TabsContent>
        <TabsContent value="guide" className="mt-6">
          <IntegrationGuide />
        </TabsContent>
      </Tabs>
    </div>
  );
}