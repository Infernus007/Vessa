import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuthStore } from '@/lib/store/auth-store';
import { authApi } from '@/lib/api/auth';
import type { APIKeyResponse, APIKeyListResponse } from '@/lib/api/auth-api';
import { Copy, RefreshCw, Trash2, Power, PowerOff, Check } from 'lucide-react';
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Skeleton } from "@/components/ui/skeleton";

export function ApiKeyPreview() {
    const [isCopied, setIsCopied] = useState(false);
    const { setApiKey } = useAuthStore();
    const queryClient = useQueryClient();

    const { data: apiKeyData, isLoading: isLoadingKey } = useQuery<APIKeyListResponse>({
        queryKey: ['apiKeys'],
        queryFn: async () => {
            return await authApi.listApiKeys();
        }
    });

    const apiKey = apiKeyData?.items[0];

    const { mutate: createKey, isPending: isCreating } = useMutation({
        mutationFn: async () => {
            const newKey = await authApi.createApiKey({ name: 'Default API Key' });
            return newKey;
        },
        onSuccess: (data) => {
            setApiKey(data.key);
            queryClient.setQueryData(['apiKeys'], {
                items: [data],
                total: 1
            });
            queryClient.invalidateQueries({ queryKey: ['apiKeys'] });
            toast.success('API key created successfully');
        },
        onError: () => {
            toast.error('Failed to create API key');
        }
    });

    const { mutate: regenerateKey, isPending: isRegenerating } = useMutation({
        mutationFn: async () => {
            if (!apiKey?.id) throw new Error('No API key to regenerate');
            const newKey = await authApi.regenerateApiKey(apiKey.id);
            return newKey;
        },
        onSuccess: (data) => {
            setApiKey(data.key);
            queryClient.setQueryData(['apiKeys'], (old: APIKeyListResponse | undefined) => ({
                items: old?.items ? [data, ...old.items.slice(1)] : [data],
                total: old?.total || 1
            }));
            queryClient.invalidateQueries({ queryKey: ['apiKeys'] });
            toast.success('API key regenerated successfully');
        },
        onError: () => {
            toast.error('Failed to regenerate API key');
        }
    });

    const { mutate: deleteKey, isPending: isDeleting } = useMutation({
        mutationFn: async () => {
            if (!apiKey?.id) throw new Error('No API key to delete');
            return await authApi.deleteApiKey(apiKey.id);
        },
        onSuccess: () => {
            setApiKey(null);
            queryClient.setQueryData(['apiKeys'], {
                items: [],
                total: 0
            });
            queryClient.invalidateQueries({ queryKey: ['apiKeys'] });
            toast.success('API key deleted successfully');
        },
        onError: () => {
            toast.error('Failed to delete API key');
        }
    });

    const { mutate: toggleActivation, isPending: isTogglingActivation } = useMutation({
        mutationFn: async () => {
            if (!apiKey?.id) throw new Error('No API key to toggle');
            return apiKey.is_active
                ? await authApi.deactivateApiKey(apiKey.id)
                : await authApi.activateApiKey(apiKey.id);
        },
        onSuccess: (data) => {
            queryClient.setQueryData(['apiKeys'], (old: APIKeyListResponse | undefined) => ({
                items: old?.items ? [data, ...old.items.slice(1)] : [data],
                total: old?.total || 1
            }));
            queryClient.invalidateQueries({ queryKey: ['apiKeys'] });
            toast.success(`API key ${data.is_active ? 'activated' : 'deactivated'} successfully`);
        },
        onError: () => {
            toast.error('Failed to toggle API key activation');
        }
    });

    const copyToClipboard = async (text: string) => {
        await navigator.clipboard.writeText(text);
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 2000);
        toast.success('API key copied to clipboard');
    };

    const maskApiKey = (key: string) => {
        return `${key.slice(0, 8)}...${key.slice(-8)}`;
    };

    if (isLoadingKey) {
        return (
            <div className="space-y-4">
                <Skeleton className="h-8 w-2/3" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-8 w-1/3" />
            </div>
        );
    }

    if (!apiKey) {
        return (
            <div className="flex flex-col items-center justify-center space-y-4 py-6">
                <p className="text-sm text-muted-foreground">No API key found</p>
                <Button
                    onClick={() => createKey()}
                    disabled={isCreating}
                >
                    {isCreating ? "Creating..." : "Generate API Key"}
                </Button>
            </div>
        );
    }

    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle>API Key</CardTitle>
                <CardDescription>Your API key for accessing the API</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <div className="space-y-1">
                            <p className="text-sm font-medium">API Key</p>
                            <p className="text-sm text-muted-foreground">
                                Use this key to authenticate your API requests
                            </p>
                        </div>
                        <Badge variant="outline">
                            {apiKey.is_active ? "Active" : "Inactive"}
                        </Badge>
                    </div>
                    <div className="flex items-center space-x-2">
                        <code className="flex-1 rounded bg-muted px-2 py-1">
                            {isRegenerating ? (
                                <Skeleton className="h-6 w-full" />
                            ) : (
                                maskApiKey(apiKey.key)
                            )}
                        </code>
                        <Button
                            variant="outline"
                            size="icon"
                            onClick={() => copyToClipboard(apiKey.key)}
                            disabled={isRegenerating}
                            className={isCopied ? 'bg-green-500 text-white hover:bg-green-600' : ''}
                        >
                            {isCopied ? (
                                <Check className="h-4 w-4" />
                            ) : (
                                <Copy className="h-4 w-4" />
                            )}
                        </Button>
                    </div>
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => regenerateKey()}
                            disabled={isRegenerating}
                        >
                            <RefreshCw className={`h-4 w-4 mr-2 ${isRegenerating ? 'animate-spin' : ''}`} />
                            {isRegenerating ? "Regenerating..." : "Regenerate"}
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => toggleActivation()}
                            disabled={isTogglingActivation || isRegenerating}
                        >
                            {apiKey.is_active ? (
                                <PowerOff className="h-4 w-4 mr-2" />
                            ) : (
                                <Power className="h-4 w-4 mr-2" />
                            )}
                            {isTogglingActivation
                                ? "Updating..."
                                : apiKey.is_active
                                    ? 'Deactivate'
                                    : 'Activate'
                            }
                        </Button>
                        <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => deleteKey()}
                            disabled={isDeleting || isRegenerating}
                        >
                            <Trash2 className="h-4 w-4 mr-2" />
                            {isDeleting ? "Deleting..." : "Delete"}
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}