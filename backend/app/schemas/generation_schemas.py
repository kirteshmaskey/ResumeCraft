"""
Pydantic schemas for resume generation and LaTeX compilation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── Request Schemas ──────────────────────────────────────────────────────

class GenerateResumeRequest(BaseModel):
    """Request to generate a tailored resume."""
    master_resume_text: str = Field(..., min_length=10, description="Full text of the master resume")
    job_description: str = Field(..., min_length=10, description="Target job description text")
    template_id: str = Field(..., description="ID of the LaTeX template to use")


class CompileLatexRequest(BaseModel):
    """Request to compile raw LaTeX code into a PDF."""
    latex_code: str = Field(..., min_length=1, description="LaTeX source code to compile")
    is_template: bool = Field(default=False, description="Whether to compile as a template with dummy data")


# ── Response Schemas ─────────────────────────────────────────────────────

class GenerateResumeResponse(BaseModel):
    """Response after resume generation."""
    id: str
    latex_source: str
    status: str = "completed"
    created_at: datetime

    model_config = {"from_attributes": True}


class CompileLatexResponse(BaseModel):
    """Response after LaTeX compilation — returns metadata; PDF is streamed separately."""
    success: bool
    message: str
    errors: Optional[List[str]] = None
