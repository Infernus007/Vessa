import { Link } from 'react-router-dom';
import { Button } from "./ui/button";
import { useAuthStore } from '@/lib/store/auth-store';
import { cn } from "@/lib/utils";
import { NotificationButton } from './notifications/NotificationButton';
import { useState } from 'react';
import { NotificationPanel } from './notifications/NotificationPanel';

interface NavbarProps {
  variant?: 'light' | 'dark';
}

export function Navbar({ variant = 'dark' }: NavbarProps) {
  const { isAuthenticated, logout } = useAuthStore();
  const isLight = variant === 'light';
  const [showNotifications, setShowNotifications] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full flex items-center border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-14 items-center justify-between">
          <div className="flex items-center space-x-8">
            <Link to="/" className={cn(
              "text-xl font-bold",
              isLight && "text-white"
            )}>VESSA</Link>
            <div className="hidden md:flex space-x-6">
              {/* <Link 
                to="/docs" 
                className={cn(
                  "text-sm transition-colors",
                  isLight ? "text-blue-100 hover:text-white" : "hover:text-primary"
                )}
              >
                Documentation
              </Link> */}
              {isAuthenticated && (
                <>
                  <Link 
                    to="/dashboard" 
                    className={cn(
                      "text-sm transition-colors",
                      isLight ? "text-blue-100 hover:text-white" : "hover:text-primary"
                    )}
                  >
                    Dashboard
                  </Link>
                  <Link 
                    to="/settings" 
                    className={cn(
                      "text-sm transition-colors",
                      isLight ? "text-blue-100 hover:text-white" : "hover:text-primary"
                    )}
                  >
                    Settings
                  </Link>
                </>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            {isAuthenticated && (
              <NotificationButton 
                onClick={() => setShowNotifications(true)} 
              />
            )}
            {isAuthenticated ? (
              <Button 
                variant={isLight ? "outline" : "ghost"} 
                onClick={logout}
                className={cn(
                  isLight && "border-white/20 text-white hover:bg-white/10"
                )}
              >
                Logout
              </Button>
            ) : (
              <>
                <Link to="/login">
                  <Button 
                    variant={isLight ? "secondary" : "ghost"}
                    className={cn(
                      isLight && "bg-white/10 text-white hover:bg-white/20 border-0"
                    )}
                  >
                    Login
                  </Button>
                </Link>
                <Link to="/signup">
                  <Button
                    className={cn(
                      isLight ? "bg-white text-blue-600 hover:bg-blue-50" : ""
                    )}
                  >
                    Sign Up
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>

        {showNotifications && (
          <div className="fixed inset-0 z-50 flex items-start justify-end p-4 pt-20 w-full h-full bg-green-500">
            <div className="absolute inset-0 bg-black/20 w-full h-full" onClick={() => setShowNotifications(false)} />
            <NotificationPanel
              onClose={() => setShowNotifications(false)}
            />
          </div>
        )}
      </div>
    </header>
  );
}