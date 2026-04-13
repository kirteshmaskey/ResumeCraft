"""
ResumeTemplate model — stores LaTeX resume templates.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class ResumeTemplate(Base):
    __tablename__ = "resume_templates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    latex_code = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, default="general")
    preview_image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<ResumeTemplate(id={self.id!r}, name={self.name!r})>"
