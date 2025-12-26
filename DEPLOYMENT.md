# Deployment Guide

This guide covers deploying the News Analytics Platform in two environments:

1. **Local Development** using Docker Compose
2. **Production Deployment** using Vercel (frontend) + Railway/Render (backend)

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Local Development (Docker Compose)](#local-development-docker-compose)
- [Production Deployment](#production-deployment)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [Troubleshooting](#troubleshooting)

---

## Architecture Overview

The News Analytics Platform consists of:

- **Frontend**: Vite + React SPA (static site, deployable to Vercel)
- **Backend**: FastAPI + Python (requires a server, deploy to Railway/Render/Fly.io)
- **Database**: MongoDB (use Atlas for production)

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   LOCAL (Docker Compose)                 │
├─────────────────────────────────────────────────────────┤
│  Frontend (Vite)  →  Backend (FastAPI)  →  MongoDB     │
│  localhost:3000       localhost:8000        localhost   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  PRODUCTION (Cloud)                      │
├─────────────────────────────────────────────────────────┤
│  Frontend (Vercel) → Backend (Railway) → MongoDB Atlas │
│  your-app.vercel.app  your-api.railway.app              │
└─────────────────────────────────────────────────────────┘
```

---

## Local Development (Docker Compose)

### Prerequisites

- Docker and Docker Compose installed
- Git

### Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/Coding-Krakken/News.git
   cd News
   ```

2. **Configure environment variables**

   ```bash
   cp backend/.env.example backend/.env
   ```

   Edit `backend/.env` and set your OpenAI API key (optional):

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Start all services**

   ```bash
   docker compose up
   ```

   This starts:
   - MongoDB on `localhost:27017`
   - Backend API on `localhost:8000`
   - Frontend on `localhost:3000`

4. **Access the application**
   - **Frontend**: http://localhost:3000
   - **API Docs**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

### Local Development without Docker

If you prefer to run services individually:

1. **Start MongoDB**

   ```bash
   # Option 1: Using Docker
   docker run -d -p 27017:27017 --name mongodb mongo:7

   # Option 2: Using local MongoDB installation
   mongod
   ```

2. **Start Backend**

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your settings
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Start Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Running Tests Locally

```bash
# Backend tests
cd backend
./run_tests.sh

# Frontend tests
cd frontend
./run_tests.sh

# Or use npm scripts from root
npm run test:backend
npm run test:frontend
```

---

## Production Deployment

### Overview

For production, we recommend:

- **Frontend**: Deploy to **Vercel** (static hosting, free tier available)
- **Backend**: Deploy to **Railway**, **Render**, or **Fly.io** (Python support)
- **Database**: **MongoDB Atlas** (managed MongoDB, free tier available)

### Step 1: Set Up MongoDB Atlas

1. **Create a MongoDB Atlas account**
   - Go to https://www.mongodb.com/cloud/atlas
   - Create a free cluster

2. **Get connection string**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string (looks like `mongodb+srv://...`)

3. **Configure network access**
   - Add `0.0.0.0/0` to IP whitelist (or specific IPs)
   - Create database user with password

### Step 2: Deploy Backend

#### Option A: Railway (Recommended)

1. **Create Railway account**: https://railway.app

2. **Deploy from GitHub**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your News repository
   - Railway will auto-detect the backend

3. **Configure environment variables**
   Go to your service settings and add:

   ```env
   ENVIRONMENT=production
   MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/news_analytics
   DATABASE_NAME=news_analytics
   SECRET_KEY=<generate with: openssl rand -hex 32>
   OPENAI_API_KEY=sk-your-production-key
   API_BASE_URL=https://your-backend.railway.app
   FRONTEND_URL=https://your-app.vercel.app
   CORS_ORIGINS=https://your-app.vercel.app,https://*.vercel.app
   ```

4. **Set build/start commands** (if needed)
   - Build: `cd backend && pip install -r requirements.txt`
   - Start: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Note your backend URL**: `https://your-backend.railway.app`

#### Option B: Render

1. **Create Render account**: https://render.com

2. **Create new Web Service**
   - Connect your GitHub repository
   - Select "Python" environment

3. **Configure build settings**
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add environment variables** (same as Railway above)

#### Option C: Fly.io

1. **Install Fly CLI**: https://fly.io/docs/hands-on/install-flyctl/

2. **Create Dockerfile** (if needed, or use existing)

3. **Deploy**
   ```bash
   cd backend
   fly launch
   fly secrets set MONGODB_URL=...
   fly secrets set SECRET_KEY=...
   # ... other secrets
   fly deploy
   ```

### Step 3: Deploy Frontend to Vercel

1. **Create Vercel account**: https://vercel.com

2. **Import project**
   - Click "Add New..." → "Project"
   - Import from GitHub
   - Select your News repository

3. **Configure build settings**
   Vercel should auto-detect these from `vercel.json`:
   - Framework Preset: Other
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/dist`
   - Install Command: `cd frontend && npm install`

4. **Set environment variables**
   In Vercel dashboard → Project Settings → Environment Variables:

   **Production:**

   ```env
   VITE_API_BASE_URL=https://your-backend.railway.app/api
   VITE_ENVIRONMENT=production
   ```

   **Preview (optional):**

   ```env
   VITE_API_BASE_URL=https://your-staging-backend.railway.app/api
   VITE_ENVIRONMENT=staging
   ```

5. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy your frontend
   - Note your deployment URL: `https://your-app.vercel.app`

6. **Update backend CORS**
   Go back to your backend deployment (Railway/Render) and update:
   ```env
   FRONTEND_URL=https://your-app.vercel.app
   CORS_ORIGINS=https://your-app.vercel.app,https://*.vercel.app
   ```

### Step 4: Verify Deployment

1. **Test frontend**: Visit `https://your-app.vercel.app`
2. **Test backend**: Visit `https://your-backend.railway.app/health`
3. **Test integration**: Try ingesting articles and clustering stories

---

## Environment Variables

### Backend Environment Variables

#### Required

| Variable        | Description               | Local Example               | Production Example                            |
| --------------- | ------------------------- | --------------------------- | --------------------------------------------- |
| `MONGODB_URL`   | MongoDB connection string | `mongodb://localhost:27017` | `mongodb+srv://user:pass@cluster.mongodb.net` |
| `DATABASE_NAME` | MongoDB database name     | `news_analytics`            | `news_analytics`                              |

#### Required for Production

| Variable       | Description          | Production Example                                 |
| -------------- | -------------------- | -------------------------------------------------- |
| `SECRET_KEY`   | JWT signing key      | Generate: `openssl rand -hex 32`                   |
| `API_BASE_URL` | Backend API URL      | `https://your-backend.railway.app`                 |
| `FRONTEND_URL` | Frontend URL         | `https://your-app.vercel.app`                      |
| `CORS_ORIGINS` | Allowed CORS origins | `https://your-app.vercel.app,https://*.vercel.app` |

#### Optional

| Variable                | Description                    | Default              |
| ----------------------- | ------------------------------ | -------------------- |
| `OPENAI_API_KEY`        | OpenAI API key for AI features | None (uses fallback) |
| `ENVIRONMENT`           | Deployment environment         | `local`              |
| `RATE_LIMIT_ENABLED`    | Enable rate limiting           | `true`               |
| `RATE_LIMIT_PER_MINUTE` | Requests per minute            | `60`                 |
| `LOG_LEVEL`             | Logging level                  | `INFO`               |

### Frontend Environment Variables

| Variable            | Description      | Local            | Production                             |
| ------------------- | ---------------- | ---------------- | -------------------------------------- |
| `VITE_API_BASE_URL` | Backend API URL  | `/api` (proxied) | `https://your-backend.railway.app/api` |
| `VITE_ENVIRONMENT`  | Environment name | `local`          | `production`                           |

---

## Database Migrations

### MongoDB Schema

MongoDB is schemaless, but we create indexes on startup for performance.

### Initial Setup

On first run, the backend will automatically:

1. Connect to MongoDB
2. Create indexes on collections (articles, stories, users, sources, audit_log)
3. Initialize empty collections

### Seeding Data (Optional)

To seed initial data:

```bash
cd backend
source venv/bin/activate
python -c "
from app.database import init_db
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def seed():
    await init_db()
    # Add seed logic here
    print('Database seeded')

asyncio.run(seed())
"
```

### Backup and Restore

**Backup** (using mongodump):

```bash
mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net" --db=news_analytics --out=backup/
```

**Restore** (using mongorestore):

```bash
mongorestore --uri="mongodb+srv://user:pass@cluster.mongodb.net" --db=news_analytics backup/news_analytics/
```

---

## Troubleshooting

### Local Development Issues

#### Problem: Docker containers won't start

**Solution:**

```bash
# Stop all containers
docker compose down

# Remove volumes (careful: this deletes data)
docker compose down -v

# Rebuild and start
docker compose up --build
```

#### Problem: Port already in use

**Solution:**

```bash
# Find process using port 8000 or 3000
lsof -i :8000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or change ports in docker-compose.yml
```

#### Problem: Frontend can't connect to backend

**Solution:**

1. Check backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in backend
3. Check proxy settings in `frontend/vite.config.js`

### Production Issues

#### Problem: Vercel build fails

**Solution:**

1. Check build logs in Vercel dashboard
2. Verify environment variables are set
3. Test build locally: `cd frontend && npm run build`
4. Check `vercel.json` configuration

#### Problem: Backend returns 500 errors

**Solution:**

1. Check backend logs in Railway/Render dashboard
2. Verify MongoDB connection string
3. Check all required environment variables are set
4. Test configuration validation: backend will log missing config

#### Problem: CORS errors in browser

**Solution:**

1. Verify `CORS_ORIGINS` in backend includes your frontend URL
2. Check frontend URL matches exactly (no trailing slash)
3. Verify backend accepts wildcard for preview deployments: `https://*.vercel.app`

#### Problem: OpenAI API errors

**Solution:**

1. Check API key is valid
2. Check API key has credits
3. App will fallback to rule-based extraction if API fails

#### Problem: MongoDB connection timeout

**Solution:**

1. Check MongoDB Atlas IP whitelist includes `0.0.0.0/0`
2. Verify connection string is correct
3. Check database user has correct permissions
4. Test connection locally: `mongosh "mongodb+srv://..."`

### Performance Issues

#### Problem: Slow article ingestion

**Solution:**

1. Check network latency to news sources
2. Consider adding more workers (if implementing background jobs)
3. Implement caching for frequently accessed data

#### Problem: Slow story clustering

**Solution:**

1. Clustering is CPU-intensive; ensure backend has adequate resources
2. Consider implementing background job queue (Bull/BullMQ with Redis)
3. Add progress indicators in UI

---

## Additional Resources

### Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vite Documentation](https://vitejs.dev/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app/)

### Support

- Open an issue on GitHub: https://github.com/Coding-Krakken/News/issues
- Check existing documentation in repository

### Monitoring and Observability

- Add logging: Backend uses Python logging (configurable via `LOG_LEVEL`)
- Add error tracking: Consider integrating Sentry or similar
- Add analytics: Consider integrating Plausible or Google Analytics

---

## Security Best Practices

1. **Never commit secrets**: Always use environment variables
2. **Use strong SECRET_KEY**: Generate with `openssl rand -hex 32`
3. **Limit CORS**: Only allow necessary origins
4. **Use HTTPS**: Always use HTTPS in production
5. **Rate limiting**: Keep rate limiting enabled
6. **MongoDB security**: Use strong passwords, limit IP access
7. **Update dependencies**: Regularly update packages for security patches
8. **Review logs**: Monitor logs for suspicious activity

---

## Future Enhancements

### Background Jobs

Currently, all processing is synchronous. For better performance:

1. Add Redis for job queue
2. Use Celery or BullMQ for background jobs
3. Move ingestion and clustering to background workers
4. Deploy workers separately (Railway/Render support workers)

### File Storage

If adding file uploads in the future:

1. Use S3-compatible storage (AWS S3, Cloudflare R2, Vercel Blob)
2. Never store files on local filesystem in production
3. Abstract storage layer with environment-based provider selection

### WebSockets / Real-time Features

Currently not used. If needed:

1. Vercel supports serverless WebSockets (beta)
2. Or use separate WebSocket server (Railway/Render)
3. Consider Server-Sent Events (SSE) as simpler alternative

---

## Cost Estimates

### Free Tier (Good for testing)

- **MongoDB Atlas**: Free tier (512MB storage)
- **Vercel**: Free tier (100GB bandwidth/month)
- **Railway**: $5/month credit (enough for small app)
- **Total**: ~$0-5/month

### Production Scale (Medium traffic)

- **MongoDB Atlas**: M10 tier (~$50/month)
- **Vercel**: Pro tier (~$20/month)
- **Railway**: ~$20/month (backend + workers)
- **OpenAI**: Pay-as-you-go (~$10-50/month depending on usage)
- **Total**: ~$100-150/month

---

## License

ISC

---

**Questions?** Open an issue on GitHub or check the main [README.md](README.md) for more information.
