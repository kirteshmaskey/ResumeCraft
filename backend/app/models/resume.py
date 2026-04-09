from sqlalchemy import Column, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class MasterResume(Base):
    __tablename__ = "master_resumes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    content = Column(JSON, nullable=False)  # Structured resume data
    raw_text = Column(Text) # Original text if uploaded as PDF/DOCX
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class GeneratedResume(Base):
    __tablename__ = "generated_resumes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    master_resume_id = Column(String, ForeignKey("master_resumes.id"), nullable=False)
    job_description = Column(Text, nullable=False)
    optimized_content = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
