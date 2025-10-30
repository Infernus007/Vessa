<div align="center">

# 📊 VESSA Dashboard

**React Security Analytics Interface**

[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-6.2-646cff.svg)](https://vitejs.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178c6.svg)](https://www.typescriptlang.org)
[![Tailwind](https://img.shields.io/badge/Tailwind-4.0-38bdf8.svg)](https://tailwindcss.com)

*Modern dashboard for VESSA Web Application Firewall monitoring and management*

</div>

---

## ✨ Features

### 📊 Analytics Dashboard

- ✅ **Real-Time Metrics** - Live threat detection statistics
- ✅ **Interactive Charts** - Time-series visualization with Recharts
- ✅ **Attack Distribution** - Visual breakdown of threat types
- ✅ **KPI Widgets** - Request counts, block rates, threat levels
- ✅ **Empty States** - User-friendly messaging when no data
- ✅ **Loading States** - Skeleton components during data fetch

### 🛡️ Incident Management

- ✅ **Incident List** - Searchable, filterable threat table
- ✅ **Incident Details** - Full request inspection and analysis
- ✅ **Threat Classification** - ML-powered attack categorization
- ✅ **Timeline View** - Chronological incident tracking
- ✅ **Resolution Actions** - Mark as resolved, false positive, etc.

### 🔐 Authentication & Security

- ✅ **JWT Authentication** - Token-based secure login
- ✅ **API Key Management** - Generate and revoke API keys
- ✅ **Protected Routes** - Auth-guarded navigation
- ✅ **Session Persistence** - Zustand state management
- ✅ **Automatic Token Refresh** - Seamless re-authentication

### 🎨 User Interface

- ✅ **Radix UI Components** - Accessible, unstyled primitives
- ✅ **Tailwind CSS 4.0** - Utility-first styling
- ✅ **Dark/Light Themes** - System preference detection
- ✅ **Responsive Design** - Mobile-first approach
- ✅ **Framer Motion** - Smooth animations and transitions

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|-------|-----------|----------|
| **Framework** | React | 19.0.0 |
| **Build Tool** | Vite | 6.2.0 |
| **Language** | TypeScript | 5.7.2 |
| **Styling** | Tailwind CSS | 4.0.12 |
| **UI Library** | Radix UI | Latest |
| **State** | Zustand | 5.0.3 |
| **Data Fetching** | React Query | 5.67.2 |
| **HTTP** | Axios | 1.8.2 |
| **Routing** | React Router | 7.3.0 |
| **Charts** | Recharts | 2.15.1 |
| **Forms** | React Hook Form | 7.54.2 |
| **Validation** | Zod | 3.24.2 |
| **Notifications** | Sonner | 2.0.1 |
| **Animations** | Framer Motion | 12.5.0 |

---

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** ([Download](https://nodejs.org/))
- **npm** or **pnpm** package manager
- **Backend API running** at http://localhost:8000

### Installation

```bash
# 1. Install dependencies
npm install
# or
pnpm install

# 2. Create environment file
cat > .env << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
EOF

# 3. Start development server
npm run dev

# 4. Open browser
# http://localhost:5173
```

### Default Credentials (Development)

```
Email: admin@example.com
Password: (create via backend CLI)
```

See [backend README](../../firewall-app/README.md) for user creation

---

## 📚 Project Structure

```
src/
├── components/              # Reusable UI components
│   ├── auth/               # Login, register forms
│   ├── dashboard/          # Analytics widgets, KPI cards
│   ├── charts/             # Recharts wrapper components
│   ├── integration/        # WAF integration guides
│   ├── layout/             # Sidebar, navbar, footer
│   ├── notifications/      # Toast notifications
│   └── ui/                 # Radix UI primitives (button, input, etc.)
│
├── lib/                    # Core utilities
│   ├── api/               # Axios client, query hooks
│   ├── context/           # Auth context, theme context
│   ├── services/          # API service layer
│   ├── store/             # Zustand state stores
│   └── utils/             # Helper functions, formatters
│
├── pages/                  # Route components
│   ├── dashboard/         # Main analytics page
│   ├── incidents/         # Incident list & details
│   ├── alerts/            # Alert management
│   ├── settings/          # User settings, API keys
│   └── auth/              # Login, register pages
│
├── main.tsx               # App entry point
├── App.tsx                # Root component, routing
└── index.css              # Global styles, Tailwind imports
```

---

## 🔧 Development

### Available Scripts

```bash
npm run dev      # Start dev server (http://localhost:5173)
npm run build    # Build for production (dist/)
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `VITE_API_BASE_URL` | Backend API endpoint | `http://localhost:8000` |
| `VITE_WS_BASE_URL` | WebSocket endpoint | `ws://localhost:8000` |

### Development Workflow

1. **Start Backend** - Ensure firewall-app is running on port 8000
2. **Start Frontend** - Run `npm run dev` in this directory
3. **Hot Reload** - Changes auto-reload in browser
4. **Type Checking** - TypeScript errors shown in terminal

### Adding New Components

```bash
# UI components (Radix primitives)
src/components/ui/

# Feature components
src/components/dashboard/

# Page components
src/pages/
```

---

## 🔗 API Integration

### Backend Endpoints Used

| Module | Endpoint | Purpose |
|--------|----------|----------|
| **Auth** | `POST /api/v1/auth/token` | User login (JWT) |
| | `POST /api/v1/auth/register` | User registration |
| **Analytics** | `GET /api/v1/incidents/analytics/overview` | Dashboard KPIs |
| | `GET /api/v1/incidents/analytics/time-series` | Chart data |
| | `GET /api/v1/incidents/analytics/attack-distribution` | Threat breakdown |
| **Incidents** | `GET /api/v1/incidents/` | Incident list |
| | `GET /api/v1/incidents/{id}` | Incident details |
| **Users** | `GET /api/v1/users/me` | Current user info |
| | `GET /api/v1/users/api-keys` | List API keys |
| | `POST /api/v1/users/api-keys` | Generate new key |

### API Client Setup

See `src/lib/api/client.ts` for Axios configuration with:
- JWT token injection
- Request/response interceptors
- Error handling
- Base URL from environment

---

## 🎨 UI Design System

### Component Library

**Radix UI Primitives** (`src/components/ui/`):
- `Button`, `Input`, `Label`, `Select`
- `DropdownMenu`, `Tooltip`, `Avatar`
- `Tabs`, `Switch`, `ScrollArea`

**Custom Components** (`src/components/`):
- `DashboardCard` - Metric display widget
- `IncidentTable` - Data table with pagination
- `ThreatChart` - Recharts wrapper
- `EmptyState` - No data placeholder
- `LoadingSkeleton` - Loading placeholders

### Styling Approach

```typescript
// Tailwind utility classes
<Button className="bg-blue-500 hover:bg-blue-600">

// CVA (Class Variance Authority) for variants
const buttonVariants = cva("base-styles", {
  variants: {
    variant: {
      default: "bg-primary",
      destructive: "bg-red-500"
    }
  }
})
```

---

## 📊 Data Flow Architecture

```
User Interaction
    ↓
┌───────────────────────────────┐
│  React Component                 │
│  - Render UI                     │
│  - Handle events                 │
└───────────────────────────────┘
    ↓
┌───────────────────────────────┐
│  React Query Hook               │
│  - Cache management             │
│  - Loading/error states         │
└───────────────────────────────┘
    ↓
┌───────────────────────────────┐
│  API Client (Axios)             │
│  - JWT token injection          │
│  - Error interceptors           │
└───────────────────────────────┘
    ↓
Backend API (FastAPI)
    ↓
Response → React Query Cache → Component Re-render
```

### State Management

- **Global State** (Zustand): Auth, user, theme
- **Server State** (React Query): API data, caching
- **Local State** (useState): Form inputs, UI toggles

---

## 🚀 Production Build

```bash
# Build for production
npm run build

# Output directory
dist/
├── assets/           # JS, CSS bundles
├── index.html        # Entry HTML
└── vite.svg          # Static assets

# Preview build locally
npm run preview  # http://localhost:4173
```

### Deployment Options

**Static Hosting** (Vercel, Netlify, GitHub Pages):
```bash
npm run build
# Deploy dist/ directory
```

**Docker**:
```dockerfile
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
EXPOSE 80
```

**Environment Variables for Production**:
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_WS_BASE_URL=wss://api.yourdomain.com
```

### Build Optimizations

- **Code Splitting** - Automatic chunk splitting
- **Tree Shaking** - Removes unused code
- **Minification** - Terser for JS, LightningCSS for CSS
- **Asset Optimization** - Image compression, font subsetting

---

## 🤝 Contributing

### Development Guidelines

```typescript
// 1. Follow TypeScript strictly (no `any` types)
const getData = async (): Promise<ApiResponse> => { ... }

// 2. Use Tailwind for styling (avoid inline styles)
<div className="flex items-center gap-2">

// 3. Destructure props for clarity
const Component: React.FC<Props> = ({ title, onAction }) => { ... }

// 4. Use React Query for server state
const { data, isLoading } = useQuery({ ... })

// 5. Handle loading and error states
{isLoading ? <Skeleton /> : <Content />}
{error && <ErrorMessage />}
```

### Code Style

- **ESLint** - Run `npm run lint` before committing
- **Prettier** - Auto-format on save (recommended)
- **Imports** - Group by external, internal, relative
- **Components** - One component per file
- **Naming** - PascalCase for components, camelCase for functions

### Pull Request Process

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes with clear commit messages
4. Run linter (`npm run lint`)
5. Test in browser (visual check)
6. Push to your fork
7. Open Pull Request with description

---

## 📝 License

Apache License 2.0 - see [LICENSE](../../LICENSE) file for details.

---

<div align="center">

**Built with React 19, Vite 6, and ❤️ by the VESSA team**

[Backend Docs](../../firewall-app/README.md) • [Root README](../../README.md) • [Report Issues](https://github.com/yourusername/vessa/issues)

</div>
