"""
Template management API — CRUD for LaTeX resume templates.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sa_func
from typing import Optional

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.core.logging import get_logger
from app.models.template import ResumeTemplate
from app.schemas.template_schemas import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateListItem,
)

logger = get_logger("api.templates")
router = APIRouter()


# ── List Templates ───────────────────────────────────────────────────────

@router.get("", response_model=list[TemplateListItem])
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    active_only: bool = Query(True, description="Return only active templates"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all resume templates, optionally filtered."""
    stmt = select(ResumeTemplate)

    if active_only:
        stmt = stmt.where(ResumeTemplate.is_active == True)  # noqa: E712
    if category:
        stmt = stmt.where(ResumeTemplate.category == category)

    stmt = stmt.order_by(ResumeTemplate.created_at.desc())
    result = await db.execute(stmt)
    templates = result.scalars().all()
    return templates


# ── Get Single Template ──────────────────────────────────────────────────

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single template by ID (includes full latex_code)."""
    template = await db.get(ResumeTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


# ── Create Template ──────────────────────────────────────────────────────

@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    payload: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new resume template."""
    # Check for duplicate name
    existing = await db.execute(
        select(ResumeTemplate).where(ResumeTemplate.name == payload.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Template with name '{payload.name}' already exists",
        )

    template = ResumeTemplate(
        name=payload.name,
        description=payload.description,
        latex_code=payload.latex_code,
        category=payload.category,
    )
    db.add(template)
    await db.flush()
    await db.refresh(template)
    logger.info("Created template: %s (id=%s)", template.name, template.id)
    return template


# ── Update Template ──────────────────────────────────────────────────────

@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    payload: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing template — partial updates supported."""
    template = await db.get(ResumeTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    await db.flush()
    await db.refresh(template)
    logger.info("Updated template: %s", template_id)
    return template


# ── Delete Template ──────────────────────────────────────────────────────

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft-delete a template (sets is_active=False)."""
    template = await db.get(ResumeTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    template.is_active = False
    await db.flush()
    logger.info("Soft-deleted template: %s", template_id)
