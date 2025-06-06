import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useAuthStore } from '@/lib/store/auth-store';
import { authApi } from '@/lib/api/auth';
import type { LoginRequest } from '@/lib/api/auth-api';
import type { AxiosError } from 'axios';
import { AuthLayout } from '../layout/auth-layout';
import { useNavigate, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { Eye, EyeOff, Mail, Lock, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

const formSchema = z.object({
  username: z
    .string()
    .min(1, "Email is required")
    .email("Please enter a valid email address"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).*$/,
      "Password must contain at least one uppercase letter, one lowercase letter, and one number"
    ),
});

interface ErrorResponse {
  detail: string;
}

export function LoginForm() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuthStore();
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  });

  const loginMutation = useMutation({
    mutationFn: async (data: LoginRequest) => {
      const loginResponse = await authApi.login(data);
      const userResponse = await authApi.getUser();
      return { loginResponse, userResponse };
    },
    onSuccess: (data) => {
      login(data.userResponse, data.loginResponse.access_token);
      authApi.getApiKey().then((apiKeyData) => {
        useAuthStore.getState().setApiKey(apiKeyData.key);
        window.location.href = '/dashboard';
      }).catch((error: AxiosError) => {
        console.error("Failed to fetch API key:", error);
        window.location.href = '/dashboard';
      });
    },
    onError: (error: AxiosError<ErrorResponse>) => {
      setError(error.response?.data?.detail || 'Login failed');
    },
  });

  const onSubmit = (data: z.infer<typeof formSchema>) => {
    setError(null);
    loginMutation.mutate(data);
  };

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/dashboard");
    }

    if (searchParams.get("session_expired")) {
      setError("Your session has expired. Please log in again.");
    }
  }, [isAuthenticated, navigate, searchParams]);

  return (
    <div className="container relative min-h-screen flex-col items-center justify-center grid lg:max-w-none lg:grid-cols-2 lg:px-0">
      <div className="relative hidden h-full flex-col bg-muted p-10 text-white dark:border-r lg:flex">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-600 to-blue-800">
          <div className="absolute inset-0 bg-[url('/assets/images/auth-bg-pattern.svg')] bg-repeat [mask-image:linear-gradient(to_bottom,white,transparent)]" />
        </div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="relative z-20 flex items-center gap-2"
        >
          <img src="/assets/images/logo.svg" alt="Logo" className="h-12" />
          <span className="text-2xl font-bold">VESSA</span>
        </motion.div>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.8 }}
          className="relative z-20 mt-auto p-14"
        >
          <img
            src="/assets/images/firewall.svg"
            alt="Security Illustration"
            className="h-auto w-full object-contain"
          />
        </motion.div>
      </div>
      <div className="lg:p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[450px]"
        >
          <Card className="border-0 shadow-xl">
            <CardHeader className="space-y-1 pb-2">
              <h2 className="text-2xl font-bold tracking-tight">Welcome back</h2>
              <CardDescription>
                Enter your credentials to access your account
              </CardDescription>
              {error && (
                <Alert variant="destructive" className="mt-4 animate-shake">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
            </CardHeader>
            <CardContent>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username">Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                    <Input
                      id="username"
                      type="email"
                      placeholder="name@example.com"
                      className={cn(
                        "pl-10",
                        form.formState.errors.username && "border-red-500 focus-visible:ring-red-500"
                      )}
                      {...form.register("username")}
                    />
                  </div>
                  {form.formState.errors.username && (
                    <p className="text-sm text-red-500 animate-slideDown">
                      {form.formState.errors.username.message}
                    </p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                      className={cn(
                        "pl-10 pr-10",
                        form.formState.errors.password && "border-red-500 focus-visible:ring-red-500"
                      )}
                      {...form.register("password")}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-2.5 text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5" />
                      ) : (
                        <Eye className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                  {form.formState.errors.password && (
                    <p className="text-sm text-red-500 animate-slideDown">
                      {form.formState.errors.password.message}
                    </p>
                  )}
                </div>
                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-2">
                    <input type="checkbox" className="rounded border-gray-300 text-primary focus:ring-primary" />
                    <span className="text-sm text-muted-foreground">Remember me</span>
                  </label>
                  <a href="/forgot-password" className="text-sm text-primary hover:underline">
                    Forgot password?
                  </a>
                </div>
                <Button
                  type="submit"
                  className="w-full"
                  disabled={loginMutation.isPending}
                >
                  {loginMutation.isPending ? (
                    <>
                      <motion.div
                        className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                      />
                      Signing in...
                    </>
                  ) : (
                    'Sign in'
                  )}
                </Button>
              </form>
              <div className="mt-6 text-center text-sm">
                Don't have an account?{" "}
                <a href="/signup" className="text-primary hover:underline font-medium">
                  Create one now
                </a>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}