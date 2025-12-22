# News Analytics Platform

A comprehensive news analytics platform that ingests articles from multiple sources, clusters them into story events, computes coverage statistics, and provides AI-powered fact-checking capabilities.

## 🚀 Quick Start

### Local Development (Docker Compose)
```bash
git clone https://github.com/Coding-Krakken/News.git
cd News
cp backend/.env.example backend/.env
# Edit backend/.env with your OpenAI API key (optional)
docker compose up
```

Visit http://localhost:3000 to use the app!

### Production Deployment
See **[DEPLOYMENT.md](DEPLOYMENT.md)** for complete deployment guide including:
- Vercel deployment (frontend)
- Railway/Render deployment (backend)
- MongoDB Atlas setup
- Environment configuration
- Troubleshooting

## Features

### Core Functionality
- **Multi-Source News Ingestion**: Automatically ingest articles from RSS feeds and APIs
- **Story Clustering**: Use NLP and machine learning to group related articles into story events
- **Coverage Analytics**: Track and visualize coverage statistics by:
  - Source
  - Category
  - Geography
  - Time
  - Ideology
- **Faceted Filtering UI**: Filter and explore stories with interactive controls
- **Coverage Matrix**: See which sources covered each story and which didn't
- **AI Fact-Only Analysis**: Extract claims, cross-corroborate them, and separate confirmed from disputed facts

### AI-Powered Fact Checking
The platform includes an innovative "Fact-Only" feature that:
1. Reads all articles in a story across all sources
2. Extracts factual claims with attribution
3. Cross-corroborates claims across sources
4. Separates confirmed from disputed claims
5. Outputs a cited fact ledger showing:
   - ✓ Confirmed claims (corroborated by multiple sources)
   - ✗ Disputed claims (conflicting information)
   - ? Uncorroborated claims (single source only)

## Architecture

### Backend (Python/FastAPI)
- **Framework**: FastAPI for high-performance async API
- **Database**: MongoDB for flexible document storage
- **NLP**: Sentence Transformers for article embeddings
- **Clustering**: DBSCAN algorithm for story grouping
- **AI**: OpenAI GPT for claim extraction and analysis

### Frontend (React)
- **Framework**: React 18 with Vite for fast development
- **Styling**: Custom CSS with responsive design
- **API Client**: Axios for HTTP requests
- **State Management**: React hooks

## Installation

### Prerequisites
- Python 3.12+
- Node.js 20+
- MongoDB (local or remote)
- OpenAI API key (optional, for AI fact-checking)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp .env.example .env
```

5. Edit `.env` and configure:
```
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=news_analytics
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

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

## Project Structure

```
News/
├── backend/
│   ├── app/
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── models/          # Data models
│   │   ├── database.py      # Database connection
│   │   └── main.py          # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── .env.example        # Environment template
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API client
│   │   ├── App.jsx         # Main app component
│   │   └── main.jsx        # Entry point
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
└── README.md               # This file
```

## Features in Detail

### Story Clustering Algorithm
1. **Embedding Generation**: Uses Sentence Transformers to create semantic embeddings of article titles and content
2. **Similarity Calculation**: Computes cosine similarity between article embeddings
3. **DBSCAN Clustering**: Groups similar articles using density-based clustering
4. **Story Creation**: Generates story metadata including title, summary, and coverage matrix

### Coverage Analytics
The platform tracks coverage across multiple dimensions:
- **By Source**: Which outlets are publishing most actively
- **By Category**: Distribution across news categories
- **By Geography**: Regional focus of coverage
- **By Ideology**: Perspective distribution (left, center, right)
- **By Time**: Temporal patterns in coverage

### Fact-Only Analysis Workflow
1. **Claim Extraction**: AI analyzes each article to extract factual assertions
2. **Attribution Tracking**: Each claim is linked to its source
3. **Cross-Corroboration**: Claims are compared across all sources
4. **Similarity Grouping**: Similar claims from different sources are grouped
5. **Verification Status**: Claims are marked as confirmed (multiple sources), disputed (conflicting), or uncorroborated (single source)
6. **Ledger Generation**: Final output shows all claims with their verification status and citations

## Security Notes

- Never commit the `.env` file with actual API keys
- Use environment variables for all sensitive configuration
- The `.gitignore` is configured to exclude sensitive files

## Contributing

This is a demonstration project showcasing news analytics and AI-powered fact-checking capabilities.

## License

ISC

## Support

For issues or questions, please open an issue in the GitHub repository.