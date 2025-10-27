import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
        errorInfo: null,
    };

    public static getDerivedStateFromError(error: Error): State {
        return {
            hasError: true,
            error,
            errorInfo: null,
        };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Error caught by boundary:', error, errorInfo);

        this.setState({
            error,
            errorInfo,
        });

        // Log to error tracking service (Sentry, etc.) in production
        if (import.meta.env.PROD) {
            // TODO: Send to error tracking service
            // Example: Sentry.captureException(error, { contexts: { react: { componentStack: errorInfo.componentStack } } });
        }
    }

    private handleReset = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null,
        });
    };

    private handleReload = () => {
        window.location.reload();
    };

    public render() {
        if (this.state.hasError) {
            // Custom fallback UI if provided
            if (this.props.fallback) {
                return this.props.fallback;
            }

            // Default error UI
            return (
                <div className="min-h-screen flex items-center justify-center p-4 bg-background">
                    <Card className="max-w-2xl w-full">
                        <CardHeader>
                            <div className="flex items-center gap-3">
                                <AlertTriangle className="h-8 w-8 text-destructive" />
                                <div>
                                    <CardTitle className="text-2xl">Something went wrong</CardTitle>
                                    <CardDescription>
                                        An unexpected error occurred. Please try again.
                                    </CardDescription>
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {/* Error details (only in development) */}
                            {!import.meta.env.PROD && this.state.error && (
                                <div className="space-y-2">
                                    <div className="bg-muted p-4 rounded-md">
                                        <p className="text-sm font-semibold text-destructive mb-2">
                                            Error: {this.state.error.message}
                                        </p>
                                        {this.state.errorInfo && (
                                            <details className="text-xs text-muted-foreground">
                                                <summary className="cursor-pointer hover:text-foreground">
                                                    Stack trace
                                                </summary>
                                                <pre className="mt-2 overflow-x-auto whitespace-pre-wrap">
                                                    {this.state.error.stack}
                                                </pre>
                                                <pre className="mt-2 overflow-x-auto whitespace-pre-wrap">
                                                    {this.state.errorInfo.componentStack}
                                                </pre>
                                            </details>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* Actions */}
                            <div className="flex gap-3">
                                <Button onClick={this.handleReset} variant="outline">
                                    Try Again
                                </Button>
                                <Button onClick={this.handleReload} variant="default">
                                    <RefreshCw className="h-4 w-4 mr-2" />
                                    Reload Page
                                </Button>
                            </div>

                            {/* User guidance */}
                            <div className="border-t pt-4 mt-4">
                                <p className="text-sm text-muted-foreground">
                                    If this problem persists, please:
                                </p>
                                <ul className="list-disc list-inside text-sm text-muted-foreground mt-2 space-y-1">
                                    <li>Clear your browser cache and cookies</li>
                                    <li>Try using a different browser</li>
                                    <li>Contact support if the issue continues</li>
                                </ul>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            );
        }

        return this.props.children;
    }
}

// Functional wrapper for easier use
export function withErrorBoundary<P extends object>(
    Component: React.ComponentType<P>,
    fallback?: ReactNode
) {
    return function WithErrorBoundaryWrapper(props: P) {
        return (
            <ErrorBoundary fallback={fallback}>
                <Component {...props} />
            </ErrorBoundary>
        );
    };
}

