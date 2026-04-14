from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.resume import MasterResume
from app.schemas.resume_schemas import MasterResumeRead
from app.services.pdf_service import extract_text_from_pdf
from app.services.ai_service import get_ai_service
from app.core.logging import get_logger
import uuid

logger = get_logger("api.resumes")
router = APIRouter()

@router.get("/", response_model=List[MasterResumeRead])
async def list_resumes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all master resumes for the current user."""
    query = select(MasterResume).where(MasterResume.user_id == current_user.id).order_by(MasterResume.updated_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=MasterResumeRead)
async def create_resume(
    name: str = Form(...),
    text_content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new master resume.
    Supports either direct text content or a PDF file upload.
    """
    raw_text = ""
    
    if file:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        content = await file.read()
        try:
            raw_text = extract_text_from_pdf(content)
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))
    elif text_content:
        raw_text = text_content
    else:
        raise HTTPException(status_code=400, detail="Either text_content or file must be provided")

    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="Extracted or provided text is empty")

    ai = get_ai_service()
    try:
        # Structured parsing via LLM
        logger.info("Parsing master resume with LLM")
        structured_profile = await ai.parse_master_resume(raw_text)
        
        new_resume = MasterResume(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            name=name,
            content=structured_profile.model_dump(),
            raw_text=raw_text
        )
        
        db.add(new_resume)
        await db.commit()
        await db.refresh(new_resume)
        
        return new_resume
    except Exception as e:
        logger.error(f"Failed to create master resume: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a master resume."""
    resume = await db.get(MasterResume, resume_id)
    if not resume or resume.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    await db.delete(resume)
    await db.commit()
    return {"status": "success"}
