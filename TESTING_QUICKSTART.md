# Testing Quick Start

This guide helps you run tests immediately without any API keys or configuration.

## TL;DR - Run Tests Now

```bash
# Run all tests (no API keys needed!)
./run-tests.sh

# With coverage reports
./run-tests.sh --coverage
```

That's it! Tests use mocked services and don't require any real API keys.

## Prerequisites

- **Backend**: Python 3.11+
- **Frontend**: Node.js 18+

## First Time Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy test environment (optional - has defaults)
cp .env.test .env
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

## Running Tests

### Option 1: Unified Test Runner (Recommended)

```bash
# Run all tests
./run-tests.sh

# With HTML coverage reports
./run-tests.sh --coverage

# Backend only
./run-tests.sh --backend

# Frontend only
./run-tests.sh --frontend

# Verbose output
./run-tests.sh --verbose
```

### Option 2: Manual Testing

**Backend:**
```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_ai_service.py

# Specific test
pytest tests/unit/test_ai_service.py::TestAIService::test_summarize_email

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

**Frontend:**
```bash
cd frontend

# Run all tests
npm test

# With coverage
npm run test:coverage

# Interactive UI
npm run test:ui

# Watch mode
npm test -- --watch

# View coverage report
open coverage/index.html  # macOS
xdg-open coverage/index.html  # Linux
start coverage/index.html  # Windows
```

## What Gets Tested

### Backend (97 tests)
- ✅ Configuration management
- ✅ AI services (summarization, categorization, tagging)
- ✅ Gmail operations (fetch, modify, archive, send)
- ✅ Calendar operations (create, update, delete, query)
- ✅ Email organization (batch processing, smart archiving)
- ✅ API endpoints (auth, gmail, calendar, chat)
- ✅ Error handling

### Frontend (33 tests)
- ✅ Component rendering
- ✅ User interactions
- ✅ State management
- ✅ API integration
- ✅ Routing
- ✅ Form handling

## FAQ

### Do I need API keys to run tests?

**No!** All external services are mocked:
- Google APIs (Gmail, Calendar, OAuth)
- AI APIs (Anthropic, OpenAI)
- No network calls are made during tests

### Do I need a .env file?

**No!** The configuration has sensible defaults for testing. However, you can copy `.env.test` to `.env` if you want to customize test settings.

### Tests are failing. What should I do?

1. **Check dependencies:**
   ```bash
   # Backend
   cd backend && pip install -r requirements.txt

   # Frontend
   cd frontend && npm install
   ```

2. **Clear cache:**
   ```bash
   # Backend
   cd backend && rm -rf __pycache__ .pytest_cache

   # Frontend
   cd frontend && rm -rf node_modules && npm install
   ```

3. **Run with verbose output:**
   ```bash
   ./run-tests.sh --verbose
   ```

4. **Check specific test:**
   ```bash
   # Backend
   cd backend && pytest tests/unit/test_config.py -v

   # Frontend
   cd frontend && npm test -- ChatInterface.test
   ```

### How do I run a single test?

**Backend:**
```bash
cd backend
pytest tests/unit/test_ai_service.py::TestAIService::test_summarize_email -v
```

**Frontend:**
```bash
cd frontend
npm test -- ChatInterface.test
```

### How do I see test coverage?

**Quick view in terminal:**
```bash
./run-tests.sh --coverage
```

**Detailed HTML report:**
```bash
# Backend
cd backend && pytest --cov=app --cov-report=html
open htmlcov/index.html

# Frontend
cd frontend && npm run test:coverage
open coverage/index.html
```

### Can I run tests in watch mode?

**Yes, for frontend:**
```bash
cd frontend
npm test -- --watch
```

**For backend, use pytest-watch:**
```bash
pip install pytest-watch
cd backend
ptw
```

### How do I debug a failing test?

**Backend:**
```bash
# Drop into debugger on failure
cd backend
pytest --pdb

# Print output
pytest -s

# Verbose with local variables
pytest -vv -l
```

**Frontend:**
```bash
# Use interactive UI
cd frontend
npm run test:ui
```

### What's the coverage target?

**80% minimum** for both backend and frontend:
- Lines: 80%
- Functions: 80%
- Branches: 80%
- Statements: 80%

### How long do tests take?

- Backend: ~10-15 seconds
- Frontend: ~5-10 seconds
- Total: **< 30 seconds**

## CI/CD

Tests run automatically on:
- Every push to `main` or `develop`
- Every pull request
- No API keys needed in CI/CD either!

## Next Steps

1. **Run tests**: `./run-tests.sh --coverage`
2. **View coverage**: Open the HTML reports
3. **Write more tests**: See `docs/TESTING.md` for guidelines
4. **Contribute**: Tests must pass before merging PRs

## Need Help?

- 📖 Full testing guide: [docs/TESTING.md](docs/TESTING.md)
- 🐛 Issues: Check GitHub issues
- 💬 Questions: Open a discussion

---

**Remember**: All tests use mocks. No real API keys needed! 🎉
