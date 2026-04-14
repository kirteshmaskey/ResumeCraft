"""
AI service for resume parsing and tailoring.

Uses LangChain + OpenAI for structured output when an API key is available.
Falls back to a deterministic pass-through mode for development.
"""

import re
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

    Supports multiple providers (OpenAI, Azure OpenAI).
    When no API key is set for the chosen provider, uses a rule-based
    fallback so the full pipeline is testable without an API key.
    """

    def __init__(self, settings: dict):
        self._settings = settings
        self._provider = settings.get("AI_PROVIDER", "openai").lower()
        self._llm = None
        self._resume_extractor = None
        self._jd_extractor = None
        self._tailor_extractor = None

        self._init_llm()

    # ── LLM Initialization ──────────────────────────────────────────────

    def _init_llm(self) -> None:
        """Initialize LangChain LLM using unified standards."""
        api_key = self._settings.get("AI_API_KEY")
        if not api_key:
            logger.warning("AI_API_KEY is not set. AI service will use fallback mode.")
            return

        try:
            if self._provider == "azure":
                self._init_azure_llm()
            else:
                self._init_standard_llm()

            if self._llm:
                self._resume_extractor = self._llm.with_structured_output(
                    ResumeProfile, method="json_schema", strict=True
                )
                self._jd_extractor = self._llm.with_structured_output(
                    JDProfile, method="json_schema", strict=True
                )
                self._tailor_extractor = self._llm.with_structured_output(
                    TailoredResumeData, method="json_schema", strict=True
                )
                logger.info("AI service initialized with provider: %s", self._provider)
        except Exception as e:
            logger.error("Failed to initialize AI service: %s", str(e))
            self._llm = None

    def _create_http_client(self):
        """Create an httpx client without proxies to avoid version conflicts."""
        import httpx
        return httpx.Client(timeout=httpx.Timeout(60.0))

    def _create_async_http_client(self):
        """Create an async httpx client without proxies."""
        import httpx
        return httpx.AsyncClient(timeout=httpx.Timeout(60.0))

    def _init_standard_llm(self) -> None:
        """Initialize any OpenAI-compatible provider."""
        from langchain_openai import ChatOpenAI

        self._llm = ChatOpenAI(
            model=self._settings.get("AI_MODEL") or "gpt-4o-mini",
            temperature=0,
            api_key=self._settings.get("AI_API_KEY"),
            base_url=self._settings.get("AI_ENDPOINT") or None,
            http_client=self._create_http_client(),
            http_async_client=self._create_async_http_client(),
        )

    def _init_azure_llm(self) -> None:
        """Initialize Azure OpenAI provider."""
        from langchain_openai import AzureChatOpenAI

        # Ensure endpoint is just the base URL: https://resource.openai.azure.com/
        endpoint = self._settings.get("AI_ENDPOINT", "").strip()
        if "/openai" in endpoint:
            endpoint = endpoint.split("/openai")[0]
        endpoint = endpoint.rstrip("/")

        self._llm = AzureChatOpenAI(
            azure_deployment=self._settings.get("AI_MODEL"),
            api_version=self._settings.get("AI_API_VERSION") or "2024-02-01",
            azure_endpoint=endpoint,
            api_key=self._settings.get("AI_API_KEY"),
            temperature=0,
            http_client=self._create_http_client(),
            http_async_client=self._create_async_http_client(),
        )

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
            result = await self._resume_extractor.ainvoke(prompt)
            return self._sanitize_resume_profile(result)

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
                "Make bullet points more impactful using action verbs and metrics. "
                "IMPORTANT: Do NOT use any LaTeX commands, special formatting, "
                "or backslash commands in your output. Return plain text only. "
                "Do not use characters like &, %, $, #, _, {, }, ~, ^ — "
                "write them out in words if needed.\n\n"
                f"RESUME_PROFILE_JSON:\n{profile.model_dump_json()}\n\n"
                f"JD_PROFILE_JSON:\n{jd.model_dump_json()}"
            )
            result = await self._tailor_extractor.ainvoke(prompt)
            return self._sanitize_tailored_data(result)

        logger.info("Using fallback resume tailor (no AI key)")
        return self._fallback_tailor(profile, jd)

    # ── AI Output Sanitization ──────────────────────────────────────────

    @staticmethod
    def _sanitize_text(text: str) -> str:
        """
        Remove any LaTeX commands or problematic markup the AI may have
        injected into plain text fields. This is a safety net — the
        `latex_escape` filter in the template handles proper escaping,
        but we don't want raw \\textbf{} etc. inside data values.
        """
        if not text:
            return text

        # Remove common LaTeX commands that AI might generate
        # e.g. \textbf{...}, \textit{...}, \emph{...}, \underline{...}
        text = re.sub(r'\\(?:textbf|textit|emph|underline|textsc)\{([^}]*)\}', r'\1', text)

        # Remove \href{url}{text} → keep just text
        text = re.sub(r'\\href\{[^}]*\}\{([^}]*)\}', r'\1', text)

        # Remove standalone LaTeX commands like \\ \newline \par
        text = re.sub(r'\\(?:newline|par|noindent|vspace\{[^}]*\}|hspace\{[^}]*\})(\s|$)', r'\1', text)

        # Remove double backslashes (LaTeX line breaks) that AI might add
        text = text.replace('\\\\', ' ')

        # Normalize smart quotes and dashes to ASCII
        text = text.replace('\u2018', "'").replace('\u2019', "'")   # smart single quotes
        text = text.replace('\u201c', '"').replace('\u201d', '"')   # smart double quotes
        text = text.replace('\u2013', '-').replace('\u2014', '-')   # en-dash, em-dash
        text = text.replace('\u2026', '...')                        # ellipsis

        return text.strip()

    @classmethod
    def _sanitize_string_list(cls, items: list[str]) -> list[str]:
        """Sanitize each string in a list."""
        return [cls._sanitize_text(item) for item in items if item]

    @classmethod
    def _sanitize_resume_profile(cls, profile: ResumeProfile) -> ResumeProfile:
        """Sanitize all text fields in a ResumeProfile."""
        profile.personal_info.name = cls._sanitize_text(profile.personal_info.name)
        profile.summary = cls._sanitize_text(profile.summary)

        for exp in profile.work_experience:
            exp.title = cls._sanitize_text(exp.title)
            exp.company = cls._sanitize_text(exp.company)
            exp.bullets = cls._sanitize_string_list(exp.bullets)

        for edu in profile.education:
            edu.institution = cls._sanitize_text(edu.institution)
            edu.degree = cls._sanitize_text(edu.degree)
            if edu.field_of_study:
                edu.field_of_study = cls._sanitize_text(edu.field_of_study)
            if edu.details:
                edu.details = cls._sanitize_text(edu.details)

        profile.skills.technical = cls._sanitize_string_list(profile.skills.technical)
        profile.skills.soft = cls._sanitize_string_list(profile.skills.soft)
        profile.skills.tools = cls._sanitize_string_list(profile.skills.tools)
        profile.skills.languages = cls._sanitize_string_list(profile.skills.languages)

        for proj in profile.projects:
            proj.name = cls._sanitize_text(proj.name)
            proj.description = cls._sanitize_text(proj.description)
            proj.bullets = cls._sanitize_string_list(proj.bullets)
            proj.technologies = cls._sanitize_string_list(proj.technologies)

        profile.certifications = cls._sanitize_string_list(profile.certifications)
        profile.achievements = cls._sanitize_string_list(profile.achievements)

        return profile

    @classmethod
    def _sanitize_tailored_data(cls, data: TailoredResumeData) -> TailoredResumeData:
        """Sanitize all text fields in TailoredResumeData."""
        # TailoredResumeData inherits from ResumeProfile
        return cls._sanitize_resume_profile(data)

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
        # Collect exactly the unified variables
        config = {
            "AI_PROVIDER": settings.AI_PROVIDER,
            "AI_API_KEY": settings.AI_API_KEY,
            "AI_MODEL": settings.AI_MODEL,
            "AI_ENDPOINT": settings.AI_ENDPOINT,
            "AI_API_VERSION": settings.AI_API_VERSION,
        }
        _ai_service = AIService(settings=config)
    return _ai_service
