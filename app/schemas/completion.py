from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseSchema


class FinalDocumentResponse(BaseSchema):
    """Схема финального документа для ответа"""
    id: UUID
    title: str
    description: str = ""  # Мобильное приложение ожидает обязательное поле
    fileUrl: Optional[str] = Field(None, alias="file_url")
    status: str  # "pending" | "signed" | "rejected"
    submittedAt: Optional[datetime] = Field(None, alias="submitted_at")
    signedAt: Optional[datetime] = Field(None, alias="signed_at")
    signatureUrl: Optional[str] = Field(None, alias="signature_url")
    
    @field_validator('description', mode='before')
    @classmethod
    def convert_description(cls, v: Any) -> str:
        """Конвертирует None в пустую строку для description"""
        if v is None:
            return ""
        return str(v)


class CompletionStatusResponse(BaseSchema):
    """Схема статуса завершения строительства"""
    projectId: UUID = Field(..., alias="project_id")
    isCompleted: bool = Field(..., alias="is_completed")
    completionDate: Optional[datetime] = Field(None, alias="completion_date")
    progress: float = Field(..., ge=0.0, le=1.0)
    allDocumentsSigned: bool = Field(False, alias="all_documents_signed")
    documents: List[FinalDocumentResponse] = []


class FinalDocumentRejectRequest(BaseModel):
    """Схема запроса на отклонение финального документа"""
    reason: str = Field(..., min_length=1)

