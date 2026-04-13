"""
Pydantic schemas for resume template CRUD operations.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Request Schemas ──────────────────────────────────────────────────────

class TemplateCreate(BaseModel):
    """Schema for creating a new resume template."""
    name: str = Field(..., min_length=1, max_length=255, description="Template display name")
    description: Optional[str] = Field(None, description="Short description of the template")
    latex_code: str = Field(..., min_length=1, description="Full LaTeX source code (Jinja2 template)")
    category: str = Field("general", max_length=100, description="Category: general, tech, academic, creative")


class TemplateUpdate(BaseModel):
    """Schema for updating an existing template — all fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    latex_code: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


# ── Response Schemas ─────────────────────────────────────────────────────

class TemplateResponse(BaseModel):
    """Single template response."""
    id: str
    name: str
    description: Optional[str] = None
    latex_code: str
    category: str
    preview_image_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TemplateListItem(BaseModel):
    """Lightweight template item for listing (no latex_code)."""
    id: str
    name: str
    description: Optional[str] = None
    category: str
    preview_image_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
