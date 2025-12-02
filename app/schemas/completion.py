from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class FinalDocumentResponse(BaseModel):
    """Схема финального документа для ответа"""
    id: UUID
    title: str
    description: Optional[str] = None
    fileUrl: Optional[str] = Field(None, alias="file_url")
    status: str  # "pending" | "signed" | "rejected"
    submittedAt: Optional[datetime] = Field(None, alias="submitted_at")
    signedAt: Optional[datetime] = Field(None, alias="signed_at")
    signatureUrl: Optional[str] = Field(None, alias="signature_url")

    class Config:
        from_attributes = True
        populate_by_name = True


class CompletionStatusResponse(BaseModel):
    """Схема статуса завершения строительства"""
    projectId: UUID = Field(..., alias="project_id")
    isCompleted: bool = Field(..., alias="is_completed")
    completionDate: Optional[datetime] = Field(None, alias="completion_date")
    progress: float = Field(..., ge=0.0, le=1.0)
    documents: List[FinalDocumentResponse] = []

    class Config:
        from_attributes = True
        populate_by_name = True


# Для списка финальных документов используем List[FinalDocumentResponse] напрямую в эндпоинтах


class FinalDocumentRejectRequest(BaseModel):
    """Схема запроса на отклонение финального документа"""
    reason: str = Field(..., min_length=1)

