from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional

from app.database import get_db
from app.models import Job
from app.services.job_matcher import JobMatcher
from app.api.schemas import JobCreate, JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])

# Initialize job matcher
job_matcher = JobMatcher()


@router.post("/", response_model=JobResponse)
def create_job(job_data: JobCreate, db: Session = Depends(get_db)):
    """
    Create a new job posting.
    """
    # Prepare job text for embedding
    job_text = job_matcher.prepare_job_text(job_data.dict())
    
    # Generate embedding
    job_embedding = job_matcher.generate_embedding(job_text)
    
    # Create job record
    job = Job(
        title=job_data.title,
        company=job_data.company,
        description=job_data.description,
        required_skills=job_data.required_skills,
        location=job_data.location,
        job_type=job_data.job_type,
        embedding=job_embedding
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return job


@router.get("/", response_model=List[JobResponse])
def list_jobs(
    skip: int = 0,
    limit: int = 100,
    job_type: str = None,
    db: Session = Depends(get_db)
):
    """List all jobs with optional filtering."""
    query = db.query(Job)
    
    if job_type:
        query = query.filter(Job.job_type == job_type)
    
    jobs = query.offset(skip).limit(limit).all()
    return jobs


@router.get("/search")
async def search_jobs(
    q: Optional[str] = Query(None, description="Search query for title/company/description"),
    skills: Optional[List[str]] = Query(None, description="Filter by required skills"),
    location: Optional[str] = Query(None, description="Filter by location"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Advanced job search with multiple filters.
    Supports text search, skills matching, location, and job type.
    """
    query = db.query(Job)
    
    # Text search in title, company, description
    if q:
        search_filter = or_(
            Job.title.ilike(f"%{q}%"),
            Job.company.ilike(f"%{q}%"),
            Job.description.ilike(f"%{q}%")
        )
        query = query.filter(search_filter)
    
    # Skills filter
    if skills:
        skill_filters = []
        for skill in skills:
            skill_filters.append(
                func.jsonb_exists(Job.skills_required, skill)
            )
        query = query.filter(or_(*skill_filters))
    
    # Location filter
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    
    # Job type filter
    if job_type:
        query = query.filter(Job.job_type == job_type)
    
    # Order by most recent
    query = query.order_by(Job.created_at.desc())
    
    # Count total
    total = query.count()
    
    # Apply pagination
    jobs = query.offset(skip).limit(limit).all()
    
    return {
        "jobs": [
            {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "salary_range": job.salary_range,
                "job_type": job.job_type,
                "skills_required": job.skills_required,
                "description": job.description[:200] + "..." if len(job.description) > 200 else job.description,
                "created_at": job.created_at.isoformat()
            }
            for job in jobs
        ],
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get job details by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, job_data: JobCreate, db: Session = Depends(get_db)):
    """Update a job posting."""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Update fields
    job.title = job_data.title
    job.company = job_data.company
    job.description = job_data.description
    job.required_skills = job_data.required_skills
    job.location = job_data.location
    job.job_type = job_data.job_type
    
    # Regenerate embedding
    job_text = job_matcher.prepare_job_text(job_data.dict())
    job.embedding = job_matcher.generate_embedding(job_text)
    
    db.commit()
    db.refresh(job)
    
    return job


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job posting."""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    
    return {"message": "Job deleted successfully"}
