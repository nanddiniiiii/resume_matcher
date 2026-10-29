"""
Job Scraper API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict
from datetime import datetime, timezone

from app.database import get_db, SessionLocal
from app.models import Job
from app.services.job_scraper import job_scraper_service
from app.auth import get_admin_user
import logging
from threading import Lock

_run_lock = Lock()
_run_status = {"running": False, "last_result": None, "last_error": None}

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scraper", tags=["scraper"])


@router.post("/run", response_model=Dict)
def run_scraper(
    background_tasks: BackgroundTasks,
    limit_per_source: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """
    Manually trigger job scraping from all sources
    Requires authentication
    Runs in background and returns immediately
    """
    if not _run_lock.acquire(blocking=False):
        raise HTTPException(409, "A scraper run is already in progress")
    _run_status.update(running=True, last_result=None, last_error=None)

    def scrape_task():
        try:
            with SessionLocal() as task_db:
                stats = job_scraper_service.scrape_all_sources(task_db, limit_per_source=limit_per_source)
            _run_status["last_result"] = stats
        except Exception:
            logger.exception("Scraping failed")
            _run_status["last_error"] = "Scraping failed; check backend logs"
        finally:
            _run_status["running"] = False
            _run_lock.release()

    background_tasks.add_task(scrape_task)

    return {
        "message": "Job scraping started in background",
        "limit_per_source": limit_per_source,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/status", response_model=Dict)
def get_scraper_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
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
            "sources_available": list(job_scraper_service.sources),
            "run": dict(_run_status),
            "last_scraped_at": last_scraped.isoformat() if last_scraped else None,
            "total_jobs": active_count + inactive_count,
            "active_jobs": active_count,
            "expired_jobs": inactive_count,
            "jobs_by_type": type_stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting scraper status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get scraper status")


@router.post("/mark-expired", response_model=Dict)
def mark_expired_jobs(
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """
    Manually trigger marking expired jobs as inactive
    """
    try:
        expired_count = job_scraper_service.mark_expired_jobs(db)

        return {
            "message": f"Marked {expired_count} jobs as expired",
            "expired_count": expired_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
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
                "status": "not_implemented",
                "type": "api"
            }
        ],
        "total_sources": 2
    }
