from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseSchema


class DocumentResponse(BaseSchema):
    """Схема документа для ответа"""
    id: UUID
    projectId: UUID = Field(..., alias="project_id")
    title: str
    description: Optional[str] = None
    fileUrl: Optional[str] = Field(None, alias="file_url")
    status: str  # "pending" | "under_review" | "approved" | "rejected"
    submittedAt: Optional[datetime] = Field(None, alias="submitted_at")
    approvedAt: Optional[datetime] = Field(None, alias="approved_at")
    rejectionReason: Optional[str] = Field(None, alias="rejection_reason")


class DocumentRejectRequest(BaseModel):
    """Схема запроса на отклонение документа"""
    reason: str = Field(..., min_length=1)

