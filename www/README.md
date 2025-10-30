# VESSA Frontend

**React Dashboard for VESSA Web Application Firewall**

Real-time security monitoring, threat analytics, and incident management dashboard built with React 19, Vite, and TypeScript.

---

## 📁 Structure

This directory contains the frontend application in `vite-project/`. See [vite-project/README.md](vite-project/README.md) for full documentation.

```
www/
└── vite-project/           # Main frontend application
    ├── src/
    │   ├── pages/          # Route components (Dashboard, Incidents, etc.)
    │   ├── components/     # Reusable UI components
    │   └── lib/            # API clients, state management
    └── package.json        # Dependencies (React 19, Vite 6.2)
```

---

## ✨ Key Features

### 📊 Real-Time Analytics
- Live threat detection metrics
- Interactive time-series charts (Recharts)
- Attack distribution visualization
- System health monitoring

### 🛡️ Incident Management
- Comprehensive threat tracking
- Incident timeline and resolution
- Detailed request analysis
- Export capabilities

### 🔐 Security & Auth
- JWT authentication
- API key management
- Role-based access control
- Session persistence (Zustand)

### 🎨 Modern UI/UX
- **React 19** with TypeScript
- **Radix UI** accessible components
- **Tailwind CSS 4.0** styling
- Dark/light theme support
- Mobile-responsive design

---

## 🚀 Quick Start

```bash
# Navigate to frontend app
cd vite-project

# Install dependencies
npm install  # or pnpm install

# Create environment file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Start development server
npm run dev

# Access at http://localhost:5173
```

---

## 🛠️ Tech Stack

| Category | Technology | Version |
|----------|------------|----------|
| **Framework** | React | 19.0 |
| **Build Tool** | Vite | 6.2 |
| **Language** | TypeScript | 5.7 |
| **Styling** | Tailwind CSS | 4.0 |
| **UI Components** | Radix UI | Latest |
| **State** | Zustand | 5.0 |
| **Data Fetching** | React Query | 5.67 |
| **HTTP Client** | Axios | 1.8 |
| **Routing** | React Router | 7.3 |
| **Charts** | Recharts | 2.15 |
| **Forms** | React Hook Form | 7.54 |
| **Validation** | Zod | 3.24 |

---

## 📚 Documentation

For detailed documentation, see:
- **[vite-project/README.md](vite-project/README.md)** - Complete frontend docs
- **[../firewall-app/README.md](../firewall-app/README.md)** - Backend API docs

---

## 🐳 Docker Development

```bash
# From project root
docker-compose up frontend

# Access at http://localhost:5173
```

---

## 🤝 Contributing

See [vite-project/README.md](vite-project/README.md) for:
- Development guidelines
- Component structure
- Coding standards
- Testing procedures

---

## 📄 License

Apache License 2.0 - see [LICENSE](../LICENSE) file for details
