from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import init_db, close_db
from .routes import articles, stories, analytics, fact_checker, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()

app = FastAPI(
    title="News Analytics Platform",
    description="A platform for ingesting, clustering, and analyzing news from multiple sources",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
app.include_router(stories.router, prefix="/api/stories", tags=["stories"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(fact_checker.router, prefix="/api/fact-checker", tags=["fact-checker"])

@app.get("/")
async def root():
    return {"message": "News Analytics Platform API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
