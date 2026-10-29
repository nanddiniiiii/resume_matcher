from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api import resumes, jobs, matches, auth, saved_jobs, applications, users, scraper, resume_analyzer

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()

# Initialize FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title="AI Job Matcher API",
    description="AI-powered job recommendation platform using semantic matching with real-time job scraping",
    version="2.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(resumes.router, prefix="/api")

app.include_router(matches.router, prefix="/api")
app.include_router(saved_jobs.router)
app.include_router(jobs.router, prefix="/api")
app.include_router(applications.router)  # Already has /api/applications prefix
app.include_router(users.router)  # Already has /api/users prefix
app.include_router(scraper.router, prefix="/api")  # Job scraper endpoints
app.include_router(resume_analyzer.router, prefix="/api")  # Resume analyzer endpoints


@app.get("/")
def root():
    """Root endpoint - API health check."""
    return {
        "message": "AI Job Matcher API",
        "status": "running",
        "version": "2.1.0",
        "features": ["semantic_matching", "job_scraping", "resume_analysis"]
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(503, "Database unavailable") from exc
    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
