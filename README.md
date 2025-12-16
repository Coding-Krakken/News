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
npm run dev
```

The backend API will be available at `http://localhost:3000`.

### 4. Set Up the Frontend

```bash
cd ../frontend
npm install
cp .env.example .env
```

Start the frontend development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3001`.

## Environment Variables

### Backend (.env)

```env
# Server Configuration
NODE_ENV=development
PORT=3000

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=news_db
DB_USER=news_user
DB_PASSWORD=news_password

# JWT Configuration
JWT_ACCESS_SECRET=your-access-token-secret-change-in-production
JWT_REFRESH_SECRET=your-refresh-token-secret-change-in-production
JWT_ACCESS_EXPIRY=15m
JWT_REFRESH_EXPIRY=7d

# Security Configuration
COOKIE_SECRET=your-cookie-secret-change-in-production

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
AUTH_RATE_LIMIT_MAX_REQUESTS=5

# CORS Configuration
CORS_ORIGIN=http://localhost:3001

# Logging
LOG_LEVEL=info
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:3000/api
```

## API Documentation

### Authentication Endpoints

#### POST /api/auth/signup
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "display_name": "John Doe" // optional
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "display_name": "John Doe",
    "avatar_url": null,
    "created_at": "2025-12-16T...",
    "updated_at": "2025-12-16T..."
  },
  "accessToken": "eyJhbGciOiJI...",
  "refreshToken": "eyJhbGciOiJI..."
}
```

#### POST /api/auth/login
Login with existing credentials.

#### POST /api/auth/logout
Logout and invalidate refresh token (requires authentication).

#### GET /api/auth/me
Get current user information (requires authentication).

#### POST /api/auth/refresh
Refresh access token using refresh token.

### User Endpoints

#### PATCH /api/users/me
Update user profile (requires authentication).

#### GET /api/users/me/preferences
Get user preferences (requires authentication).

#### PUT /api/users/me/preferences
Update user preferences (requires authentication).

### Bookmark Endpoints

#### POST /api/bookmarks
Create a bookmark (requires authentication).

#### GET /api/bookmarks
List user's bookmarks (requires authentication).

#### DELETE /api/bookmarks/:id
Delete a bookmark (requires authentication).

### Saved Filter Endpoints

#### POST /api/saved-filters
Create a saved filter (requires authentication).

#### GET /api/saved-filters
List user's saved filters (requires authentication).

#### PUT /api/saved-filters/:id
Update a saved filter (requires authentication).

#### DELETE /api/saved-filters/:id
Delete a saved filter (requires authentication).

### Feed Endpoints

#### GET /api/feeds/custom
Get personalized news feed (requires authentication).

## Testing

### Backend Tests

Run all tests with coverage:
```bash
cd backend
npm test
```

Run unit tests only:
```bash
npm run test:unit
```

Run integration tests only:
```bash
npm run test:integration
```

### Frontend Tests

Run frontend tests:
```bash
cd frontend
npm test
```

### E2E Tests

Run end-to-end tests with Playwright:
```bash
cd frontend
npm run test:e2e
```

## Security Features

### Authentication & Authorization
- JWT-based authentication with short-lived access tokens (15 minutes)
- Refresh token rotation for enhanced security
- Secure httpOnly cookies with SameSite protection
- Server-side token invalidation on logout

### Password Security
- Argon2id hashing algorithm (recommended by OWASP)
- Strong password requirements (min 8 chars, uppercase, lowercase, number)
- No password storage in logs or responses

### API Security
- Rate limiting on all endpoints (100 requests per 15 minutes)
- Stricter rate limiting on auth endpoints (5 requests per 15 minutes)
- CORS with explicit origin allowlist
- Helmet.js security headers
- Input validation with express-validator
- Protection against user enumeration

### Data Privacy
- PII redaction in logs (email, password, tokens)
- No sensitive data in error messages
- User data isolation (horizontal privilege prevention)

## Development

### Linting

Backend:
```bash
cd backend
npm run lint
npm run lint:fix
```

Frontend:
```bash
cd frontend
npm run lint
npm run lint:fix
```

### Building for Production

Backend:
```bash
cd backend
npm run build
npm start
```

Frontend:
```bash
cd frontend
npm run build
npm run preview
```

## Project Structure

```
News/
├── backend/
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