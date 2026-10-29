from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import List, Optional, Dict
from datetime import datetime


# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def password_bytes(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 UTF-8 bytes")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict


# Resume schemas
class ResumeUploadResponse(BaseModel):
    id: int
    filename: str
    message: str
    skills_found: List[str]
    education_found: int
    experience_found: int


class ResumeResponse(BaseModel):
    id: int
    filename: str
    skills: Optional[List[str]]
    education: Optional[List[Dict]]
    experience: Optional[List[Dict]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Job schemas
class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    company: Optional[str] = None
    description: str = Field(min_length=1)
    required_skills: List[str]
    location: Optional[str] = None
    job_type: Optional[str] = None  # internship, full-time, part-time


class JobResponse(BaseModel):
    id: int
    title: str
    company: Optional[str]
    description: str
    required_skills: List[str]
    location: Optional[str]
    job_type: Optional[str]
    source: Optional[str] = None
    source_url: Optional[str] = None
    scraped_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Job Match schemas
class JobMatchExplanation(BaseModel):
    match_quality: str
    overall_score: float
    skill_match_percentage: float
    recommendation: str
    skill_analysis: str
    strengths: List[str]
    areas_to_improve: List[str]
    why_this_matches: str


class JobMatchResponse(BaseModel):
    job: JobResponse
    similarity_score: float
    matching_skills: List[str]
    missing_skills: List[str]
    explanation: JobMatchExplanation


class JobMatchListResponse(BaseModel):
    total_matches: int
    matches: List[JobMatchResponse]
