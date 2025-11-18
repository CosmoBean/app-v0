# Contributing to Gmail AI Organizer

Thank you for your interest in contributing to Gmail AI Organizer! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/gmail-ai-organizer.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

## Development Setup

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Using Docker

```bash
docker-compose up -d
```

## Code Style

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for functions and classes
- Use meaningful variable names
- Keep functions small and focused

Example:
```python
async def process_email(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process email with AI.

    Args:
        email_data: Email data from Gmail API

    Returns:
        Processed email with AI-generated fields
    """
    # Implementation
```

### TypeScript/React (Frontend)

- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Keep components small and reusable
- Use meaningful prop names

Example:
```typescript
interface EmailListProps {
  emails: Email[]
  onEmailSelect: (email: Email) => void
}

export function EmailList({ emails, onEmailSelect }: EmailListProps) {
  // Implementation
}
```

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Pull Request Guidelines

1. **Title**: Use clear, descriptive titles
   - ✅ "Add email batch processing feature"
   - ❌ "Update code"

2. **Description**: Explain what and why
   - What changes were made
   - Why they were necessary
   - Any breaking changes
   - Screenshots for UI changes

3. **Testing**: Describe how you tested
   - Manual testing steps
   - Automated tests added
   - Edge cases considered

4. **Keep it focused**: One feature/fix per PR

5. **Update documentation**: Update README if needed

## Commit Messages

Follow conventional commits format:

```
type(scope): brief description

Detailed explanation if needed

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat(ai): add support for local AI models

fix(gmail): resolve pagination issue in email fetching

docs(readme): update installation instructions
```

## Feature Requests

Open an issue with:
- Clear description of the feature
- Use cases and benefits
- Potential implementation approach
- Any related issues or PRs

## Bug Reports

Open an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages or logs
- Screenshots if applicable

## Code Review Process

1. Maintainers will review within 1-3 days
2. Address feedback promptly
3. Be open to suggestions
4. Discuss major changes before implementing

## Security

- Never commit credentials or API keys
- Use environment variables for sensitive data
- Report security issues privately to maintainers
- Don't open public issues for security vulnerabilities

## Documentation

- Update README for new features
- Add inline comments for complex logic
- Update API documentation for new endpoints
- Include usage examples where helpful

## Questions?

- Open a discussion on GitHub
- Join our community chat (if available)
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing to Gmail AI Organizer!
