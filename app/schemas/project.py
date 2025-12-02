from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class ProjectStageResponse(BaseModel):
    """Схема этапа проекта для ответа"""
    id: UUID
    name: str
    status: str  # "pending" | "in_progress" | "completed"

    class Config:
        from_attributes = True


class ProjectResponse(BaseModel):
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

    class Config:
        from_attributes = True
        populate_by_name = True


# Для списка проектов используем List[ProjectResponse] напрямую в эндпоинтах


class EmptyResponse(BaseModel):
    """Пустой ответ для POST запросов"""
    pass

