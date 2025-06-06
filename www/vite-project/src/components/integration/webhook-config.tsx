import { useState } from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertCircle, Plus, Trash2 } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function WebhookConfig() {
  const [webhooks, setWebhooks] = useState([
    { id: 1, url: 'https://example.com/webhook', events: ['incident.created'], active: true },
  ]);
  const [newWebhookUrl, setNewWebhookUrl] = useState('');
  const [selectedEvents, setSelectedEvents] = useState<string[]>(['incident.created']);

  const addWebhook = () => {
    if (!newWebhookUrl) return;
    
    const newWebhook = {
      id: Date.now(),
      url: newWebhookUrl,
      events: selectedEvents,
      active: true
    };
    
    setWebhooks([...webhooks, newWebhook]);
    setNewWebhookUrl('');
  };

  const removeWebhook = (id: number) => {
    setWebhooks(webhooks.filter(webhook => webhook.id !== id));
  };

  const toggleWebhook = (id: number) => {
    setWebhooks(webhooks.map(webhook => 
      webhook.id === id ? { ...webhook, active: !webhook.active } : webhook
    ));
  };

  const toggleEvent = (event: string) => {
    if (selectedEvents.includes(event)) {
      setSelectedEvents(selectedEvents.filter(e => e !== event));
    } else {
      setSelectedEvents([...selectedEvents, event]);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Webhook Configuration</CardTitle>
        <CardDescription>
          Configure webhooks to receive raw event data from your applications
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Important</AlertTitle>
          <AlertDescription>
            Webhooks allow your systems to receive raw event data that can be processed by the VESSA backend.
            Your endpoint will receive the exact data that was sent to the API without any preprocessing.
          </AlertDescription>
        </Alert>

        <div className="space-y-4">
          <h3 className="text-lg font-medium">Active Webhooks</h3>
          
          {webhooks.length === 0 ? (
            <div className="text-center py-4 border rounded-md bg-muted/50">
              <p className="text-sm text-muted-foreground">No webhooks configured</p>
            </div>
          ) : (
            <div className="space-y-3">
              {webhooks.map(webhook => (
                <div key={webhook.id} className="flex items-center justify-between p-3 border rounded-md">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{webhook.url}</p>
                    <p className="text-xs text-muted-foreground">
                      Events: {webhook.events.join(', ')}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Switch 
                      checked={webhook.active} 
                      onCheckedChange={() => toggleWebhook(webhook.id)} 
                    />
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      onClick={() => removeWebhook(webhook.id)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-medium">Add New Webhook</h3>
          
          <div className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor="webhook-url">Webhook URL</Label>
              <Input 
                id="webhook-url" 
                placeholder="https://your-domain.com/webhook" 
                value={newWebhookUrl}
                onChange={(e) => setNewWebhookUrl(e.target.value)}
              />
            </div>
            
            <div className="space-y-2">
              <Label>Events to Subscribe</Label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  'incident.created',
                  'incident.updated',
                  'incident.resolved',
                  'incident.comment_added',
                  'incident.assigned',
                  'incident.severity_changed'
                ].map(event => (
                  <div key={event} className="flex items-center space-x-2">
                    <Switch 
                      id={`event-${event}`}
                      checked={selectedEvents.includes(event)}
                      onCheckedChange={() => toggleEvent(event)}
                    />
                    <Label htmlFor={`event-${event}`} className="text-sm cursor-pointer">
                      {event}
                    </Label>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button onClick={addWebhook} disabled={!newWebhookUrl} className="w-full">
          <Plus className="mr-2 h-4 w-4" />
          Add Webhook
        </Button>
      </CardFooter>
    </Card>
  );
}