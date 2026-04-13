"""
Resume generation & LaTeX compilation API.

Endpoints:
- POST /generate  — AI-tailored resume from master resume + JD + template
- POST /compile   — Compile raw LaTeX code → PDF download
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.core.logging import get_logger
from app.models.template import ResumeTemplate
from app.schemas.generation_schemas import (
    GenerateResumeRequest,
    GenerateResumeResponse,
    CompileLatexRequest,
    CompileLatexResponse,
)
from app.services.ai_service import get_ai_service
from app.services.latex_service import (
    compile_latex_to_pdf,
    render_template,
    get_dummy_resume_data,
)

logger = get_logger("api.generation")
router = APIRouter()


# ── Generate Tailored Resume ────────────────────────────────────────────

@router.post("/generate", response_model=GenerateResumeResponse)
async def generate_resume(
    payload: GenerateResumeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate a tailored resume.

    1. Fetch the selected LaTeX template
    2. Parse the master resume into structured data
    3. Analyze the job description
    4. Tailor the resume data to the JD
    5. Render the Jinja2 LaTeX template with tailored data
    6. Return the rendered LaTeX source
    """
    # 1. Fetch template
    template = await db.get(ResumeTemplate, payload.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    ai = get_ai_service()

    try:
        # 2. Parse master resume
        logger.info("Parsing master resume (%d chars)", len(payload.master_resume_text))
        resume_profile = await ai.parse_master_resume(payload.master_resume_text)

        # 3. Analyze JD
        logger.info("Analyzing JD (%d chars)", len(payload.job_description))
        jd_profile = await ai.analyze_jd(payload.job_description)

        # 4. Tailor
        logger.info("Tailoring resume for: %s", jd_profile.job_title)
        tailored = await ai.tailor_resume(resume_profile, jd_profile)

        # 5. Render LaTeX
        rendered_latex = render_template(
            template.latex_code,
            tailored.model_dump(),
        )

        result_id = str(uuid.uuid4())
        logger.info("Resume generated successfully (id=%s)", result_id)

        return GenerateResumeResponse(
            id=result_id,
            latex_source=rendered_latex,
            status="completed",
            created_at=datetime.now(timezone.utc),
        )

    except Exception as e:
        logger.error("Resume generation failed: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Resume generation failed: {str(e)}",
        )


# ── Compile Raw LaTeX → PDF ─────────────────────────────────────────────

@router.post("/compile")
async def compile_latex(
    payload: CompileLatexRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Compile raw LaTeX source into a PDF and return it as a downloadable file.
    """
    try:
        latex_code_to_compile = payload.latex_code
        if payload.is_template:
            dummy_data = get_dummy_resume_data()
            latex_code_to_compile = render_template(latex_code_to_compile, dummy_data)
        
        pdf_bytes, warnings = compile_latex_to_pdf(latex_code_to_compile)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=resume.pdf",
                "X-Latex-Warnings": str(len(warnings)),
            },
        )

    except RuntimeError as e:
        logger.error("LaTeX compilation failed: %s", str(e))
        raise HTTPException(
            status_code=422,
            detail={
                "message": "LaTeX compilation failed",
                "errors": str(e).splitlines(),
            },
        )
    except Exception as e:
        logger.error("Unexpected error during compilation: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal server error during LaTeX compilation",
        )
