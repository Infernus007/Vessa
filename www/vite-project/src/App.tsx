import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { LoginForm } from './components/auth/login-form';
import { RegisterForm } from './components/auth/register-form';
import { useAuthStore } from './lib/store/auth-store';
import Dashboard from './pages/dashboard';
import IntegrationPage from './pages/dashboard/integration';
import { DashboardLayout } from './components/layout/dashboard-layout';
import IncidentDetails from "@/pages/dashboard/incident-details";
import { NotificationProvider } from '@/lib/context/notification-context';
import { LandingPage } from './pages/landing';
import { IncidentsPage } from './pages/incidents';
import AlertsPage from './app/dashboard/alerts/page';
import ReportsPage from './app/dashboard/reports/page';
import { ApiKeyManager } from './components/auth/api-key-manager';

// Protected Route wrapper component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <Router>
      <NotificationProvider>
        <div className="min-h-screen bg-background">
          <Routes>
            {/* Redirect to dashboard if authenticated, otherwise show landing page */}
            <Route 
              path="/" 
              element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LandingPage />} 
            />
            
            {/* Auth routes */}
            <Route path="/login" element={<LoginForm />} />
            <Route path="/signup" element={<RegisterForm />} />
            <Route path="/docs" element={<div>Documentation</div>} />
            <Route path="/demo" element={<div>Request Demo</div>} />
            <Route path="/contact" element={<div>Contact Sales</div>} />
            
            {/* Dashboard and protected routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }>
              <Route index element={<Dashboard />} />
              <Route path="integration" element={<IntegrationPage />} />
              <Route path="incidents" element={<IncidentsPage />} />
              <Route path="incidents/:id" element={<IncidentDetails />} />
              <Route path="incidents/new" element={<div>New Incident</div>} />
              <Route path="reports" element={<ReportsPage />} />
              <Route path="alerts" element={<AlertsPage />} />
              <Route path="api-keys" element={<ApiKeyManager />} />
              <Route path="team" element={<div>Team</div>} />
              <Route path="settings" element={<div>Settings</div>} />
              <Route path="profile" element={<div>Profile</div>} />
              <Route path="help" element={<div>Help & Support</div>} />
            </Route>
            
            {/* Fallback route */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </NotificationProvider>
    </Router>
  );
}

export default App;
