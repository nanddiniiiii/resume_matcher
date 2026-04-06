"""
Job Scraper API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict
from datetime import datetime

from app.database import get_db
from app.models import Job
from app.services.job_scraper import job_scraper_service
from app.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scraper", tags=["scraper"])


@router.post("/run", response_model=Dict)
def run_scraper(
    background_tasks: BackgroundTasks,
    limit_per_source: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Manually trigger job scraping from all sources
    Requires authentication
    Runs in background and returns immediately
    """
    def scrape_task():
        try:
            stats = job_scraper_service.scrape_all_sources(db, limit_per_source=limit_per_source)
            logger.info(f"Scraping completed: {stats}")
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
    
    background_tasks.add_task(scrape_task)
    
    return {
        "message": "Job scraping started in background",
        "limit_per_source": limit_per_source,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/status", response_model=Dict)
def get_scraper_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get status of job scraping:
    - Total jobs by source
    - Last scrape time
    - Active vs expired jobs
    """
    try:
        # Get total jobs by source
        jobs_by_source = db.query(
            Job.source,
            func.count(Job.id).label('count')
        ).group_by(Job.source).all()
        
        source_stats = {source: count for source, count in jobs_by_source if source}
        
        # Get last scrape time
        last_scraped = db.query(func.max(Job.scraped_at)).scalar()
        
        # Get active vs inactive count
        active_count = db.query(Job).filter(Job.is_active == True).count()
        inactive_count = db.query(Job).filter(Job.is_active == False).count()
        
        # Get jobs by type
        jobs_by_type = db.query(
            Job.job_type,
            func.count(Job.id).label('count')
        ).filter(Job.is_active == True).group_by(Job.job_type).all()
        
        type_stats = {job_type: count for job_type, count in jobs_by_type if job_type}
        
        return {
            "jobs_by_source": source_stats,
            "last_scraped_at": last_scraped.isoformat() if last_scraped else None,
            "total_jobs": active_count + inactive_count,
            "active_jobs": active_count,
            "expired_jobs": inactive_count,
            "jobs_by_type": type_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting scraper status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get scraper status")


@router.post("/mark-expired", response_model=Dict)
def mark_expired_jobs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Manually trigger marking expired jobs as inactive
    """
    try:
        expired_count = job_scraper_service.mark_expired_jobs(db)
        
        return {
            "message": f"Marked {expired_count} jobs as expired",
            "expired_count": expired_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error marking expired jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark expired jobs")


@router.get("/sources", response_model=Dict)
def get_available_sources():
    """Get list of available job scraping sources"""
    return {
        "sources": [
            {
                "name": "remoteok",
                "description": "Remote tech jobs from RemoteOK",
                "status": "active",
                "type": "web_scraping"
            },
            {
                "name": "adzuna",
                "description": "Jobs from Adzuna API",
                "status": "requires_api_key",
                "type": "api"
            }
        ],
        "total_sources": 2
    }
