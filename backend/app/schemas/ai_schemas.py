"""
Pydantic schemas for AI-structured resume data.
These are used as the structured output format for LLM calls
and as the data model for Jinja2 LaTeX template rendering.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class PersonalInfo(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None


class WorkExperience(BaseModel):
    company: str
    title: str
    start_date: str
    end_date: str
    location: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)


class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: str
    end_date: str
    gpa: Optional[str] = None
    details: Optional[str] = None


class SkillsSection(BaseModel):
    technical: List[str] = Field(default_factory=list)
    soft: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)


class Project(BaseModel):
    name: str
    description: str
    technologies: List[str] = Field(default_factory=list)
    bullets: List[str] = Field(default_factory=list)
    url: Optional[str] = None


class ResumeProfile(BaseModel):
    """Complete structured resume data extracted from a master resume."""
    personal_info: PersonalInfo
    summary: str = ""
    work_experience: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: SkillsSection = Field(default_factory=SkillsSection)
    projects: List[Project] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)


class JDProfile(BaseModel):
    """Structured data extracted from a job description."""
    job_title: str
    company_name: Optional[str] = None
    seniority_level: str = "mid"
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    key_responsibilities: List[str] = Field(default_factory=list)
    industry_keywords: List[str] = Field(default_factory=list)


class TailoredResumeData(ResumeProfile):
    """
    Same structure as ResumeProfile but with content tailored
    to the target job description. Inherits all fields.
    """
    pass
