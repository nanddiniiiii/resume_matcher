from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, nullable=False)  # List of required skills
    location = Column(String, nullable=True)
    job_type = Column(String, nullable=True)  # internship, full-time, part-time, remote, hybrid

    # Embedding for semantic search
    embedding = Column(JSON, nullable=True)  # Stored as list

    # Scraping metadata
    source = Column(String, nullable=True)  # remoteok, adzuna, manual, indeed
    source_url = Column(String, nullable=True)  # Original job posting URL
    source_job_id = Column(String, nullable=True)  # External job ID for deduplication
    scraped_at = Column(DateTime(timezone=True), nullable=True)  # When job was scraped
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Job expiration date
    is_active = Column(Boolean, default=True)  # Whether job is still active

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
