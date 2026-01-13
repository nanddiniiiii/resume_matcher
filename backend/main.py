from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api import resumes, jobs, matches, auth, saved_jobs, applications, users

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="AI Job Matcher API",
    description="AI-powered job recommendation platform using semantic matching",
    version="2.0.0"
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
app.include_router(jobs.router, prefix="/api")
app.include_router(matches.router, prefix="/api")
app.include_router(saved_jobs.router)  # Already has /api/jobs prefix
app.include_router(applications.router)  # Already has /api/applications prefix
app.include_router(users.router)  # Already has /api/users prefix


@app.get("/")
def root():
    """Root endpoint - API health check."""
    return {
        "message": "AI Job Matcher API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
