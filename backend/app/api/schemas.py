from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from datetime import datetime


# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


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
    
    class Config:
        from_attributes = True


# Job schemas
class JobCreate(BaseModel):
    title: str
    company: Optional[str] = None
    description: str
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
    created_at: datetime
    
    class Config:
        from_attributes = True


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
