"""
Extended user statistics and profile endpoints.
Provides detailed user activity metrics and profile management.
"""
from fastapi import Query, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.models.job_match import JobMatch
from app.models.saved_job import SavedJob
from app.models.job_application import JobApplication

router = APIRouter(prefix="/api/users", tags=["users"])


class UserStatsResponse(BaseModel):
    total_resumes: int
    total_matches: int
    total_saved_jobs: int
    total_applications: int
    application_breakdown: dict  # Count by status
    recent_activity: dict


@router.get("/stats")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive user statistics."""
    # Count resumes
    total_resumes = db.query(Resume).filter(Resume.user_id == current_user.id).count()

    # Count matches across all resumes
    total_matches = db.query(JobMatch).join(Resume).filter(
        Resume.user_id == current_user.id
    ).count()

    # Count saved jobs
    total_saved_jobs = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id
    ).count()

    # Count applications
    total_applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    ).count()

    # Application breakdown by status
    app_breakdown = db.query(
        JobApplication.status,
        func.count(JobApplication.id)
    ).filter(
        JobApplication.user_id == current_user.id
    ).group_by(JobApplication.status).all()

    application_breakdown = {status: count for status, count in app_breakdown}

    # Recent activity
    recent_resume = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).order_by(Resume.created_at.desc()).first()

    recent_application = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    ).order_by(JobApplication.applied_date.desc()).first()

    return {
        "total_resumes": total_resumes,
        "total_matches": total_matches,
        "total_saved_jobs": total_saved_jobs,
        "total_applications": total_applications,
        "application_breakdown": application_breakdown,
        "recent_activity": {
            "last_resume_upload": recent_resume.created_at.isoformat() if recent_resume else None,
            "last_application": recent_application.applied_date.isoformat() if recent_application else None
        }
    }


@router.get("/resumes")
def get_user_resumes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's resume history with pagination."""
    resumes = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).order_by(
        Resume.created_at.desc()
    ).offset(skip).limit(limit).all()

    total = db.query(Resume).filter(Resume.user_id == current_user.id).count()

    result = []
    for resume in resumes:
        # Count matches for this resume
        match_count = db.query(JobMatch).filter(JobMatch.resume_id == resume.id).count()

        result.append({
            "id": resume.id,
            "filename": resume.filename,
            "uploaded_at": resume.created_at.isoformat(),
            "skills": resume.skills,
            "match_count": match_count
        })

    return {
        "resumes": result,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }


@router.get("/matches/{resume_id}")
def get_resume_matches(
    resume_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    min_score: float = 0.0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get job matches for a specific resume with pagination and filtering."""
    # Verify resume belongs to user
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Get matches with score filter
    matches = db.query(JobMatch).filter(
        JobMatch.resume_id == resume_id,
        JobMatch.similarity_score >= min_score
    ).order_by(
        JobMatch.similarity_score.desc()
    ).offset(skip).limit(limit).all()

    total = db.query(JobMatch).filter(
        JobMatch.resume_id == resume_id,
        JobMatch.similarity_score >= min_score
    ).count()

    return {
        "matches": [
            {
                "id": match.id,
                "job_id": match.job_id,
                "match_score": round(match.similarity_score, 2),
                "explanation": match.explanation,
                "created_at": match.created_at.isoformat()
            }
            for match in matches
        ],
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }
