"""
API endpoints for job application tracking.
Track the status of job applications (applied, interviewing, rejected, accepted).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.job_application import JobApplication
from app.models.job import Job
from app.models.resume import Resume

router = APIRouter(prefix="/api/applications", tags=["applications"])


class ApplicationCreate(BaseModel):
    job_id: int
    resume_id: Optional[int] = None
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: str  # applied, interviewing, rejected, accepted
    notes: Optional[str] = None


@router.post("/")
async def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Track a new job application."""
    # Verify job exists
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Verify resume if provided
    if application.resume_id:
        resume = db.query(Resume).filter(
            Resume.id == application.resume_id,
            Resume.user_id == current_user.id
        ).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
    
    # Check if already applied
    existing = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.job_id == application.job_id
    ).first()
    
    if existing:
        return {
            "message": "Application already tracked",
            "application_id": existing.id,
            "status": existing.status
        }
    
    # Create application
    new_app = JobApplication(
        user_id=current_user.id,
        job_id=application.job_id,
        resume_id=application.resume_id,
        status="applied",
        notes=application.notes
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    
    return {
        "message": "Application tracked successfully",
        "application_id": new_app.id,
        "status": new_app.status
    }


@router.put("/{application_id}")
async def update_application(
    application_id: int,
    update: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update application status (e.g., interviewing, rejected, accepted)."""
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Validate status
    valid_statuses = ["applied", "interviewing", "rejected", "accepted"]
    if update.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    application.status = update.status
    if update.notes is not None:
        application.notes = update.notes
    
    db.commit()
    db.refresh(application)
    
    return {
        "message": "Application updated successfully",
        "application_id": application.id,
        "status": application.status
    }


@router.get("/")
async def get_applications(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all job applications for the current user, optionally filtered by status."""
    query = db.query(JobApplication, Job).join(
        Job, JobApplication.job_id == Job.id
    ).filter(
        JobApplication.user_id == current_user.id
    )
    
    if status:
        query = query.filter(JobApplication.status == status)
    
    applications = query.order_by(
        JobApplication.applied_date.desc()
    ).offset(skip).limit(limit).all()
    
    total_query = db.query(JobApplication).filter(JobApplication.user_id == current_user.id)
    if status:
        total_query = total_query.filter(JobApplication.status == status)
    total = total_query.count()
    
    result = []
    for app, job in applications:
        result.append({
            "application_id": app.id,
            "status": app.status,
            "applied_date": app.applied_date.isoformat(),
            "notes": app.notes,
            "job": {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "job_type": job.job_type
            }
        })
    
    return {
        "applications": result,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }


@router.delete("/{application_id}")
async def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an application record."""
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    db.delete(application)
    db.commit()
    
    return {"message": "Application deleted successfully"}
