from pydantic import Field
from typing import List, Optional
from uuid import UUID

from app.schemas.base import BaseSchema


class ProjectStageResponse(BaseSchema):
    """Схема этапа проекта для ответа"""
    id: UUID
    name: str
    status: str  # "pending" | "in_progress" | "completed"


class ProjectResponse(BaseSchema):
    """Схема проекта для ответа"""
    id: UUID
    name: str
    address: str
    description: Optional[str] = None
    area: float
    floors: int
    price: float
    imageUrl: Optional[str] = Field(None, alias="image_url")
    stages: List[ProjectStageResponse] = []

