# Gmail AI Organizer

An open-source AI-powered email and calendar organization tool that connects to Gmail, intelligently categorizes emails, creates summaries, and provides a conversational interface to manage your inbox and schedule.

[![Tests](https://github.com/yourusername/gmail-ai-organizer/workflows/Tests/badge.svg)](https://github.com/yourusername/gmail-ai-organizer/actions)
[![Coverage](https://img.shields.io/badge/coverage-%3E80%25-brightgreen)](./docs/TESTING.md)

## 🧪 Quick Test (No API Keys Required!)

```bash
# Clone and test immediately - no configuration needed!
git clone <repo>
cd gmail-ai-organizer
./run-tests.sh --coverage
```

All tests use mocked services. No Google/AI API keys required! See [TESTING_QUICKSTART.md](TESTING_QUICKSTART.md) for details.

## Features

- 🔐 **Secure Gmail Integration** - OAuth2 authentication with Google APIs
- 🤖 **AI-Powered Organization** - Automatically tag, summarize, and classify emails
- 💬 **Chat Interface** - Conversational UI to manage emails and calendar
- 📅 **Calendar Integration** - Organize your schedule alongside your inbox
- 🔑 **Flexible API Keys** - Free tier with project keys OR bring your own keys (BYOK)
- 🎯 **Smart Filtering** - Separate real emails from clutter automatically
- 📊 **Email Analytics** - Insights into your email patterns
- 🌐 **Open Source** - Fully transparent and customizable

## Architecture

```
┌─────────────────┐
│  React Frontend │
│  (Chat UI)      │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  FastAPI │
    │  Backend │
    └─┬──┬──┬──┘
      │  │  │
  ┌───▼  │  └───┐
  │Gmail │Calendar│
  │ API  │  API  │
  └──────┴───────┘
         │
    ┌────▼────┐
    │ AI APIs │
    │Claude/  │
    │OpenAI   │
    └─────────┘
```

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **Frontend**: React 18+, TypeScript, Tailwind CSS
- **Database**: SQLite (local) / PostgreSQL (production)
- **AI**: Anthropic Claude API, OpenAI API (configurable)
- **APIs**: Google Gmail API, Google Calendar API

## API Key Strategy

### Free Tier (Project Keys)
- Limited monthly quota using project-provided API keys
- Perfect for trying out the application
- No setup required

### BYOK (Bring Your Own Keys)
- Unlimited usage with your own API keys
- Support for:
  - Anthropic Claude API
  - OpenAI API
  - Local models (Ollama, LM Studio)
- Configure in Settings panel

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Cloud Project with Gmail & Calendar APIs enabled
- (Optional) Anthropic or OpenAI API key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# - Add Google OAuth credentials
# - (Optional) Add AI API keys

# Run the backend
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to access the application.

## Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable APIs:
   - Gmail API
   - Google Calendar API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8000/auth/callback`
5. Download credentials and add to `.env`

## Configuration

### Environment Variables

```env
# Google OAuth
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# AI Configuration (Optional - for BYOK)
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key

# Free Tier Keys (Project-provided)
PROJECT_ANTHROPIC_KEY=limited_quota_key
PROJECT_OPENAI_KEY=limited_quota_key

# Database
DATABASE_URL=sqlite:///./gmail_organizer.db

# Security
SECRET_KEY=your_secret_key_here
```

## Features Detail

### Email Organization
- **Smart Categorization**: Automatically categorize emails (Important, Newsletter, Social, Promotions, etc.)
- **Summarization**: AI-generated summaries of long emails
- **Batch Actions**: Tag, archive, delete multiple emails through chat
- **Custom Rules**: Create personalized organization rules

### Calendar Integration
- **Smart Scheduling**: Extract meeting info from emails and create events
- **Availability Check**: Ask "When am I free this week?"
- **Event Summaries**: Get daily/weekly calendar summaries
- **Quick Actions**: "Schedule meeting with X next Tuesday at 2pm"

### Chat Interface Commands

```
"Summarize my unread emails"
"Show me important emails from this week"
"Archive all newsletters"
"When is my next meeting?"
"Schedule a meeting with John tomorrow at 3pm"
"What's on my calendar today?"
"Tag all emails from example.com as 'Work'"
```

## Project Structure

```
gmail-ai-organizer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration management
│   │   ├── models/              # Database models
│   │   ├── routers/             # API endpoints
│   │   │   ├── gmail.py
│   │   │   ├── calendar.py
│   │   │   ├── chat.py
│   │   │   └── auth.py
│   │   ├── services/
│   │   │   ├── gmail_service.py
│   │   │   ├── calendar_service.py
│   │   │   ├── ai_service.py
│   │   │   └── organizer.py
│   │   └── utils/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml
└── README.md
```

## Development

### Running Tests

We maintain **>80% test coverage** across both backend and frontend.

**Quick Test:**
```bash
./run-tests.sh
```

**With Coverage:**
```bash
./run-tests.sh --coverage
```

**Backend Only:**
```bash
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html  # View coverage report
```

**Frontend Only:**
```bash
cd frontend
npm run test:coverage
open coverage/index.html  # View coverage report
```

**Test Options:**
```bash
# Verbose output
./run-tests.sh --verbose

# Backend only
./run-tests.sh --backend

# Frontend only
./run-tests.sh --frontend

# Watch mode (frontend)
cd frontend && npm test -- --watch
```

See [docs/TESTING.md](docs/TESTING.md) for comprehensive testing guide.

### Test Coverage

- **Backend**: pytest with async support, mocked external APIs
- **Frontend**: Vitest + React Testing Library
- **Minimum Coverage**: 80% (lines, functions, branches, statements)
- **CI/CD**: Automated tests on all PRs via GitHub Actions

### Docker Deployment

```bash
docker-compose up -d
```

## Privacy & Security

- **Local-First**: All email data processed locally by default
- **No Data Collection**: We don't collect or store your emails
- **Open Source**: Audit the code yourself
- **Secure OAuth**: Industry-standard Google authentication
- **Encrypted Storage**: Local database encryption support

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap

- [ ] Multi-account support
- [ ] Outlook/Microsoft 365 integration
- [ ] Mobile app (React Native)
- [ ] Browser extension
- [ ] Local AI models (Ollama support)
- [ ] Email templates
- [ ] Advanced analytics dashboard
- [ ] Team collaboration features

## License

MIT License - see [LICENSE](LICENSE) file for details

## Support

- 📖 [Documentation](docs/)
- 💬 [Discussions](https://github.com/yourusername/gmail-ai-organizer/discussions)
- 🐛 [Issue Tracker](https://github.com/yourusername/gmail-ai-organizer/issues)

## Acknowledgments

- Google APIs for Gmail and Calendar integration
- Anthropic Claude for AI capabilities
- FastAPI for the excellent Python framework
- React community for frontend tools

---

**Note**: This tool requires appropriate Google API quotas and AI API access. Free tier limits apply unless using BYOK.
