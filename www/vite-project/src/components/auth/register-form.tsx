import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useAuthStore } from '@/lib/store/auth-store';
import { authApi } from '@/lib/api/auth';
import type { RegisterRequest } from '@/lib/api/auth-api';
import type { AxiosError } from 'axios';
import { motion, AnimatePresence } from "framer-motion";
import { Eye, EyeOff, Mail, Lock, User, Building2, AlertCircle, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

const formSchema = z.object({
  email: z
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
  name: z
    .string()
    .min(2, "Name must be at least 2 characters")
    .max(50, "Name must be less than 50 characters"),
});

interface ErrorResponse {
  detail: string;
}

const strengthChecks = [
  { re: /[0-9]/, label: 'Includes number' },
  { re: /[a-z]/, label: 'Includes lowercase letter' },
  { re: /[A-Z]/, label: 'Includes uppercase letter' },
  { re: /.{8,}/, label: 'At least 8 characters' },
];

export function RegisterForm() {
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState<number>(0);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
      name: "",
    },
  });

  const checkPasswordStrength = (value: string) => {
    let strength = 0;
    for (const check of strengthChecks) {
      if (check.re.test(value)) {
        strength++;
      }
    }
    setPasswordStrength(strength);
  };

  const registerMutation = useMutation({
    mutationFn: async (data: RegisterRequest) => {
      return await authApi.register(data);
    },
    onSuccess: () => {
      window.location.href = '/login?registered=true';
    },
    onError: (error: AxiosError<ErrorResponse>) => {
      setError(error.response?.data?.detail || 'Registration failed');
    },
  });

  const onSubmit = (data: z.infer<typeof formSchema>) => {
    setError(null);
    registerMutation.mutate(data);
  };

  return (
    <div className="container relative min-h-screen flex-col items-center justify-center grid lg:max-w-none lg:grid-cols-2 lg:px-0">
      <div className="relative hidden h-full flex-col bg-muted p-10 text-white dark:border-r lg:flex">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-600 via-blue-600 to-blue-800">
          <div className="absolute inset-0 bg-[url('/assets/images/auth-bg-pattern.svg')] bg-repeat [mask-image:linear-gradient(to_bottom,white,transparent)]" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(255,255,255,0.1),transparent)]" />
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
          transition={{ delay: 0.2, duration: 0.5 }}
          className="relative z-20 mt-8"
        >
          <img 
            src="/assets/images/join.svg"
            alt="Join Illustration"
            className="h-80 w-auto mx-auto mb-8"
          />
          <div className="space-y-8">
            <h3 className="text-3xl font-bold tracking-tight">
              Join the Next Generation of Security Management
            </h3>
            <ul className="grid gap-4">
              {[
                { title: 'Real-time Threat Detection', description: 'Identify and respond to security incidents instantly' },
                { title: 'Advanced Analytics', description: 'Get deep insights into your security posture' },
                { title: 'Automated Response', description: 'Streamline your incident response workflow' },
              ].map((feature, i) => (
                <motion.li
                  key={feature.title}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + i * 0.1 }}
                  className="flex items-start gap-3"
                >
                  <CheckCircle2 className="h-6 w-6 text-blue-300 flex-shrink-0 mt-1" />
                  <div>
                    <h4 className="font-medium">{feature.title}</h4>
                    <p className="text-sm text-blue-200/80">{feature.description}</p>
                  </div>
                </motion.li>
              ))}
            </ul>
          </div>
        </motion.div>
      </div>
      <div className="lg:p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[500px]"
        >
          <Card className="border-0 shadow-xl">
            <CardHeader className="space-y-1 pb-2">
              <h2 className="text-2xl font-bold tracking-tight">Create an account</h2>
              <CardDescription>
                Enter your information to get started
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
                  <Label htmlFor="name">Full Name</Label>
                  <div className="relative">
                    <User className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                    <Input
                      id="name"
                      placeholder="John Doe"
                      className={cn(
                        "pl-10",
                        form.formState.errors.name && "border-red-500 focus-visible:ring-red-500"
                      )}
                      {...form.register("name")}
                    />
                  </div>
                  {form.formState.errors.name && (
                    <p className="text-sm text-red-500 animate-slideDown">
                      {form.formState.errors.name.message}
                    </p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="name@example.com"
                      className={cn(
                        "pl-10",
                        form.formState.errors.email && "border-red-500 focus-visible:ring-red-500"
                      )}
                      {...form.register("email")}
                    />
                  </div>
                  {form.formState.errors.email && (
                    <p className="text-sm text-red-500 animate-slideDown">
                      {form.formState.errors.email.message}
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
                      {...form.register("password", {
                        onChange: (e) => checkPasswordStrength(e.target.value)
                      })}
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
                  <div className="space-y-2">
                    <div className="flex gap-1">
                      {strengthChecks.map((check, i) => (
                        <motion.div
                          key={check.label}
                          className={cn(
                            "h-1 w-full rounded-full",
                            i < passwordStrength ? "bg-green-500" : "bg-gray-200"
                          )}
                          initial={false}
                          animate={{
                            backgroundColor: i < passwordStrength ? "rgb(34 197 94)" : "rgb(229 231 235)"
                          }}
                        />
                      ))}
                    </div>
                    <AnimatePresence>
                      {form.watch("password") && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          className="text-sm space-y-2"
                        >
                          {strengthChecks.map(({ re, label }) => (
                            <div
                              key={label}
                              className="flex items-center gap-2 text-muted-foreground"
                            >
                              <CheckCircle2
                                className={cn(
                                  "h-4 w-4",
                                  re.test(form.watch("password") || "")
                                    ? "text-green-500"
                                    : "text-gray-300"
                                )}
                              />
                              {label}
                            </div>
                          ))}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </div>
                <Button
                  type="submit"
                  className="w-full"
                  disabled={registerMutation.isPending}
                >
                  {registerMutation.isPending ? (
                    <>
                      <motion.div
                        className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                      />
                      Creating account...
                    </>
                  ) : (
                    'Create account'
                  )}
                </Button>
              </form>
              <div className="mt-6 text-center text-sm">
                Already have an account?{" "}
                <a href="/login" className="text-primary hover:underline font-medium">
                  Sign in
                </a>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}