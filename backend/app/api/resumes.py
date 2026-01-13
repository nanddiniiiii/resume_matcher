from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime

from app.database import get_db
from app.models import Resume, User
from app.services.resume_parser import ResumeParser
from app.services.job_matcher import JobMatcher
from app.api.schemas import ResumeUploadResponse, ResumeResponse
from app.config import settings

router = APIRouter(prefix="/resumes", tags=["resumes"])

# Initialize services
resume_parser = ResumeParser()
job_matcher = JobMatcher()


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user_email: str = "demo@example.com",  # Simplified for now
    db: Session = Depends(get_db)
):
    """
    Upload and parse a resume PDF file.
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
        )
    
    # Get or create user
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        user = User(email=user_email, name="Demo User")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save file with timestamp to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse resume
        parsed_data = resume_parser.parse_resume(file_path)
        
        # Generate embedding for resume
        resume_text = job_matcher.prepare_resume_text(parsed_data)
        resume_embedding = job_matcher.generate_embedding(resume_text)
        
        # Create resume record
        resume = Resume(
            user_id=user.id,
            filename=file.filename,
            file_path=file_path,
            raw_text=parsed_data['raw_text'],
            skills=parsed_data['skills'],
            education=parsed_data['education'],
            experience=parsed_data['experience'],
            embedding=resume_embedding
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        return ResumeUploadResponse(
            id=resume.id,
            filename=resume.filename,
            message="Resume uploaded and parsed successfully",
            skills_found=parsed_data['skills'],
            education_found=len(parsed_data['education']),
            experience_found=len(parsed_data['experience'])
        )
    
    except Exception as e:
        # Clean up file if processing failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """Get resume details by ID."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return resume


@router.get("/", response_model=List[ResumeResponse])
def list_resumes(
    user_email: str = "demo@example.com",
    db: Session = Depends(get_db)
):
    """List all resumes for a user."""
    user = db.query(User).filter(User.email == user_email).first()
    
    if not user:
        return []
    
    resumes = db.query(Resume).filter(Resume.user_id == user.id).all()
    return resumes


@router.delete("/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    """Delete a resume."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete file
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    
    # Delete database record
    db.delete(resume)
    db.commit()
    
    return {"message": "Resume deleted successfully"}
