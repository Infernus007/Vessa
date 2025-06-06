import * as React from "react";
import { cn } from "@/lib/utils";

interface StepsProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function Steps({ children, className, ...props }: StepsProps) {
  // Count the number of Step children
  const stepCount = React.Children.count(children);
  
  // Clone each child and add the step number and total steps
  const stepsWithProps = React.Children.map(children, (child, index) => {
    if (React.isValidElement(child)) {
      return React.cloneElement(child, {
        stepNumber: index + 1,
        totalSteps: stepCount,
      });
    }
    return child;
  });

  return (
    <div className={cn("space-y-8", className)} {...props}>
      {stepsWithProps}
    </div>
  );
}

interface StepProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  stepNumber?: number;
  totalSteps?: number;
}

export function Step({ 
  title, 
  children, 
  stepNumber, 
  totalSteps,
  className, 
  ...props 
}: StepProps) {
  return (
    <div className={cn("relative pl-8", className)} {...props}>
      {/* Step number indicator */}
      <div className="absolute left-0 top-0 flex h-6 w-6 items-center justify-center rounded-full border bg-background text-sm font-medium">
        {stepNumber}
      </div>
      
      {/* Connector line */}
      {stepNumber && totalSteps && stepNumber < totalSteps && (
        <div className="absolute left-3 top-6 h-full w-px bg-border -ml-px" />
      )}
      
      {/* Content */}
      <div className="space-y-2">
        <h3 className="text-base font-medium">{title}</h3>
        <div className="text-sm text-muted-foreground">{children}</div>
      </div>
    </div>
  );
}