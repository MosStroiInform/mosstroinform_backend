from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseSchema


class FinalDocumentResponse(BaseSchema):
    """Схема финального документа для ответа"""
    id: UUID
    title: str
    description: Optional[str] = None
    fileUrl: Optional[str] = Field(None, alias="file_url")
    status: str  # "pending" | "signed" | "rejected"
    submittedAt: Optional[datetime] = Field(None, alias="submitted_at")
    signedAt: Optional[datetime] = Field(None, alias="signed_at")
    signatureUrl: Optional[str] = Field(None, alias="signature_url")


class CompletionStatusResponse(BaseSchema):
    """Схема статуса завершения строительства"""
    projectId: UUID = Field(..., alias="project_id")
    isCompleted: bool = Field(..., alias="is_completed")
    completionDate: Optional[datetime] = Field(None, alias="completion_date")
    progress: float = Field(..., ge=0.0, le=1.0)
    documents: List[FinalDocumentResponse] = []


class FinalDocumentRejectRequest(BaseModel):
    """Схема запроса на отклонение финального документа"""
    reason: str = Field(..., min_length=1)

