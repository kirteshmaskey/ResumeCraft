"""
AI service for resume parsing and tailoring.

Uses LangChain + OpenAI for structured output when an API key is available.
Falls back to a deterministic pass-through mode for development.
"""

from typing import Optional

from app.schemas.ai_schemas import (
    ResumeProfile,
    JDProfile,
    TailoredResumeData,
    PersonalInfo,
    WorkExperience,
    Education,
    SkillsSection,
    Project,
)
from app.core.logging import get_logger

logger = get_logger("ai_service")


class AIService:
    """
    Orchestrates AI-powered resume parsing and tailoring.

    When OPENAI_API_KEY is set, uses LangChain ChatOpenAI with
    structured output. Otherwise, uses a rule-based fallback
    so the full pipeline is testable without an API key.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self._api_key = api_key
        self._model = model
        self._llm = None
        self._resume_extractor = None
        self._jd_extractor = None
        self._tailor_extractor = None

        if api_key:
            self._init_llm()

    # ── LLM Initialization ──────────────────────────────────────────────

    def _init_llm(self) -> None:
        """Lazy-initialize LangChain LLM and structured extractors."""
        try:
            from langchain_openai import ChatOpenAI

            self._llm = ChatOpenAI(
                model=self._model,
                temperature=0,
                api_key=self._api_key,
            )
            self._resume_extractor = self._llm.with_structured_output(
                ResumeProfile, method="json_schema", strict=True
            )
            self._jd_extractor = self._llm.with_structured_output(
                JDProfile, method="json_schema", strict=True
            )
            self._tailor_extractor = self._llm.with_structured_output(
                TailoredResumeData, method="json_schema", strict=True
            )
            logger.info("AI service initialized with model: %s", self._model)
        except ImportError:
            logger.warning(
                "langchain-openai not installed. AI service will use fallback mode."
            )
            self._llm = None

    @property
    def is_ai_available(self) -> bool:
        """Check if the AI backend is properly configured."""
        return self._llm is not None

    # ── Public API ──────────────────────────────────────────────────────

    async def parse_master_resume(self, resume_text: str) -> ResumeProfile:
        """
        Parse raw resume text into a structured ResumeProfile.
        Uses AI if available, otherwise returns a stub profile.
        """
        if self.is_ai_available:
            prompt = (
                "Extract a structured resume profile from the resume text below. "
                "Do NOT invent information. Only extract what is present.\n\n"
                f"RESUME:\n{resume_text}"
            )
            return await self._resume_extractor.ainvoke(prompt)

        logger.info("Using fallback resume parser (no AI key)")
        return self._fallback_parse_resume(resume_text)

    async def analyze_jd(self, jd_text: str) -> JDProfile:
        """
        Extract structured data from a job description.
        """
        if self.is_ai_available:
            prompt = (
                "Extract job requirements, skills, and keywords from "
                "this job description.\n\n"
                f"JOB DESCRIPTION:\n{jd_text}"
            )
            return await self._jd_extractor.ainvoke(prompt)

        logger.info("Using fallback JD analyzer (no AI key)")
        return self._fallback_analyze_jd(jd_text)

    async def tailor_resume(
        self,
        profile: ResumeProfile,
        jd: JDProfile,
    ) -> TailoredResumeData:
        """
        Tailor a resume profile to match a job description.
        Only rephrases and reorders — never invents experience.
        """
        if self.is_ai_available:
            prompt = (
                "Rephrase and reorder the resume content to better match the job. "
                "Do NOT invent experience. Use only the provided content. "
                "Prioritize relevant skills and experience. "
                "Make bullet points more impactful using action verbs and metrics.\n\n"
                f"RESUME_PROFILE_JSON:\n{profile.model_dump_json()}\n\n"
                f"JD_PROFILE_JSON:\n{jd.model_dump_json()}"
            )
            return await self._tailor_extractor.ainvoke(prompt)

        logger.info("Using fallback resume tailor (no AI key)")
        return self._fallback_tailor(profile, jd)

    # ── Fallback Implementations ────────────────────────────────────────

    @staticmethod
    def _fallback_parse_resume(text: str) -> ResumeProfile:
        """Simple rule-based resume parsing for development."""
        lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
        name = lines[0] if lines else "Unknown"
        email = ""
        for line in lines:
            if "@" in line and "." in line:
                email = line
                break

        return ResumeProfile(
            personal_info=PersonalInfo(name=name, email=email),
            summary=" ".join(lines[1:3]) if len(lines) > 1 else "",
            work_experience=[],
            education=[],
            skills=SkillsSection(),
            projects=[],
        )

    @staticmethod
    def _fallback_analyze_jd(text: str) -> JDProfile:
        """Simple keyword extraction for development."""
        words = text.lower().split()
        # Extract potential skill keywords (longer words likely more meaningful)
        keywords = list({w.strip(".,;:()") for w in words if len(w) > 4})[:20]
        return JDProfile(
            job_title="Position",
            required_skills=keywords[:10],
            preferred_skills=keywords[10:],
            key_responsibilities=[],
            industry_keywords=keywords[:5],
        )

    @staticmethod
    def _fallback_tailor(profile: ResumeProfile, jd: JDProfile) -> TailoredResumeData:
        """Pass-through tailoring — returns profile data unchanged."""
        return TailoredResumeData(**profile.model_dump())


# ── Singleton factory ───────────────────────────────────────────────────

_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get or create the singleton AIService instance."""
    global _ai_service
    if _ai_service is None:
        from app.core.config import get_settings
        settings = get_settings()
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        _ai_service = AIService(api_key=api_key or None)
    return _ai_service
