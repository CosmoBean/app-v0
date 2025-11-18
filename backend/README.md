# Gmail AI Organizer - Backend

FastAPI backend for the Gmail AI Organizer application.

## Quick Start

### Running Tests (No API Keys Needed!)

```bash
# From project root
./run-tests.sh --backend

# Or from backend directory
cd backend
pytest
```

Tests use mocked services and don't require any real API keys.

### Development Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For testing
cp .env.test .env  # Or create your own .env

# Run server
uvicorn app.main:app --reload
```

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_ai_service.py

# Watch mode (requires pytest-watch)
pip install pytest-watch
ptw

# View coverage report
open htmlcov/index.html
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_config.py
│   ├── test_ai_service.py
│   ├── test_gmail_service.py
│   ├── test_calendar_service.py
│   └── test_organizer.py
└── integration/             # Integration tests
    ├── test_auth_api.py
    ├── test_gmail_api.py
    ├── test_calendar_api.py
    └── test_chat_api.py
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

See `.env.example` for all configuration options. For testing, defaults are provided in the code.

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── models/              # Database models
│   ├── routers/             # API endpoints
│   ├── services/            # Business logic
│   └── utils/               # Utilities
├── tests/                   # Test suite
├── requirements.txt         # Dependencies
└── pytest.ini              # Test configuration
```

## Development

```bash
# Run server with auto-reload
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black app/

# Lint
flake8 app/
```

## Production

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

See main [README.md](../README.md) for full documentation.
