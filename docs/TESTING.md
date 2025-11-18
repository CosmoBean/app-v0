# Testing Guide

This document provides comprehensive information about testing the Gmail AI Organizer application.

## Table of Contents

- [Overview](#overview)
- [Backend Testing](#backend-testing)
- [Frontend Testing](#frontend-testing)
- [Test Coverage](#test-coverage)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [CI/CD Integration](#cicd-integration)

## Overview

The project maintains high test coverage (>80%) across both backend and frontend:

- **Backend**: pytest with async support
- **Frontend**: Vitest with React Testing Library
- **Coverage**: Enforced minimum 80% coverage
- **CI/CD**: Automated testing on all PRs

## Backend Testing

### Technology Stack

- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities
- **httpx**: HTTP client for testing

### Test Structure

```
backend/tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Unit tests
│   ├── test_config.py
│   ├── test_ai_service.py
│   ├── test_gmail_service.py
│   ├── test_calendar_service.py
│   └── test_organizer.py
└── integration/          # Integration tests
    ├── test_auth_api.py
    ├── test_gmail_api.py
    ├── test_calendar_api.py
    └── test_chat_api.py
```

### Running Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_ai_service.py

# Run tests matching pattern
pytest -k "test_gmail"

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Backend Test Examples

**Unit Test Example:**
```python
import pytest
from app.services.ai_service import AIService

@pytest.mark.unit
@pytest.mark.asyncio
async def test_summarize_email(mock_ai_service):
    """Test email summarization"""
    summary = await mock_ai_service.summarize_email(
        "This is a test email about a meeting"
    )
    assert isinstance(summary, str)
    assert len(summary) > 0
```

**Integration Test Example:**
```python
@pytest.mark.integration
def test_get_messages(client, sample_email):
    """Test Gmail messages endpoint"""
    response = client.post(
        "/gmail/messages",
        json={"max_results": 10},
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
```

## Frontend Testing

### Technology Stack

- **Vitest**: Test framework
- **React Testing Library**: Component testing
- **@testing-library/user-event**: User interaction simulation
- **jsdom**: DOM environment
- **MSW**: API mocking

### Test Structure

```
frontend/src/test/
├── setup.ts              # Test configuration
├── utils/
│   └── test-utils.tsx    # Testing utilities
├── mocks/
│   └── mockData.ts       # Mock data
├── components/           # Component tests
│   ├── ChatInterface.test.tsx
│   ├── EmailList.test.tsx
│   └── CalendarView.test.tsx
├── pages/                # Page tests
│   └── LoginPage.test.tsx
├── services/             # Service tests
│   └── api.test.ts
└── store/                # Store tests
    └── authStore.test.ts
```

### Running Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run with UI
npm run test:ui

# Watch mode
npm test -- --watch

# Run specific test file
npm test -- ChatInterface.test

# Update snapshots
npm test -- -u
```

### Coverage Reports

```bash
# Generate coverage report
npm run test:coverage

# View report
open coverage/index.html  # macOS
xdg-open coverage/index.html  # Linux
```

### Frontend Test Examples

**Component Test Example:**
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '../utils/test-utils'
import ChatInterface from '../../components/ChatInterface'

describe('ChatInterface', () => {
  it('should render initial message', () => {
    render(<ChatInterface />)
    expect(screen.getByText(/AI email assistant/i)).toBeInTheDocument()
  })

  it('should handle user input', () => {
    render(<ChatInterface />)
    const input = screen.getByPlaceholderText(/Ask me anything/i)

    fireEvent.change(input, { target: { value: 'Test' } })
    expect(input.value).toBe('Test')
  })
})
```

**Store Test Example:**
```typescript
import { describe, it, expect } from 'vitest'
import { useAuthStore } from '../../store/authStore'

describe('AuthStore', () => {
  it('should set authentication data', () => {
    useAuthStore.getState().setAuth({
      accessToken: 'token',
      userEmail: 'test@example.com',
    })

    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(true)
  })
})
```

## Test Coverage

### Coverage Requirements

Both backend and frontend enforce minimum 80% coverage:

- **Lines**: 80%
- **Functions**: 80%
- **Branches**: 80%
- **Statements**: 80%

### Viewing Coverage

**Backend:**
```bash
cd backend
pytest --cov=app --cov-report=term-missing
```

**Frontend:**
```bash
cd frontend
npm run test:coverage
```

### Coverage Badge

Add to your README:
```markdown
[![codecov](https://codecov.io/gh/USERNAME/REPO/branch/main/graph/badge.svg)](https://codecov.io/gh/USERNAME/REPO)
```

## Writing Tests

### Best Practices

1. **Test Naming**
   - Use descriptive names: `test_should_archive_email_when_category_is_newsletter`
   - Follow pattern: `test_<what>_<when>_<expected>`

2. **Arrange-Act-Assert**
   ```python
   def test_example():
       # Arrange
       user = create_user()

       # Act
       result = user.do_something()

       # Assert
       assert result.is_success()
   ```

3. **Mock External Services**
   - Always mock API calls
   - Mock datetime for time-dependent tests
   - Use fixtures for common mocks

4. **Test One Thing**
   - Each test should verify one behavior
   - Keep tests focused and simple

5. **Use Fixtures**
   ```python
   @pytest.fixture
   def sample_email():
       return {
           "id": "email123",
           "subject": "Test",
           # ...
       }
   ```

### What to Test

**Backend:**
- ✅ Service methods
- ✅ API endpoints
- ✅ Data validation
- ✅ Error handling
- ✅ Authentication
- ❌ Third-party libraries
- ❌ Configuration loading

**Frontend:**
- ✅ Component rendering
- ✅ User interactions
- ✅ State management
- ✅ API integration
- ✅ Routing
- ❌ External libraries
- ❌ CSS styling

### Test Markers

**Backend:**
```python
@pytest.mark.unit          # Unit test
@pytest.mark.integration   # Integration test
@pytest.mark.slow          # Slow running test
@pytest.mark.asyncio       # Async test
```

**Frontend:**
```typescript
describe.skip('...', () => {})  // Skip test suite
it.only('...', () => {})        // Run only this test
```

## CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

### Workflow Jobs

1. **Backend Tests**
   - Python 3.11
   - Run pytest with coverage
   - Upload to Codecov

2. **Frontend Tests**
   - Node.js 18
   - Run Vitest with coverage
   - Upload to Codecov

3. **Linting**
   - Black, flake8 (Python)
   - ESLint (TypeScript)

4. **Security Scan**
   - Trivy vulnerability scanner
   - Upload to GitHub Security

### Local Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Debugging Tests

### Backend

```bash
# Print output
pytest -s

# Drop into debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l

# Verbose with full diff
pytest -vv
```

### Frontend

```bash
# Debug mode
npm test -- --reporter=verbose

# Run in browser
npm run test:ui
```

## Performance Testing

### Backend

```bash
# Install locust
pip install locust

# Run load tests
locust -f tests/performance/locustfile.py
```

### Frontend

```bash
# Install lighthouse
npm install -g lighthouse

# Run performance audit
lighthouse http://localhost:5173 --view
```

## Troubleshooting

### Common Issues

**Backend:**
- Async test not awaited: Add `@pytest.mark.asyncio`
- Import errors: Check `sys.path` in `conftest.py`
- Mock not working: Use `pytest-mock` fixtures

**Frontend:**
- Component not found: Check test-utils wrapper
- Async state not updated: Use `waitFor`
- API mock not working: Verify MSW handlers

### Getting Help

- Check test output carefully
- Read error messages fully
- Search existing issues
- Ask in discussions

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Vitest documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Best Practices](https://testingjavascript.com/)

---

**Remember**: Good tests are:
- Fast
- Isolated
- Repeatable
- Self-validating
- Timely
