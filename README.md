<div align="center">

# 🛡️ VESSA

**Vulnerability Event and Security Systems Analysis**

### Open-Source ML-Enhanced Web Application Firewall

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-beta-yellow.svg)]()

*A self-hosted WAF with DistilBERT-based threat detection for developers who need customizable security*

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 🎯 What is VESSA?

VESSA is an **experimental, open-source Web Application Firewall** that combines traditional pattern-based detection with machine learning models. It's designed for developers, security researchers, and teams looking for a self-hosted, customizable WAF solution.

### 🚀 Why VESSA?

- **🔬 ML-Enhanced**: Uses DistilBERT models for attack classification alongside regex patterns
- **🎛️ Flexible Deployment**: Reverse proxy, FastAPI middleware, or WSGI integration
- **🔓 Open Source**: Apache 2.0 license - inspect, modify, and deploy however you want
- **📊 Full Dashboard**: React-based analytics UI for real-time threat monitoring
- **🐳 Docker-Ready**: Deploy in minutes with Docker Compose

### ⚠️ Current Status: **Beta**

VESSA is functional and suitable for:
- Development/staging environments
- Security research and experimentation
- Small-to-medium traffic applications (<10K req/min)
- Learning WAF concepts and ML integration

**Not recommended for:**
- Production systems with critical data
- High-traffic applications without extensive testing
- Compliance-required environments (SOC 2, ISO 27001)

---

## ✨ Features

### 🛡️ Core WAF Capabilities

- ✅ **Inline Request Blocking** - Real-time interception and blocking
- ✅ **Multiple Deployment Modes**
  - Reverse proxy (protect any backend)
  - FastAPI middleware (drop-in protection)
  - WSGI integration (Flask, Django compatible)
- ✅ **Configurable Actions** - Block, monitor, simulate, or challenge modes
- ✅ **IP Whitelist/Blacklist** - Simple access control
- ✅ **Request Caching** - Performance optimization with 5-minute TTL

### 🤖 ML-Powered Detection

- ✅ **Dual-Model System**
  - Binary classifier (benign vs. malicious)
  - Multi-class classifier (attack type identification)
- ✅ **DistilBERT Architecture** - Pre-trained on ~50K samples
- ✅ **OOD Detection** - Energy-based scoring for novel attacks
- ✅ **Async Processing** - Optional background ML analysis for speed

### 🔍 Pattern-Based Detection

- ✅ **SQL Injection** - 15+ patterns with encoding variants
- ✅ **XSS** - 15+ patterns (script tags, event handlers, etc.)
- ✅ **Path Traversal** - 25+ patterns (URL encoded, double encoded)
- ✅ **Command Injection** - Shell metacharacters and piping
- ✅ **NoSQL Injection** - MongoDB operator detection

### 📊 Dashboard & Analytics

- ✅ **React 19 + TypeScript** - Modern, type-safe frontend
- ✅ **Real-Time Metrics** - Live threat detection statistics
- ✅ **Interactive Charts** - Historical data visualization (Recharts)
- ✅ **Incident Management** - Track and resolve security events
- ✅ **Dark/Light Themes** - Responsive, accessible UI

### 🏗️ Production Infrastructure

- ✅ **FastAPI Backend** - Async Python with Pydantic validation
- ✅ **MySQL + Redis** - Persistent storage and caching
- ✅ **JWT Authentication** - Secure API access
- ✅ **Database Migrations** - Alembic-managed schema changes
- ✅ **Gunicorn + Nginx** - Production deployment ready
- ✅ **Audit Logging** - Comprehensive security event tracking

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/vessa.git
cd vessa

# Start all services (backend, frontend, MySQL, Redis)
docker-compose up --build

# Access applications
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Reverse Proxy Mode (Protect Existing App)

```bash
# Protect any backend without code changes
cd firewall-app
python -m services.waf.reverse_proxy \
  --backend http://localhost:3000 \
  --port 8080 \
  --mode block

# Your app is now protected at http://localhost:8080
```

### Option 3: Manual Setup

See detailed instructions in [firewall-app/README.md](firewall-app/README.md)

---

## 📁 Architecture

### Monorepo Structure

```
vessa/
├── absolution/              # ML Detection Engine
│   ├── src/absolution/
│   │   ├── model_loader.py  # DistilBERT model interface
│   │   └── Models/          # Pre-trained binary & multi-class models (~50K samples)
│   └── pyproject.toml
│
├── firewall-app/            # WAF Backend (FastAPI)
│   ├── services/
│   │   ├── waf/            # WAF engine, middleware, reverse proxy
│   │   ├── incident/       # Threat analysis & incident management
│   │   ├── auth/           # JWT authentication
│   │   └── common/         # Middleware, models, utilities
│   ├── alembic/            # Database migrations
│   ├── main.py             # FastAPI application entry
│   └── gunicorn.conf.py    # Production server config
│
├── www/vite-project/        # Dashboard Frontend (React 19)
│   ├── src/
│   │   ├── pages/          # Dashboard, incidents, alerts, settings
│   │   ├── components/     # Reusable UI components (Radix UI)
│   │   └── lib/            # API clients, state, services
│   └── package.json        # React 19, Vite 6.2, TypeScript
│
└── docker-compose.yml       # Full-stack deployment
```

### Request Flow

```
Client Request
    ↓
┌─────────────────────────────────────┐
│  WAF Middleware / Reverse Proxy     │
│  - Extract request features         │
│  - Check IP whitelist/blacklist     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Static Analysis (Fast Path)        │
│  - Regex pattern matching           │
│  - SQL injection, XSS, etc.         │
│  - ~1-5ms latency                   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  ML Analysis (Optional)              │
│  - DistilBERT inference             │
│  - Binary + Multi-class models      │
│  - Energy-based OOD detection       │
│  - ~50-100ms latency (sync mode)    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Decision Engine                     │
│  - Combine static + ML scores       │
│  - Apply threshold rules            │
│  - BLOCK / ALLOW / CHALLENGE        │
└─────────────────────────────────────┘
    ↓
Blocked (403)   OR   Forward to Backend
```

---

## 📚 Documentation

| Component | Description | Documentation |
|-----------|-------------|---------------|
| **WAF Backend** | FastAPI server, WAF engine, ML integration | [firewall-app/README.md](firewall-app/README.md) |
| **Frontend** | React dashboard for monitoring | [www/vite-project/README.md](www/vite-project/README.md) |
| **ML Models** | DistilBERT classifiers | [absolution/README.md](absolution/README.md) |
| **Deployment** | Production setup guide | [firewall-app/DEPLOYMENT_GUIDE.md](firewall-app/DEPLOYMENT_GUIDE.md) |

---

## 🧪 Testing & Performance

### Current State (Honest Assessment)

| Metric | Status | Notes |
|--------|--------|-------|
| **Test Coverage** | ~25% | Backend only; target: 80%+ |
| **Performance** | Untested | No load testing published |
| **Throughput** | Unknown | Needs benchmarking with `wrk` or `locust` |
| **ML Accuracy** | Untested in prod | Models trained on ~50K samples |
| **False Positive Rate** | Unknown | Requires real-world testing |

### Running Tests

```bash
# Backend tests (limited coverage)
cd firewall-app
poetry run pytest --cov=services tests/

# Frontend linting
cd www/vite-project
npm run lint
```

---

## ⚙️ Configuration

### Backend Environment Variables

**Required:**
```bash
DB_PASSWORD=your_secure_password
JWT_SECRET_KEY=$(openssl rand -hex 32)  # Generate securely!
REDIS_URL=redis://localhost:6379/0
```

**Optional:**
```bash
WAF_ENABLED=true                    # Enable inline WAF middleware
WAF_MODE=block                      # block, monitor, simulate, challenge
STATIC_ANALYSIS_ENABLED=1           # Enable pattern matching
DYNAMIC_ANALYSIS_ENABLED=1          # Enable ML models
```

See [firewall-app/env.example](firewall-app/env.example) for full config.

### Frontend Environment Variables

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

---

## 🛠️ Development Setup

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Python 3.9+** with Poetry
- **Node.js 18+** with npm/pnpm
- **MySQL 8.0+** and **Redis 6.0+** (or use Docker)

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/yourusername/vessa.git
cd vessa

# 2. Start infrastructure (MySQL + Redis)
docker-compose up -d db redis

# 3. Backend setup
cd firewall-app
poetry install
cp env.example .env  # Edit with your config
poetry run alembic upgrade head
poetry run uvicorn main:app --reload

# 4. Frontend setup (new terminal)
cd www/vite-project
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
npm run dev
```

Access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🚧 Known Limitations

### Be Aware Of:

- ⚠️ **Test Coverage**: Only ~25% backend coverage; extensive testing needed
- ⚠️ **Threat Intelligence**: Demo data only; integrate real feeds (AbuseIPDB, etc.)
- ⚠️ **Performance**: No published load testing results
- ⚠️ **Bot Detection**: Not implemented (planned feature)
- ⚠️ **DDoS Protection**: L7 flood detection not available
- ⚠️ **Model Retraining**: No pipeline documented; pre-trained models only
- ⚠️ **False Positive Rate**: Unknown; requires production validation

### Roadmap

- [ ] Increase test coverage to 80%+
- [ ] Publish performance benchmarks (latency, throughput)
- [ ] Integrate commercial threat feeds
- [ ] Add bot detection and CAPTCHA challenges
- [ ] Document model retraining process
- [ ] Add Kubernetes deployment manifests
- [ ] Create learning mode (auto-rule generation)

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Areas Needing Help

1. **Testing**: Increase test coverage (especially WAF engine)
2. **Performance**: Load testing and optimization
3. **Threat Intel**: Real feed integrations
4. **Documentation**: Tutorials, deployment guides
5. **ML Models**: Adversarial testing, retraining pipelines

### Contribution Process

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/vessa.git
cd vessa

# 2. Create feature branch
git checkout -b feature/amazing-feature

# 3. Make changes and test
cd firewall-app
poetry run pytest

# 4. Commit with clear message
git commit -m "feat: add amazing feature"

# 5. Push and create PR
git push origin feature/amazing-feature
```

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript strictly in frontend (no `any` types)
- Add tests for new features
- Update documentation
- Run linters before committing

---

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

This allows you to:
- ✅ Use commercially
- ✅ Modify and distribute
- ✅ Use privately
- ✅ Use patent claims

Under conditions:
- ℹ️ License and copyright notice
- ℹ️ State changes made

---

## 👥 Authors & Acknowledgments

**Created by:**
- Jash Naik ([@infernus007](https://github.com/infernus007)) - jashnaik2004@gmail.com
- Raj Shekhar - infojar001@gmail.com

**Built with:**
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/) - DistilBERT models
- [React](https://react.dev/) - Frontend framework
- [Radix UI](https://www.radix-ui.com/) - Accessible components

**Inspired by:**
- ModSecurity (pattern-based WAF)
- Cloudflare WAF (ML-powered detection)
- OWASP Core Rule Set

---

<div align="center">

### 💡 Questions? Issues? Ideas?

[Open an Issue](https://github.com/yourusername/vessa/issues) • [Start a Discussion](https://github.com/yourusername/vessa/discussions) • [Read the Docs](firewall-app/README.md)

**⭐ Star this repo if you find it useful!**

Built with ❤️ by the VESSA team

</div>
