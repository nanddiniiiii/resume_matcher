"""Authenticated resume upload and management."""
import logging
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Resume, User, JobApplication
from app.auth import get_current_user
from app.services.resume_parser import ResumeParser
from app.services.job_matcher import JobMatcher
from app.api.schemas import ResumeUploadResponse, ResumeResponse
from app.config import settings

router = APIRouter(prefix="/resumes", tags=["resumes"])
logger = logging.getLogger(__name__)
resume_parser = ResumeParser()
job_matcher = JobMatcher()


def owned_resume(resume_id: int, db: Session, user: User) -> Resume:
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    if resume is None:
        raise HTTPException(404, "Resume not found")
    return resume


@router.post("/upload", response_model=ResumeUploadResponse)
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    filename = Path((file.filename or "").replace("\\", "/")).name
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / f"{uuid4().hex}.pdf"
    try:
        size = 0
        with path.open("xb") as target:
            while chunk := file.file.read(64 * 1024):
                size += len(chunk)
                if size > settings.MAX_UPLOAD_SIZE:
                    raise HTTPException(413, "Resume exceeds the upload size limit")
                target.write(chunk)
        if not size or path.read_bytes()[:5] != b"%PDF-":
            raise HTTPException(400, "Upload is not a valid PDF")
        try:
            parsed = resume_parser.parse_resume(str(path))
        except Exception as exc:
            raise HTTPException(400, "Cannot read this PDF. Use an unencrypted PDF with selectable text.") from exc
        embedding = job_matcher.generate_embedding(job_matcher.prepare_resume_text(parsed))
        resume = Resume(user_id=current_user.id, filename=filename, file_path=str(path),
                        raw_text=parsed["raw_text"], skills=parsed["skills"],
                        education=parsed["education"], experience=parsed["experience"], embedding=embedding)
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return ResumeUploadResponse(id=resume.id, filename=filename,
            message="Resume uploaded and parsed successfully", skills_found=parsed["skills"],
            education_found=len(parsed["education"]), experience_found=len(parsed["experience"]))
    except Exception as exc:
        db.rollback()
        path.unlink(missing_ok=True)
        if isinstance(exc, HTTPException):
            raise
        logger.exception("Resume processing failed")
        raise HTTPException(503, "Resume processing is temporarily unavailable. Please try again.") from exc
    finally:
        file.file.close()


@router.get("/", response_model=list[ResumeResponse])
def list_resumes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return owned_resume(resume_id, db, current_user)


@router.delete("/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resume = owned_resume(resume_id, db, current_user)
    path = Path(resume.file_path)
    db.query(JobApplication).filter(JobApplication.resume_id == resume.id).update({"resume_id": None})
    db.delete(resume)
    db.commit()
    path.unlink(missing_ok=True)
    return {"message": "Resume deleted successfully"}
