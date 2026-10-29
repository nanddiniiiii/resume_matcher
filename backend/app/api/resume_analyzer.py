"""
Resume Analyzer API Endpoints
Provides resume optimization suggestions for specific jobs
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict

from app.database import get_db
from app.models import Job, Resume
from app.services.resume_analyzer import resume_analyzer_service
from app.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume-analyzer", tags=["resume-analyzer"])


class ResumeAnalysisRequest(BaseModel):
    resume_id: int
    job_id: int


class ResumeAnalysisResponse(BaseModel):
    ats_score: int
    score_interpretation: str
    missing_keywords: List[str]
    weak_areas: List[Dict]
    suggestions: List[Dict]
    keyword_analysis: Dict
    skill_match_rate: float
    recommended_additions: List[str]


@router.post("/analyze", response_model=ResumeAnalysisResponse)
def analyze_resume_for_job(
    request: ResumeAnalysisRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Analyze resume against a specific job and get improvement suggestions

    Returns:
    - ATS score (0-100)
    - Missing keywords
    - Weak areas
    - Specific, actionable suggestions
    - Keyword frequency analysis
    """
    try:
        # Get resume
        resume = db.query(Resume).filter(
            Resume.id == request.resume_id,
            Resume.user_id == current_user.id
        ).first()

        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Get job
        job = db.query(Job).filter(Job.id == request.job_id).first()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Get matching skills from resume (simple extraction for demo)
        resume_skills = resume.skills or []

        # Analyze resume against job
        analysis = resume_analyzer_service.analyze_resume_for_job(
            resume_text=resume.raw_text,
            job_description=job.description,
            job_skills=job.required_skills,
            resume_skills=resume_skills
        )

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing resume: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze resume")


@router.get("/quick-tips/{job_id}")
def get_quick_tips(
    job_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get quick optimization tips for a job without full analysis
    Faster endpoint for displaying tips on job cards
    """
    try:
        # Get job
        job = db.query(Job).filter(Job.id == job_id).first()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Get user's most recent resume
        resume = db.query(Resume).filter(
            Resume.user_id == current_user.id
        ).order_by(Resume.created_at.desc()).first()

        if not resume:
            return {
                "tips": [
                    "Upload a resume to get personalized tips",
                    f"This job requires: {', '.join(job.required_skills[:5])}",
                    "Make sure to highlight relevant experience"
                ]
            }

        # Quick skill comparison
        resume_skills = resume.skills or []
        missing_skills = [skill for skill in job.required_skills if skill.lower() not in resume.raw_text.lower()]

        tips = []

        if missing_skills:
            tips.append(f"Consider adding these skills if you have them: {', '.join(missing_skills[:3])}")

        tips.append(f"Match rate: {len(set(s.lower() for s in resume_skills) & set(s.lower() for s in job.required_skills))}/{len(job.required_skills)} required skills")
        tips.append("Tailor your resume to highlight relevant experience for this position")

        return {
            "job_title": job.title,
            "tips": tips[:5],
            "missing_skills": missing_skills[:10]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting quick tips: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tips")


def _extract_skills_from_resume(resume_text: str) -> List[str]:
    """
    Extract skills from resume text
    (Simple version - in production you'd use more sophisticated NLP)
    """
    common_skills = [
        'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Ruby', 'Go', 'Rust', 'PHP', 'Swift',
        'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring', 'Express',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'CI/CD',
        'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
        'Machine Learning', 'AI', 'Data Science', 'NLP', 'Computer Vision',
        'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum', 'TensorFlow',
        'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn', 'FastAPI', 'Next.js',
        'TypeScript', 'HTML', 'CSS', 'Tailwind', 'Bootstrap', 'Material-UI'
    ]

    resume_lower = resume_text.lower()
    found_skills = []

    for skill in common_skills:
        if skill.lower() in resume_lower:
            found_skills.append(skill)

    return found_skills
