from fastapi import APIRouter, Depends, HTTPException, Query
from app.auth import get_current_user
from app.models import User
from app.api.resumes import owned_resume
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Job, JobMatch
from app.services.job_matcher import JobMatcher
from app.api.schemas import JobMatchListResponse, JobMatchResponse, JobMatchExplanation

router = APIRouter(prefix="/matches", tags=["matches"])

# Initialize job matcher
job_matcher = JobMatcher()


@router.get("/{resume_id}", response_model=JobMatchListResponse)
def get_job_matches(
    resume_id: int,
    top_n: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get top job matches for a resume.
    This is the core feature - semantic job matching with explanations.
    """
    # Get resume
    resume = owned_resume(resume_id, db, current_user)

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if not resume.embedding:
        raise HTTPException(
            status_code=400,
            detail="Resume embedding not found. Please re-upload the resume."
        )

    # Get all jobs
    jobs = db.query(Job).filter(Job.is_active.is_(True)).all()

    if not jobs:
        return JobMatchListResponse(total_matches=0, matches=[])

    # Prepare job data for matching
    jobs_data = []
    for job in jobs:
        if job.embedding:  # Only include jobs with embeddings
            jobs_data.append({
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'description': job.description,
                'required_skills': job.required_skills,
                'location': job.location,
                'job_type': job.job_type,
                'embedding': job.embedding,
                'created_at': job.created_at,
                'source': job.source, 'source_url': job.source_url,
                'scraped_at': job.scraped_at, 'expires_at': job.expires_at, 'is_active': job.is_active
            })

    # Perform matching
    matches = job_matcher.rank_jobs(
        resume_embedding=resume.embedding,
        resume_skills=resume.skills or [],
        jobs=jobs_data,
        top_n=top_n
    )

    # Save matches to database
    for match in matches:
        job_match = JobMatch(
            resume_id=resume.id,
            job_id=match['job']['id'],
            similarity_score=match['similarity_score'],
            matching_skills=match['matching_skills'],
            missing_skills=match['missing_skills'],
            explanation=match['explanation']
        )

        # Check if match already exists
        existing = db.query(JobMatch).filter(
            JobMatch.resume_id == resume.id,
            JobMatch.job_id == match['job']['id']
        ).first()

        if existing:
            # Update existing match
            existing.similarity_score = match['similarity_score']
            existing.matching_skills = match['matching_skills']
            existing.missing_skills = match['missing_skills']
            existing.explanation = match['explanation']
        else:
            # Create new match
            db.add(job_match)

    db.commit()

    # Format response
    match_responses = []
    for match in matches:
        job_data = match['job']

        match_responses.append(JobMatchResponse(
            job={
                'id': job_data['id'],
                'title': job_data['title'],
                'company': job_data['company'],
                'description': job_data['description'],
                'required_skills': job_data['required_skills'],
                'location': job_data['location'],
                'job_type': job_data['job_type'],
                'created_at': job_data['created_at'],
                **{key: job_data[key] for key in ('source', 'source_url', 'scraped_at', 'expires_at', 'is_active')}
            },
            similarity_score=match['similarity_score'],
            matching_skills=match['matching_skills'],
            missing_skills=match['missing_skills'],
            explanation=JobMatchExplanation(**match['explanation'])
        ))

    return JobMatchListResponse(
        total_matches=len(match_responses),
        matches=match_responses
    )


@router.get("/history/{resume_id}")
def get_match_history(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get previously saved match history for a resume."""
    resume = owned_resume(resume_id, db, current_user)

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    matches = db.query(JobMatch).filter(JobMatch.resume_id == resume_id).all()

    return {
        "total_matches": len(matches),
        "matches": matches
    }
