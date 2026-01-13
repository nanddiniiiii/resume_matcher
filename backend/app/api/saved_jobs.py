"""
API endpoints for saved jobs functionality.
Users can save/bookmark jobs for later review.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.saved_job import SavedJob
from app.models.job import Job

router = APIRouter(prefix="/api/jobs", tags=["saved-jobs"])


@router.post("/{job_id}/save")
async def save_job(
    job_id: int,
    notes: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save/bookmark a job for later review."""
    # Check if job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if already saved
    existing = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        SavedJob.job_id == job_id
    ).first()
    
    if existing:
        # Update notes if provided
        if notes is not None:
            existing.notes = notes
            db.commit()
            return {"message": "Job already saved, notes updated", "saved_job_id": existing.id}
        return {"message": "Job already saved", "saved_job_id": existing.id}
    
    # Create new saved job
    saved_job = SavedJob(
        user_id=current_user.id,
        job_id=job_id,
        notes=notes
    )
    db.add(saved_job)
    db.commit()
    db.refresh(saved_job)
    
    return {
        "message": "Job saved successfully",
        "saved_job_id": saved_job.id
    }


@router.delete("/{job_id}/save")
async def unsave_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a job from saved jobs."""
    saved_job = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        SavedJob.job_id == job_id
    ).first()
    
    if not saved_job:
        raise HTTPException(status_code=404, detail="Saved job not found")
    
    db.delete(saved_job)
    db.commit()
    
    return {"message": "Job removed from saved jobs"}


@router.get("/saved")
async def get_saved_jobs(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all saved jobs for the current user."""
    saved_jobs = db.query(SavedJob, Job).join(
        Job, SavedJob.job_id == Job.id
    ).filter(
        SavedJob.user_id == current_user.id
    ).order_by(
        SavedJob.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    total = db.query(SavedJob).filter(SavedJob.user_id == current_user.id).count()
    
    result = []
    for saved_job, job in saved_jobs:
        result.append({
            "saved_job_id": saved_job.id,
            "saved_at": saved_job.created_at.isoformat(),
            "notes": saved_job.notes,
            "job": {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "salary_range": job.salary_range,
                "job_type": job.job_type,
                "description": job.description[:200] + "..." if len(job.description) > 200 else job.description,
                "skills_required": job.skills_required
            }
        })
    
    return {
        "saved_jobs": result,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }
