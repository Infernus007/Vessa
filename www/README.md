# Vessa Frontend

A modern Next.js web application for monitoring and managing the Vessa Web Application Firewall. Provides real-time request analysis, threat detection, and security monitoring capabilities.

## Features

- Real-time request monitoring
- Interactive security dashboards
- Request analysis visualization
- Attack pattern detection
- User authentication and authorization
- Responsive design

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
www/
├── app/                # Next.js 13+ app directory
│   ├── api/           # API routes
│   ├── (auth)/        # Authentication pages
│   ├── dashboard/     # Dashboard pages
│   └── layout.tsx     # Root layout
├── components/        # Reusable components
│   ├── ui/           # UI components
│   ├── forms/        # Form components
│   └── charts/       # Chart components
├── lib/              # Utility functions
├── styles/           # Global styles
├── public/           # Static assets
└── types/            # TypeScript types
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run test` - Run tests
- `npm run type-check` - Run TypeScript type checking

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run directly with Docker
docker build -t vessa-frontend .
docker run -p 3000:3000 vessa-frontend
```

## Technologies Used

- Next.js 13+
- TypeScript
- Tailwind CSS
- Shadcn/ui
- React Query
- Chart.js
- Jest
- Playwright

## Development Guidelines

1. Follow the [Next.js App Router](https://nextjs.org/docs/app) conventions
2. Use TypeScript for all new code
3. Write tests for new features
4. Follow the component structure in `components/`
5. Use the provided UI components from `components/ui/`

## Testing

```bash
# Run unit tests
npm run test

# Run E2E tests
npm run test:e2e

# Run with coverage
npm run test:coverage
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details 