# News Analytics Platform + Authentication

A comprehensive news analytics platform that ingests articles from multiple sources, clusters them into story events, computes coverage statistics, and provides AI-powered fact-checking capabilities. This repository includes both the core analytics services and a complete user authentication and personalization system.

## Features

### Core Analytics

- **Multi-source ingestion**: Ingest from RSS, APIs, and web scraping
- **Story clustering**: Automatically group related articles
- **Coverage analysis**: See which outlets cover which stories
- **Fact-checking**: AI-powered claim extraction and corroboration
- **Analytics dashboard**: Comprehensive statistics and filtering

### Authentication & Personalization

- ✅ **Secure Authentication**: JWT-based auth with refresh token rotation
- ✅ **User Profiles**: View and edit profiles with avatar support
- ✅ **Bookmarks**: Save articles and stories for later reading
- ✅ **Saved Filters**: Create and manage custom news filters
- ✅ **Personalized Feed**: Get news based on your preferences
- ✅ **100% Test Coverage**: Comprehensive unit, integration, and E2E tests

## Tech Stack

### Backend

- **Analytics**: Python with FastAPI, Motor (async MongoDB)
- **Auth API**: Node.js with Express, TypeScript, PostgreSQL
- **NLP**: Sentence Transformers, scikit-learn (DBSCAN clustering)
- **Security**: Argon2id password hashing, JWT with refresh tokens
- **Testing**: pytest, Jest with 100% coverage requirement

### Frontend

- React 18 with TypeScript
- Vite for development and building
- React Router for navigation
- Axios for API communication

### Testing

- Jest for unit/integration tests
- Playwright for E2E tests
- 100% code coverage enforced in CI

## Prerequisites

- Node.js 18+ and npm
- Python 3.12+
- Docker and Docker Compose
- MongoDB (for analytics) or PostgreSQL (for auth)
- Git

## Quick Start

### Local Development (Docker Compose)

\`\`\`bash
git clone https://github.com/Coding-Krakken/News.git
cd News
cp backend/.env.example backend/.env

# Edit backend/.env if needed

docker compose up
\`\`\`

- Analytics API: http://localhost:8000
- Auth API: http://localhost:3000
- Frontend: http://localhost:3001
- API Docs: http://localhost:8000/docs

### Production Deployment

See \`DEPLOYMENT.md\` for detailed production deployment instructions including:

- Railway backend deployment
- Vercel frontend deployment
- Environment configuration
- SSL/TLS setup

## CI/CD

The project includes automated GitHub Actions workflows that enforce quality standards:

**CI Pipeline (\`.github/workflows/ci.yml\`):**

- ✅ Backend tests with PostgreSQL service container
- ✅ Frontend tests with 100% coverage enforcement
- ✅ E2E tests with Playwright
- ✅ Build validation
- ✅ Artifact uploads for test reports
- ✅ Explicit least-privilege permissions
- ✅ Deterministic builds with npm ci
- ✅ Node.js 18 pinned via .nvmrc and package.json engines

**Quality Gates (All Must Pass):**

- ✅ Linting (ESLint)
- ✅ Type checking (TypeScript)
- ✅ Unit tests
- ✅ Integration tests
- ✅ E2E tests (Playwright)
- ✅ 100% code coverage on auth backend (lines/branches/functions/statements)
- ✅ 95%+ coverage on analytics backend
- ✅ 80%+ coverage on frontend

**Running CI Checks Locally:**
\`\`\`bash

# Backend lint

cd backend && npm run lint

# Backend typecheck

cd backend && npm run build

# Backend tests

cd backend && npm test

# Frontend lint

cd frontend && npm run lint

# Frontend tests

cd frontend && npm test

# E2E tests

cd frontend && npm run test:e2e
\`\`\`

**Accessing Test Artifacts:**

- Playwright reports are uploaded to GitHub Actions artifacts
- Coverage reports available in CI logs
- Retention: 30 days for Playwright reports

## Development

Follow the Quick Start above to start services locally. See \`backend/\` and \`frontend/\` directories for per-service instructions and scripts.

## Testing

### Backend Tests (Node.js Auth)

Run all tests with coverage:
\`\`\`bash
cd backend
npm test
\`\`\`

Run unit tests only:
\`\`\`bash
npm run test:unit
\`\`\`

Run integration tests only:
\`\`\`bash
npm run test:integration
\`\`\`

### Backend Tests (Python Analytics)

\`\`\`bash
cd backend
./run_tests.sh
\`\`\`

**Test Statistics:**

- 112+ test functions across 11 test files
- Unit, Integration, and E2E tests
- Mock database for testing
- Async test support

### Frontend Tests

\`\`\`bash
cd frontend
npm test
\`\`\`

**Test Statistics:**

- 70+ test functions across 7 test files
- Component, Page, and Service tests
- React Testing Library
- Mock API responses

### E2E Tests

\`\`\`bash
cd frontend
npm run test:e2e
\`\`\`

## API Endpoints

### Auth API

**Authentication:**

- \`POST /api/auth/signup\` - User registration
- \`POST /api/auth/login\` - User login
- \`POST /api/auth/logout\` - Revoke tokens
- \`GET /api/auth/me\` - Get current user
- \`POST /api/auth/refresh\` - Rotate tokens

**User Management:**

- \`PATCH /api/users/me\` - Update profile
- \`GET /api/users/me/preferences\` - Get preferences
- \`PUT /api/users/me/preferences\` - Update preferences

**Bookmarks:**

- \`POST /api/bookmarks\` - Save article/story
- \`GET /api/bookmarks\` - List bookmarks
- \`DELETE /api/bookmarks/:id\` - Remove bookmark

**Saved Filters:**

- \`POST /api/saved-filters\` - Create filter
- \`GET /api/saved-filters\` - List filters
- \`PUT /api/saved-filters/:id\` - Update filter
- \`DELETE /api/saved-filters/:id\` - Delete filter

**Feeds:**

- \`GET /api/feeds/custom\` - Get personalized feed

### Analytics API

**Articles:**

- \`POST /api/articles/ingest\` - Ingest articles
- \`GET /api/articles/\` - Get articles with filtering
- \`GET /api/articles/sources/list\` - List sources
- \`POST /api/articles/sources/add\` - Add source

**Stories:**

- \`POST /api/stories/cluster\` - Trigger clustering
- \`GET /api/stories/\` - Get stories
- \`GET /api/stories/{story_id}\` - Get story details
- \`GET /api/stories/{story_id}/coverage\` - Coverage matrix

**Analytics:**

- \`GET /api/analytics/stats\` - Get statistics
- \`GET /api/analytics/filter\` - Filter articles
- \`GET /api/analytics/facets\` - Get filter options

**Fact Checker:**

- \`POST /api/fact-checker/{story_id}\` - Generate fact ledger
- \`GET /api/fact-checker/{story_id}\` - Get fact ledger

## Environment Variables

### Backend Auth (.env)

\`\`\`env
NODE_ENV=development
PORT=3000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=news_db
DB_USER=news_user
DB_PASSWORD=news_password
JWT_ACCESS_SECRET=your-secret
JWT_REFRESH_SECRET=your-refresh-secret
CORS_ORIGIN=http://localhost:3001
\`\`\`

### Backend Analytics (.env)

\`\`\`env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=news_analytics
OPENAI_API_KEY=sk-... # Optional
\`\`\`

### Frontend (.env)

\`\`\`env
VITE_API_URL=http://localhost:3000/api
VITE_ANALYTICS_API_URL=http://localhost:8000/api
\`\`\`

## Documentation

- **Deployment Guide**: \`DEPLOYMENT.md\`
- **Security**: \`docs/SECURITY.md\`
- **User Guide**: \`docs/USER_GUIDE.md\`
- **Implementation**: \`IMPLEMENTATION_SUMMARY.md\`
- **Test Coverage**: \`COMPLETE_TEST_COVERAGE.md\`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all tests pass (100% coverage required for auth)
5. Run linters and type checking
6. Submit a pull request

## License

MIT
