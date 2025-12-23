# Quick Start Guide

## Option 1: Docker (Recommended for Quick Setup)

1. Make sure Docker and Docker Compose are installed
2. Create environment file:
```bash
cp backend/.env.example backend/.env
# Optionally edit backend/.env to add your OpenAI API key
```

3. Start all services:
```bash
docker compose up
```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Option 2: Manual Setup

### Prerequisites
- Python 3.12+
- Node.js 20+
- MongoDB running on localhost:27017

### Quick Setup Script
```bash
./setup.sh
```

Then in two separate terminals:

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Production Deployment

For production deployment to Vercel, Railway, or other cloud platforms, see:
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete production deployment guide

## First Steps

1. **Ingest Articles**: Click "Ingest Articles" button to fetch news from configured sources
2. **Cluster Stories**: Click "Cluster Stories" to group related articles
3. **Explore**: Browse stories and click on any story for details
4. **Generate Facts**: Click "Generate Fact Ledger" to see AI-powered fact analysis
5. **View Analytics**: Navigate to Analytics page for coverage statistics

## Configuration

### Add Your OpenAI API Key (Optional)
Edit `backend/.env`:
```
OPENAI_API_KEY=sk-...your-key-here...
```

Note: The platform works without OpenAI, but uses a simpler fact extraction method.

### Environment Variables
See `backend/.env.example` for all available configuration options including:
- Database connection
- CORS settings
- Rate limiting
- Logging level

### Add More News Sources
Use the API or edit `backend/app/services/ingestion.py` to add more RSS feeds.

## Troubleshooting

**MongoDB Connection Error:**
- Make sure MongoDB is running
- Check connection string in `backend/.env`

**Frontend Can't Connect to Backend:**
- Make sure backend is running on port 8000
- Check browser console for CORS errors

**No Articles Appearing:**
- Click "Ingest Articles" first
- Check backend logs for RSS feed errors
- Some RSS feeds may be blocked or require authentication

**Configuration Validation Errors:**
- Check that all required environment variables are set
- See the helpful error messages printed on startup
- Refer to `.env.example` for correct format

## Need Help?
- See the full [README.md](README.md) for detailed documentation
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Check backend/frontend test documentation for development
