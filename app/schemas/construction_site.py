from pydantic import Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseSchema


class CameraResponse(BaseSchema):
    """Схема камеры для ответа"""
    id: UUID
    name: str
    description: Optional[str] = None
    streamUrl: str = Field(..., alias="stream_url")
    isActive: bool = Field(..., alias="is_active")
    thumbnailUrl: Optional[str] = Field(None, alias="thumbnail_url")


class ConstructionSiteResponse(BaseSchema):
    """Схема строительной площадки для ответа"""
    id: UUID
    projectId: UUID = Field(..., alias="project_id")
    projectName: str = Field(..., alias="project_name")
    address: str
    cameras: List[CameraResponse] = []
    startDate: Optional[datetime] = Field(None, alias="start_date")
    expectedCompletionDate: Optional[datetime] = Field(None, alias="expected_completion_date")
    progress: float = Field(..., ge=0.0, le=1.0)

