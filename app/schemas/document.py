from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseSchema


class DocumentResponse(BaseSchema):
    """Схема документа для ответа"""
    id: UUID
    projectId: UUID = Field(..., alias="project_id")
    title: str
    description: str = ""  # Мобильное приложение ожидает обязательное поле
    fileUrl: Optional[str] = Field(None, alias="file_url")
    status: str  # "pending" | "under_review" | "approved" | "rejected"
    submittedAt: Optional[datetime] = Field(None, alias="submitted_at")
    approvedAt: Optional[datetime] = Field(None, alias="approved_at")
    rejectionReason: Optional[str] = Field(None, alias="rejection_reason")
    
    @field_validator('description', mode='before')
    @classmethod
    def convert_description(cls, v: Any) -> str:
        """Конвертирует None в пустую строку для description"""
        if v is None:
            return ""
        return str(v)


class DocumentRejectRequest(BaseModel):
    """Схема запроса на отклонение документа"""
    reason: str = Field(..., min_length=1)

