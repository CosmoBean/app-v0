# Gmail AI Organizer - Frontend

React + TypeScript frontend for the Gmail AI Organizer application.

## Quick Start

### Running Tests (No Setup Needed!)

```bash
# From project root
./run-tests.sh --frontend

# Or from frontend directory
cd frontend
npm test
```

Tests are fully mocked and don't require any backend or API keys.

### Development Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open browser at http://localhost:5173
```

## Running Tests

```bash
# Run tests
npm test

# With coverage
npm run test:coverage

# Interactive UI
npm run test:ui

# Watch mode
npm test -- --watch

# View coverage report
open coverage/index.html
```

## Test Structure

```
src/test/
├── setup.ts                 # Test configuration
├── utils/
│   └── test-utils.tsx       # Testing utilities
├── mocks/
│   └── mockData.ts          # Mock data
├── components/              # Component tests
│   ├── ChatInterface.test.tsx
│   ├── EmailList.test.tsx
│   └── CalendarView.test.tsx
├── pages/                   # Page tests
│   └── LoginPage.test.tsx
├── services/                # Service tests
│   └── api.test.ts
└── store/                   # Store tests
    └── authStore.test.ts
```

## Scripts

```bash
npm run dev           # Development server
npm run build         # Production build
npm run preview       # Preview production build
npm run test          # Run tests
npm run test:coverage # Run tests with coverage
npm run test:ui       # Interactive test UI
npm run lint          # Lint code
```

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Router** - Routing
- **Axios** - HTTP client
- **Vitest** - Testing
- **React Testing Library** - Component testing

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   ├── pages/               # Page components
│   ├── services/            # API services
│   ├── store/               # State management
│   ├── types/               # TypeScript types
│   ├── test/                # Test files
│   ├── App.tsx              # Main app component
│   └── main.tsx             # Entry point
├── public/                  # Static assets
├── package.json
└── vite.config.ts
```

## Development

```bash
# Start dev server
npm run dev

# Run tests in watch mode
npm test -- --watch

# Lint code
npm run lint

# Build for production
npm run build
```

## Environment Variables

Create `.env.local` for local development:

```env
VITE_API_URL=http://localhost:8000
```

See main [README.md](../README.md) for full documentation.
