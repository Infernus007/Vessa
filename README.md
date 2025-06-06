# Vessa - AI-Powered Web Application Firewall

Vessa is a comprehensive web application security solution that combines state-of-the-art machine learning models with a modern web interface for detecting and classifying malicious HTTP requests.

## Project Structure

This is a monorepo containing the following components:

- `absolution/`: Core ML package for request classification
  - Binary and multi-class classification
  - Out-of-distribution detection
  - Built with PyTorch and Transformers

- `firewall-app/`: Backend API service
  - FastAPI/Flask application
  - Integrates with absolution for request analysis
  - RESTful API endpoints
  - Runs on port 8000

- `www/`: Frontend application
  - Next.js web interface
  - Real-time request monitoring
  - Interactive dashboards
  - Runs on port 3000

- `dataset-generator/`: Utility for generating training data
  - Helps create and manage training datasets
  - Supports data augmentation

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
   - Frontend: http://localhost:3000
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
   cd www
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
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

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- Jash Naik <jashnaik2004@gmail.com>
- Raj Shekhar <infojar001@gmail.com>

## Acknowledgments

- Thanks to all contributors and supporters of the project
- Special thanks to the open-source community for the amazing tools and libraries 
