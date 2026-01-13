from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class JobMatch(Base):
    __tablename__ = "job_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    # Match details
    similarity_score = Column(Float, nullable=False)  # 0 to 1
    matching_skills = Column(JSON, nullable=True)  # Skills that match
    missing_skills = Column(JSON, nullable=True)  # Skills that are required but missing
    explanation = Column(JSON, nullable=True)  # Detailed explanation
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    resume = relationship("Resume", back_populates="matches")
    job = relationship("Job", back_populates="matches")
