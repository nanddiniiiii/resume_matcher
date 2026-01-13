from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    
    # Parsed content
    raw_text = Column(Text, nullable=True)
    skills = Column(JSON, nullable=True)  # List of skills
    education = Column(JSON, nullable=True)  # Education details
    experience = Column(JSON, nullable=True)  # Work experience
    
    # Embedding for semantic search
    embedding = Column(JSON, nullable=True)  # Stored as list
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    matches = relationship("JobMatch", back_populates="resume", cascade="all, delete-orphan")
