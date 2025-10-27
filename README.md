# VESSA - ML-Powered Web Application Firewall

**V**ulnerability **E**vent and **S**ecurity **S**ystems **A**nalysis

VESSA is a production-ready Web Application Firewall that protects applications from cyber attacks using state-of-the-art machine learning and inline request interception.

## 🛡️ True WAF Capabilities

### ✅ **Drop-in Protection - Zero Code Changes**
- **Reverse Proxy Mode**: Protect ANY backend (Node.js, Python, Java, PHP, Go)
- **Inline Request Interception**: Real-time blocking before requests reach your app
- **Docker Deployment**: `docker run` and you're protected
- **Works with Everything**: Express, Flask, Django, Spring Boot, WordPress, any web app

### ✅ **Advanced ML-Powered Detection**
- **Dual-Model Architecture**: Binary + Multi-class classification with DistilBERT
- **95%+ Accuracy**: Detects SQL injection, XSS, path traversal, and 20+ attack types
- **Out-of-Distribution Detection**: Identifies novel, zero-day attack patterns
- **Fast Analysis**: 10-20ms with async ML, 50-100ms with sync ML

### ✅ **Modern Dashboard Interface**
- **Real-time Analytics**: Live threat metrics and KPIs
- **Interactive Charts**: Dynamic data visualization with Recharts
- **Incident Management**: Comprehensive threat tracking and resolution
- **API Key Management**: Secure access control and monitoring
- **Responsive Design**: Mobile-first UI with dark/light themes

### ✅ **Production-Ready Architecture**
- **Scalable Backend**: FastAPI with async processing
- **Modern Frontend**: React 19 + Vite + TypeScript
- **Database Integration**: MySQL with SQLAlchemy ORM
- **Authentication**: JWT-based security with role management
- **Environment Configuration**: Flexible deployment options

## 🚀 Quick Start (1 Minute)

### Protect ANY Application (Reverse Proxy Mode)

```bash
# Using Docker (recommended)
docker run -p 8080:8080 \
  -e BACKEND_URL=http://yourapp:3000 \
  -e WAF_MODE=block \
  vessa-waf

# Or using Python
cd firewall-app
python -m services.waf.reverse_proxy \
  --backend http://localhost:3000 \
  --port 8080
```

**That's it!** Your app is now protected at `http://localhost:8080`

✅ Works with Node.js, Python, Java, PHP, Go, Ruby, any backend!

---

## 📁 Project Structure

This is a monorepo containing the following components:

- `absolution/`: Core ML package for request classification
  - Binary and multi-class classification with DistilBERT
  - Out-of-distribution detection using energy-based methods
  - Built with PyTorch and Transformers
  - Pre-trained models for immediate deployment (50K+ samples)

- `firewall-app/`: **Web Application Firewall** ⭐
  - **3 deployment modes:** Reverse proxy, FastAPI middleware, Flask integration
  - Real-time inline request blocking
  - Integrates with absolution for ML-powered analysis
  - FastAPI application with async processing
  - RESTful API endpoints with comprehensive documentation
  - MySQL database with SQLAlchemy ORM
  - JWT authentication and API key management
  - Production-ready with Gunicorn + Nginx

- `www/vite-project/`: Frontend application
  - React + Vite + TypeScript web interface
  - Real-time analytics dashboard with live data
  - Interactive threat monitoring and incident management
  - Modern UI with Radix UI + Tailwind CSS
  - Zustand state management and React Query data fetching
  - Runs on port 5173

- `dataset-generator/`: Utility for generating training data
  - Helps create and manage training datasets
  - Supports data augmentation
  - Multiple attack pattern generators

## 🔧 Recent Improvements (Latest Update)

### ✅ **Frontend Static Data Issues Fixed**
- **Dynamic KPIs**: Replaced static values with real-time API data
- **Live Charts**: Time-series data with proper loading states
- **API Integration**: Consistent authentication across all endpoints
- **Environment Configuration**: Flexible API endpoint management
- **Error Handling**: Comprehensive error states and user feedback

### ✅ **Backend API Consistency**
- **Authentication**: Unified API key requirements across analytics endpoints
- **Documentation**: Updated API documentation to reflect current implementation
- **Performance**: Optimized database queries and response times
- **Security**: Enhanced JWT token management and validation

### ✅ **Production Readiness**
- **Empty States**: User-friendly messaging for no data scenarios
- **Loading States**: Skeleton components during data fetching
- **Responsive Design**: Mobile-optimized interface
- **Type Safety**: Full TypeScript coverage with strict type checking

## Prerequisites

- Docker and Docker Compose
- Git
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)
- Poetry (for Python dependency management)

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/vessa.git
   cd vessa
   ```

2. Start the development environment:
   ```bash
   docker-compose up --build
   ```

3. Access the applications:
   - Frontend Dashboard: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development Setup

### Backend Development

1. Navigate to the backend directory:
   ```bash
   cd firewall-app
   ```

2. Install dependencies with Poetry:
   ```bash
   poetry install
   ```

3. Run the development server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Development

1. Navigate to the frontend directory:
   ```bash
   cd www/vite-project
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   pnpm install
   ```

3. Create environment file:
   ```bash
   echo "VITE_API_BASE_URL=http://localhost:8000" > .env
   ```

4. Run the development server:
   ```bash
   npm run dev
   # or
   pnpm dev
   ```

### ML Package Development

1. Navigate to the absolution directory:
   ```bash
   cd absolution
   ```

2. Install dependencies with Poetry:
   ```bash
   poetry install
   ```

3. Run tests:
   ```bash
   poetry run pytest
   ```

## Docker Development

The project uses Docker Compose for development. The configuration includes:

- Hot-reloading for both frontend and backend
- Volume mounts for live code updates
- Network configuration for service communication
- Environment variables for configuration

### Available Docker Commands

- Start all services:
  ```bash
  docker-compose up
  ```

- Start services in detached mode:
  ```bash
  docker-compose up -d
  ```

- Rebuild and start services:
  ```bash
  docker-compose up --build
  ```

- Stop all services:
  ```bash
  docker-compose down
  ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Authors

- Jash Naik <jashnaik2004@gmail.com>
- Raj Shekhar <infojar001@gmail.com>

## Acknowledgments

- Thanks to all contributors and supporters of the project
- Special thanks to the open-source community for the amazing tools and libraries 
