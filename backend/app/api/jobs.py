from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

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
