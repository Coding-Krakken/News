<<<<<<< HEAD
# News Application

A full-stack news application with secure user authentication, profiles, bookmarks, saved filters, and personalized news feeds.

## Features

- ✅ **Secure Authentication**: JWT-based authentication with refresh token rotation
- ✅ **User Profiles**: View and edit user profiles with avatar support
- ✅ **Bookmarks**: Save articles and stories for later reading
- ✅ **Saved Filters**: Create and manage custom news filters
- ✅ **Personalized Feed**: Get news based on your preferences
- ✅ **100% Test Coverage**: Comprehensive unit, integration, and E2E tests

## Tech Stack

### Backend
- Node.js with Express
- TypeScript
- PostgreSQL database
- Argon2id password hashing
- JWT authentication with refresh tokens
- Rate limiting and security headers
- Structured logging with PII redaction

### Frontend
- React 18 with TypeScript
- React Router for navigation
- Axios for API communication
- Vite for development and building

### Testing
- Jest for unit and integration tests
- Playwright for E2E tests
- 100% code coverage requirement

## Prerequisites

- Node.js 18+ and npm
- Docker and Docker Compose (for PostgreSQL)
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Coding-Krakken/News.git
cd News
```

### 2. Start the Database

```bash
docker-compose up -d
```

This will start PostgreSQL containers for both development and testing.

### 3. Set Up the Backend

```bash
cd backend
npm install
cp .env.example .env
```

Edit `.env` if needed to configure your environment.

Run database migrations:

```bash
# Install PostgreSQL client tools if not available
# Then run migrations manually or use a migration tool
psql -h localhost -U news_user -d news_db < migrations/1702000001_create_users_table.sql
psql -h localhost -U news_user -d news_db < migrations/1702000002_create_user_preferences_table.sql
psql -h localhost -U news_user -d news_db < migrations/1702000003_create_bookmarks_table.sql
psql -h localhost -U news_user -d news_db < migrations/1702000004_create_saved_filters_table.sql
psql -h localhost -U news_user -d news_db < migrations/1702000005_create_refresh_tokens_table.sql
```

Start the backend server:

```bash
**News Analytics Platform**

A comprehensive news analytics platform that ingests articles from multiple sources, clusters them into story events, computes coverage statistics, and provides AI-powered fact-checking capabilities.

This repository contains both the core analytics platform and a complete user authentication and personalization system (user profiles, bookmarks, saved filters, and custom feeds).

## Quick Start

### Local Development (Docker Compose)
```bash
git clone https://github.com/Coding-Krakken/News.git
cd News
cp backend/.env.example backend/.env
# Edit backend/.env if needed
docker compose up
```

Visit http://localhost:3000 (backend) and http://localhost:3001 (frontend) for the app.

### Production Deployment
See **[DEPLOYMENT.md](DEPLOYMENT.md)** for complete deployment instructions, including cloud deployment options and environment configuration.

## Features

### Core Analytics
- Multi-source news ingestion (RSS/APIs)
- Story clustering (embeddings + DBSCAN)
- Coverage analytics by source, category, geography, time, ideology
- Fact extraction and cross-source corroboration

### Authentication & Personalization
- JWT-based authentication with refresh token rotation
- Argon2id password hashing
- User profiles (view/edit)
- Bookmarks (articles & stories)
- Saved filters (JSON queries)
- Personalized custom feeds based on preferences

## Tech Stack

### Backend
- Node.js (Express) &/or FastAPI components
- TypeScript & Python components in the repo
- PostgreSQL and/or MongoDB depending on service

### Frontend
- React 18 with TypeScript
- Vite for development

### Testing
- Jest for unit/integration tests
- Playwright for E2E tests

## Development

Follow the Quick Start above to start services locally. See `backend/` and `frontend/` directories for per-service instructions and scripts.


## Running the Application

### Start MongoDB
If running locally:
```bash
mongod
```

### Start Backend Server
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

API Documentation: http://localhost:8000/docs

### Start Frontend Development Server
```bash
cd frontend
npm run dev
```

The application will be available at http://localhost:3000

## Usage

### 1. Ingest Articles
Click "Ingest Articles" to fetch latest articles from configured news sources. The platform comes with several pre-configured sources including BBC News, CNN, Reuters, and The Guardian.

### 2. Cluster Stories
After ingesting articles, click "Cluster Stories" to group related articles into story events using machine learning.

### 3. Explore Stories
Browse the story cards to see:
- Number of articles covering each story
- Which sources covered the story
- Story category and metadata

### 4. Filter Stories
Use the faceted filters to include or exclude:
- Specific news sources
- Categories
- Geographic regions
- Ideological perspectives

### 5. View Story Details
Click on any story to see:
- All articles in the story
- Coverage matrix showing which sources covered it
- Option to generate AI fact analysis

### 6. Generate Fact Ledger
Click "Generate Fact Ledger" on any story to:
- Extract claims from all articles
- Cross-corroborate facts across sources
- See which claims are confirmed, disputed, or uncorroborated
- View attribution for each claim

### 7. View Analytics
Navigate to the Analytics page to see comprehensive statistics:
- Total articles and stories
- Breakdown by source, category, geography, ideology, and time

## API Endpoints

### Articles
- `POST /api/articles/ingest` - Ingest articles from all sources
- `GET /api/articles/` - Get all articles with filtering
- `GET /api/articles/sources/list` - List configured sources
- `POST /api/articles/sources/add` - Add a new source

### Stories
- `POST /api/stories/cluster` - Trigger story clustering
- `GET /api/stories/` - Get all stories
- `GET /api/stories/{story_id}` - Get specific story
- `GET /api/stories/{story_id}/articles` - Get articles in story
- `GET /api/stories/{story_id}/coverage` - Get coverage matrix

### Analytics
- `GET /api/analytics/stats` - Get coverage statistics
- `GET /api/analytics/filter` - Filter articles by criteria
- `GET /api/analytics/facets` - Get available filter options

### Fact Checker
- `POST /api/fact-checker/{story_id}` - Generate fact ledger
- `GET /api/fact-checker/{story_id}` - Get existing fact ledger

## Adding News Sources

You can add new RSS sources through the API:

```bash
curl -X POST "http://localhost:8000/api/articles/sources/add" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Source",
    "url": "https://example.com/rss",
    "source_type": "rss",
    "ideology": "center",
    "geography": "United States"
  }'
```

## Configuration

### Clustering Parameters
Edit `backend/app/services/clustering.py` to adjust:
- `similarity_threshold`: Minimum similarity for clustering (default: 0.7)
- `time_window_hours`: Time window for clustering articles (default: 72 hours)

### AI Fact-Checking
The fact-checking feature works in two modes:
1. **With OpenAI API**: Uses GPT-3.5 for advanced claim extraction
2. **Fallback Mode**: Simple rule-based extraction if API key is not configured

## Technology Stack

**Backend:**
- FastAPI - Web framework
- Motor - Async MongoDB driver
- Sentence Transformers - NLP embeddings
- scikit-learn - Machine learning (DBSCAN clustering)
- feedparser - RSS parsing
- OpenAI - AI claim extraction
- BeautifulSoup - HTML parsing

**Frontend:**
- React 18 - UI framework
- Vite - Build tool
- Axios - HTTP client

**Testing:**
- **Backend**: pytest, pytest-asyncio, pytest-cov, httpx, mongomock-motor
- **Frontend**: Vitest, React Testing Library, jsdom, MSW

**Database:**
- MongoDB - Document storage

## Development

### Backend Tests

The platform includes a comprehensive test suite with **95%+ code coverage**:

```bash
cd backend
./run_tests.sh
```

**Test Statistics:**
- 112+ test functions across 11 test files
- Unit, Integration, and E2E tests
- Mock database for testing
- Async test support

**Run specific tests:**
```bash
pytest tests/unit/ -v           # Unit tests
pytest tests/integration/ -v     # Integration tests
pytest tests/e2e/ -v            # End-to-end tests
```

**Coverage report:**
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

See `backend/tests/README.md` for detailed test documentation.

### Frontend Tests

Comprehensive frontend test suite with **80%+ code coverage**:

```bash
cd frontend
./run_tests.sh
```

**Test Statistics:**
- 70+ test functions across 7 test files
- Component, Page, and Service tests
- React Testing Library
- Mock API responses

**Run specific tests:**
```bash
npm test                    # Watch mode
npm run test:coverage       # With coverage
npm run test:ui             # UI mode
```

**Coverage report:**
```bash
npm run test:coverage
open coverage/index.html
```

See `frontend/TEST_README.md` for detailed test documentation.

### Frontend Build
```bash
cd frontend
npm run build
```

Production build will be in `frontend/dist/`

>>>>>>> origin/main
## Project Structure

```
News/
├── backend/
<<<<<<< HEAD
│   ├── migrations/          # Database migrations
│   ├── src/
│   │   ├── config/         # Configuration files
│   │   ├── controllers/    # Request handlers
│   │   ├── middleware/     # Express middleware
│   │   ├── models/         # Data models
│   │   ├── routes/         # API routes
│   │   ├── services/       # Business logic & repositories
│   │   ├── utils/          # Utility functions
│   │   ├── test/           # Test helpers
│   │   ├── __tests__/      # Integration tests
│   │   ├── app.ts          # Express app setup
│   │   └── index.ts        # Server entry point
│   └── package.json
├── frontend/
│   ├── e2e/                # E2E tests
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── contexts/       # React contexts
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── types/          # TypeScript types
│   │   ├── App.tsx         # Main app component
│   │   └── main.tsx        # Entry point
│   └── package.json
├── docker-compose.yml      # Docker setup for PostgreSQL
└── README.md              # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all tests pass
5. Submit a pull request

## License

MIT
=======
│   ├── app/
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
<!--
Unified README: combines the analytics platform documentation with the
authentication & personalization features added in this branch.
-->

# News Analytics Platform + Personalization

A comprehensive news analytics platform that ingests articles from multiple sources, clusters them into story events, computes coverage statistics, and provides AI-powered fact-checking capabilities.

This repository includes both the core analytics services and a complete
user authentication and personalization system (user profiles, bookmarks,
saved filters, and custom feeds).

## Quick Start (local)

1. Clone the repo:

```bash
git clone https://github.com/Coding-Krakken/News.git
cd News
```

2. Copy example envs and start services (using Docker Compose):

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```

3. Backend API: http://localhost:3000 (or 8000 for analytics services)
   Frontend: http://localhost:3001 (or 3000 depending on service)

See `backend/` and `frontend/` directories for service-specific scripts and
testing instructions.

## Major Features

- Multi-source ingestion, story clustering, and coverage analytics
- AI-powered claim extraction and fact corroboration
- User authentication (JWT + refresh tokens)
- User profiles, bookmarks, saved filters
- Personalized custom feeds

## Documentation

- Deployment: DEPLOYMENT.md
- Security: docs/SECURITY.md
- User guide: docs/USER_GUIDE.md
- Implementation notes: IMPLEMENTATION_SUMMARY.md

## Development & Tests

Each subproject contains its own test scripts. Typical commands:

```bash
# Backend
cd backend && npm install && npm test

# Frontend
cd frontend && npm install && npm test

# E2E (Playwright)
cd frontend && npm run test:e2e
```

## License

MIT
