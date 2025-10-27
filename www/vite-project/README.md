# Vessa Frontend - AI-Powered Web Application Firewall Dashboard

A modern React-based dashboard for the Vessa AI-powered web application firewall, built with Vite, TypeScript, and Tailwind CSS.

## 🚀 Features

### Core Dashboard
- **Real-time Analytics**: Live threat detection metrics and KPIs
- **Incident Management**: Comprehensive incident tracking and resolution
- **API Key Management**: Secure API key generation and management
- **Team Collaboration**: Multi-user support with role-based access

### Analytics & Reporting
- **Threat Analytics**: Real-time threat detection and classification
- **Attack Distribution**: Visual breakdown of attack vectors and patterns
- **Geographic Analytics**: Threat origin mapping and analysis
- **Time Series Charts**: Historical data visualization with Recharts
- **System Impact Analysis**: Performance and security metrics

### User Interface
- **Modern Design**: Built with Radix UI and Tailwind CSS
- **Responsive Layout**: Mobile-first design with adaptive components
- **Dark/Light Mode**: Theme switching with next-themes
- **Interactive Charts**: Dynamic data visualization with loading states
- **Real-time Updates**: Live data fetching with React Query

### Authentication & Security
- **JWT Authentication**: Secure user authentication
- **API Key Management**: RESTful API access control
- **Protected Routes**: Role-based access control
- **Session Management**: Persistent authentication state

## 🛠️ Tech Stack

- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite 6.2
- **Styling**: Tailwind CSS 4.0 + Radix UI
- **State Management**: Zustand
- **Data Fetching**: TanStack React Query + Axios
- **Routing**: React Router DOM 7
- **Charts**: Recharts 2.15
- **Forms**: React Hook Form + Zod validation
- **Notifications**: Sonner + Custom notification system

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- npm or pnpm

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   # or
   pnpm install
   ```

2. **Environment Setup**:
   Create `.env` file:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   VITE_WS_BASE_URL=ws://localhost:8000
   ```

3. **Start development server**:
   ```bash
   npm run dev
   # or
   pnpm dev
   ```

4. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

## 📁 Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── auth/            # Authentication components
│   ├── dashboard/       # Dashboard-specific components
│   ├── charts/          # Chart components
│   ├── integration/     # SDK integration components
│   ├── layout/          # Layout components
│   ├── notifications/    # Notification system
│   └── ui/              # Base UI components (Radix UI)
├── lib/                 # Utilities and services
│   ├── api/            # API clients and endpoints
│   ├── context/        # React contexts
│   ├── services/       # Business logic services
│   ├── store/          # State management (Zustand)
│   └── utils/          # Utility functions
├── pages/              # Page components
│   ├── dashboard/      # Dashboard pages
│   └── ...            # Other pages
└── main.tsx           # Application entry point
```

## 🔧 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Key Features Implemented

#### ✅ Dynamic Data Integration
- **Real-time KPIs**: Total requests, block rate, threat types
- **Live Charts**: Time-series data with empty states
- **API Integration**: Proper error handling and loading states
- **Environment Configuration**: Flexible API endpoint configuration

#### ✅ Authentication System
- **JWT-based Auth**: Secure token management
- **API Key Management**: RESTful API access control
- **Protected Routes**: Role-based navigation
- **Session Persistence**: Zustand state management

#### ✅ Analytics Dashboard
- **Threat Analytics**: Real-time threat detection metrics
- **Attack Distribution**: Attack vector analysis
- **Geographic Analytics**: Threat origin mapping
- **System Impact**: Performance and security metrics
- **Time Series**: Historical data visualization

#### ✅ Modern UI/UX
- **Responsive Design**: Mobile-first approach
- **Loading States**: Skeleton components during data fetch
- **Empty States**: User-friendly messaging for no data
- **Interactive Charts**: Hover effects and tooltips
- **Theme Support**: Dark/light mode switching

## 🔗 API Integration

The frontend integrates with the Vessa backend API:

- **Analytics Endpoints**: `/api/v1/incidents/analytics/*`
- **Incident Management**: `/api/v1/incidents/*`
- **Authentication**: `/api/v1/auth/*`
- **User Management**: `/api/v1/users/*`
- **Notifications**: `/api/v1/notifications/*`

## 🎨 UI Components

Built with a comprehensive design system:

- **Radix UI**: Accessible, unstyled components
- **Tailwind CSS**: Utility-first styling
- **Custom Components**: Dashboard-specific components
- **Chart Library**: Recharts for data visualization
- **Form Handling**: React Hook Form with validation

## 📊 Data Flow

1. **Authentication**: User login → JWT token → API client configuration
2. **Data Fetching**: React Query → API clients → Backend endpoints
3. **State Management**: Zustand stores → Component state
4. **Real-time Updates**: WebSocket connections for live data
5. **Error Handling**: Global error boundaries and API error handling

## 🚀 Deployment

The frontend is optimized for production deployment:

- **Vite Build**: Optimized bundle with code splitting
- **Environment Variables**: Configurable API endpoints
- **Static Assets**: Optimized images and fonts
- **TypeScript**: Full type safety in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the LICENSE file in the repository root for details.
