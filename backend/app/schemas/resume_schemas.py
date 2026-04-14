from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class MasterResumeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class MasterResumeCreate(MasterResumeBase):
    text_content: Optional[str] = None
    # PDF is handled via multipart upload

class MasterResumeUpdate(MasterResumeBase):
    pass

class MasterResumeRead(MasterResumeBase):
    id: str
    user_id: str
    content: dict
    raw_text: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
